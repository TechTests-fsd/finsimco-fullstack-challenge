import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AppState, SimulationField, FieldToggleStatus } from '../types/simulation';
import { calculateValuation } from '../utils/calculations';

interface SimulationStore extends AppState {
  updateSimulationField: (field: SimulationField, value: string | number) => void;
  updateFieldStatus: (field: SimulationField, status: FieldToggleStatus) => void;
  
  incrementTimer: () => void;
  resetTimer: () => void;
  
  toggleFirstTimeGuidance: () => void;
  openVideoModal: () => void;
  closeVideoModal: () => void;
  openTextModal: () => void;
  closeTextModal: () => void;
  
  setUserRole: (role: 'team1' | 'team2') => void;
  setUserName: (name: string) => void;
  
  resetSimulation: () => void;
}

const initialSimulationData = {
  ebitda: 10,
  interestRate: 20,
  multiple: 10,
  factorScore: 3,
  companyName: 'ABC Corp.',
  description: 'This is the company\'s description. This company is #1!'
};

const initialFieldStatus = Object.keys(initialSimulationData).reduce((acc, key) => {
  acc[key as SimulationField] = key === 'description' ? 'TBD' : 'OK';
  return acc;
}, {} as { [K in SimulationField]: FieldToggleStatus });

const useSimulationStore = create<SimulationStore>()(
  persist(
    (set, get) => ({
      simulation: initialSimulationData,
      fieldStatus: initialFieldStatus,
      valuation: calculateValuation(initialSimulationData),
      timer: {
        hours: 0,
        minutes: 0,
        seconds: 0,
        totalSeconds: 0
      },
      user: {
        name: 'John Doe',
        role: 'team1'
      },
      isFirstTimeGuidanceOpen: true,
      isVideoModalOpen: false,
      isTextModalOpen: false,

      updateSimulationField: (field, value) => {
        set((state) => {
          const isNumericField = typeof state.simulation[field] === 'number';
          
          const processedValue = isNumericField 
            ? (parseFloat(String(value)) || state.simulation[field] || 0) 
            : value;

          const newSimulation = {
            ...state.simulation,
            [field]: processedValue
          };
          
          return {
            simulation: newSimulation,
            valuation: calculateValuation(newSimulation)
          };
        });
      },

      updateFieldStatus: (field, status) => {
        set((state) => ({
          fieldStatus: {
            ...state.fieldStatus,
            [field]: status
          }
        }));
      },

      incrementTimer: () => {
        set((state) => {
          const newTotalSeconds = state.timer.totalSeconds + 1;
          const hours = Math.floor(newTotalSeconds / 3600);
          const minutes = Math.floor((newTotalSeconds % 3600) / 60);
          const seconds = newTotalSeconds % 60;

          return {
            timer: {
              hours,
              minutes,
              seconds,
              totalSeconds: newTotalSeconds
            }
          };
        });
      },

      resetTimer: () => {
        set({
          timer: {
            hours: 0,
            minutes: 0,
            seconds: 0,
            totalSeconds: 0
          }
        });
      },

      toggleFirstTimeGuidance: () => {
        set((state) => ({
          isFirstTimeGuidanceOpen: !state.isFirstTimeGuidanceOpen
        }));
      },

      openVideoModal: () => set({ isVideoModalOpen: true }),
      closeVideoModal: () => set({ isVideoModalOpen: false }),
      openTextModal: () => set({ isTextModalOpen: true }),
      closeTextModal: () => set({ isTextModalOpen: false }),

      setUserRole: (role) => {
        set((state) => ({
          user: {
            ...state.user,
            role
          }
        }));
      },

      setUserName: (name) => {
        set((state) => ({
          user: {
            ...state.user,
            name
          }
        }));
      },

      resetSimulation: () => {
        set({
          simulation: initialSimulationData,
          fieldStatus: initialFieldStatus,
          valuation: calculateValuation(initialSimulationData),
          timer: {
            hours: 0,
            minutes: 0,
            seconds: 0,
            totalSeconds: 0
          }
        });
      }
    }),
    {
      name: 'simulation-storage',
      partialize: (state) => ({
        isFirstTimeGuidanceOpen: state.isFirstTimeGuidanceOpen,
        user: state.user
      })
    }
  )
);

export default useSimulationStore; 
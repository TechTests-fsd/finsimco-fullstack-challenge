export interface SimulationData {
  ebitda: number;
  interestRate: number;
  multiple: number;
  factorScore: number;
  companyName: string;
  description: string;
}

export type FieldToggleStatus = 'TBD' | 'OK';
export type SimulationField = keyof SimulationData;

export type FieldStatus = {
  [K in SimulationField]: FieldToggleStatus;
};

export interface ValuationData {
  amount: number;
  percentage: number;
  maxValuation: number;
}

export interface TimerData {
  hours: number;
  minutes: number;
  seconds: number;
  totalSeconds: number;
}

export interface UserData {
  name: string;
  role: 'team1' | 'team2';
}

export interface AppState {
  simulation: SimulationData;
  fieldStatus: FieldStatus;
  valuation: ValuationData;
  timer: TimerData;
  user: UserData;
  isFirstTimeGuidanceOpen: boolean;
  isVideoModalOpen: boolean;
  isTextModalOpen: boolean;
} 
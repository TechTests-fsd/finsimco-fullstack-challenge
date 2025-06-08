import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import Team1Page from './pages/Team1Page';
import Team2Page from './pages/Team2Page';
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/team1" element={<Team1Page />} />
          <Route path="/team2" element={<Team2Page />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

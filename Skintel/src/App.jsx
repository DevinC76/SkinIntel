import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./Header";
import "./App.css";

import WeeklyRoutine from "./pages/WeeklyRoutine";
import Routine from "./pages/Routine";
import ConfidenceCalendar from "./pages/ConfidenceCalendar";

const Main = () => (
  <div className="routine-layout">
    <Routine />
    <div className="confidence-calendar-wrapper">
      <ConfidenceCalendar />
    </div>
  </div>
);

const Scan = () => <></>;
const Data = () => <></>;
const Info = () => <></>;
const PersonalSettings = () => <></>;

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Main />} />
            <Route path="/scan" element={<Scan />} />
            <Route path="/data" element={<Data />} />
            <Route path="/routine" element={<WeeklyRoutine />} />
            <Route path="/info" element={<Info />} />
            <Route path="/settings" element={<PersonalSettings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

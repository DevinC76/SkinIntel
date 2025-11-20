// /src/pages/Routine.jsx

import React, { useEffect, useState } from "react";
import "./Routine.css";
import { fetchRoutineData, getTodayRoutine } from "../api/routineApi";

// ------------------------------
// Temporary local test data
// ------------------------------
const testData = {
  Monday: {
    morning: ["Cleansing", "Lotion", "Sunscreen"],
    afternoon: ["Cleansing", "Retinal"],
    night: ["Lotion", "Eye Cream", "Vaseline"],
  },
  Tuesday: {
    morning: ["Cleansing", "Serum"],
    afternoon: ["Mist"],
    night: ["Moisturizer", "Lip Treatment"],
  },
  Wednesday: {
    morning: ["Water Rinse"],
    afternoon: ["Hydration Spray"],
    night: ["Night Cream"],
  },
  Thursday: {
    morning: ["Cleansing"],
    afternoon: ["Serum"],
    night: ["Retinol", "Moisturizer"],
  },
  Friday: {
    morning: ["Cleansing", "Vitamin C"],
    afternoon: ["Sunscreen"],
    night: ["Lotion"],
  },
};

// ------------------------------
// Routine Component
// ------------------------------
export default function Routine() {
  const [today, setToday] = useState("");
  const [routine, setRoutine] = useState(null);

  useEffect(() => {
    async function load() {
      // const data = await fetchRoutineData();
      const data = testData; // ← local test data only
      const { today, routine } = getTodayRoutine(data);

      setToday(today);
      setRoutine(routine);
    }

    load();
  }, []);

  const formattedDate = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="routine-container">
      <h2>{formattedDate}</h2>

      {!routine ? (
        <p>No routine available for today.</p>
      ) : (
        <div className="routine-section">
          {Object.keys(routine).map((period) => (
            <div key={period} className="routine-period">
              <h3>{period[0].toUpperCase() + period.slice(1)}</h3>
              <ul>
                {routine[period].map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

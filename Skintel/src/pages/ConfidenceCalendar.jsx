import React, { useState, useEffect } from "react";
import "./ConfidenceCalendar.css";

function generateDays(numDays = 30) {
    const today = new Date();
    const days = [];

    for (let i = numDays - 1; i >= 0; i--) {
        const day = new Date();
        day.setDate(today.getDate() - i);
        days.push({ date: day, confidence: null });
    }

    return days;
}

export default function ConfidenceCalendar() {
    const [days, setDays] = useState([]);

    useEffect(() => {
        setDays(generateDays(28));
    }, []);

    const handleClick = (index) => {
        setDays((prev) => {
            const newDays = [...prev];
            const current = newDays[index].confidence;
            newDays[index].confidence = current === null ? 0 : (current + 1) % 3;
            return newDays;
        });
    };

    const getColor = (level) => {
        switch (level) {
            case 0:
                return "#ffd56b"; // Medium
            case 1:
                return "#ff7b7b"; // Low
            case 2:
                return "#4caf50"; // High
            case 3:
                return "#444";    // Unset / Gray
            default:
                return "#444";    // Fallback
        }
    };

    const getLabel = (level) => {
        return level === null ? "Not set" : ["Low", "Medium", "High"][level];
    };

    return (
        <div className="confidence-calendar">
            <h2>Confidence Tracker</h2>
            <div className="calendar-grid">
                {days.map((day, index) => (
                    <div
                        key={index}
                        className="calendar-day"
                        style={{ backgroundColor: getColor(day.confidence) }}
                        title={`${day.date.toLocaleDateString()} - ${getLabel(day.confidence)}`}
                        onClick={() => handleClick(index)}
                    />
                ))}
            </div>
        </div>
    );
}

import React, { useState, useEffect } from "react";
import "./ConfidenceCalendar.css";

const colors = {
    0: "#ff7b7b", // Low
    1: "#ffd56b", // Medium
    2: "#4caf50", // High
    3: "#444",    // Max / High (used for unfilled days)
};

const postDataForDay = async (dateStr, value) => {
    console.log("POST to API:", { [dateStr]: value });
};

// Sample data with random values
const sampleDataForMonth = () => ({
    "2025-11-01": Math.floor(Math.random() * 4),
    "2025-11-03": Math.floor(Math.random() * 4),
    "2025-11-07": Math.floor(Math.random() * 4),
    "2025-11-18": Math.floor(Math.random() * 4),
    "2025-11-19": Math.floor(Math.random() * 4),
    "2025-11-02": Math.floor(Math.random() * 4),
});

export default function ConfidenceCalendar() {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [calendarData, setCalendarData] = useState({});

    useEffect(() => {
        setCalendarData(sampleDataForMonth());
    }, [currentMonth]);

    const getMonthDays = (monthDate, data) => {
        const year = monthDate.getFullYear();
        const month = monthDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const days = [];

        for (let i = 0; i < firstDay.getDay(); i++) days.push(null);

        for (let d = 1; d <= lastDay.getDate(); d++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
            // Default unfilled days to 3 (#444)
            days.push({ date: new Date(year, month, d), value: data[dateStr] ?? 3 });
        }

        return days;
    };

    const monthDays = getMonthDays(currentMonth, calendarData);

    const handlePrevMonth = () =>
        setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));

    const handleNextMonth = () =>
        setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));

    const weekDays = ["S", "M", "T", "W", "T", "F", "S"];

    const handleDayClick = async (day) => {
        if (!day) return;

        const today = new Date();
        if (
            day.date.getFullYear() !== today.getFullYear() ||
            day.date.getMonth() !== today.getMonth() ||
            day.date.getDate() !== today.getDate()
        ) return;

        const dateStr = `${day.date.getFullYear()}-${String(day.date.getMonth() + 1).padStart(2, '0')}-${String(day.date.getDate()).padStart(2, '0')}`;
        const currentVal = calendarData[dateStr];
        const newVal = currentVal === 3 ? 0 : (currentVal + 1) % 4; // start cycle from 0 instead of 3

        setCalendarData(prev => ({ ...prev, [dateStr]: newVal }));
        await postDataForDay(dateStr, newVal);
    };

    const today = new Date();

    return (
        <div className="confidence-calendar">
            <div className="calendar-header">
                <button onClick={handlePrevMonth}>◀</button>
                <h2>{currentMonth.toLocaleString("default", { month: "long", year: "numeric" })}</h2>
                <button onClick={handleNextMonth}>▶</button>
            </div>

            <div className="week-labels">
                {weekDays.map(wd => <div key={wd} className="week-label">{wd}</div>)}
            </div>

            <div className="calendar-grid">
                {monthDays.map((day, index) => {
                    if (!day) return <div key={index} className="calendar-day" style={{ backgroundColor: "transparent" }} />;

                    const isToday = day.date.getFullYear() === today.getFullYear() &&
                        day.date.getMonth() === today.getMonth() &&
                        day.date.getDate() === today.getDate();

                    return (
                        <div
                            key={index}
                            className="calendar-day"
                            style={{
                                backgroundColor: colors[day.value],
                                cursor: 'pointer',
                                border: isToday ? '2px solid white' : 'none'
                            }}
                            title={`${day.date.toLocaleDateString()} - Value: ${day.value}`}
                            onClick={() => handleDayClick(day)}
                        />
                    );
                })}
            </div>
        </div>
    );
}

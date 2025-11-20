
export async function fetchRoutineData() {

}

export function getTodayRoutine(data) {
    const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    const today = weekdays[new Date().getDay()];
    return { today, routine: data[today] || null };
}

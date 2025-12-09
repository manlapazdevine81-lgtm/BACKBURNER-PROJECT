document.addEventListener("DOMContentLoaded", function () {
    const calendar = document.getElementById("calendar");
    const monthAndYear = document.getElementById("monthAndYear");

    const prevMonthBtn = document.getElementById("prevMonth");
    const nextMonthBtn = document.getElementById("nextMonth");

    const eventModal = document.getElementById("eventModal");
    const eventDateInput = document.getElementById("eventDate");
    const closeModal = document.getElementById("closeModal");

    let today = new Date();
    let currentMonth = today.getMonth();
    let currentYear = today.getFullYear();

    // YEAR-INDEPENDENT HOLIDAYS
    const holidays = {
        "01-01": "New Year's Day",
        "02-25": "EDSA People Power Revolution",
        "04-17": "Maundy Thursday",
        "04-18": "Good Friday",
        "04-19": "Black Saturday",
        "05-01": "Labor Day",
        "06-12": "Independence Day",
        "08-21": "Ninoy Aquino Day",
        "08-25": "National Heroes Day",
        "11-30": "Bonifacio Day",
        "12-25": "Christmas Day",
        "12-30": "Rizal Day"
    };

    function renderCalendar(month, year) {
        calendar.innerHTML = "";

        const months = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ];

        monthAndYear.textContent = `${months[month]} ${year}`;

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        const days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
        days.forEach(day => {
            const dayHeader = document.createElement("div");
            dayHeader.classList.add("day-name");
            dayHeader.textContent = day;
            calendar.appendChild(dayHeader);
        });

        for(let i=0;i<firstDay;i++){
            const empty = document.createElement("div");
            empty.classList.add("empty-cell");
            calendar.appendChild(empty);
        }

        for(let day=1;day<=daysInMonth;day++){
            const dateCell = document.createElement("div");
            dateCell.classList.add("calendar-day");
            dateCell.textContent = day;

            const monthDay = `${String(month+1).padStart(2,"0")}-${String(day).padStart(2,"0")}`;
            const fullDate = `${year}-${monthDay}`;

            // Highlight today
            if(day===today.getDate() && month===today.getMonth() && year===today.getFullYear()){
                dateCell.classList.add("today");
            }

            // Holiday
            if(holidays[monthDay]){
                dateCell.classList.add("holiday");
                const holidayLabel = document.createElement("span");
                holidayLabel.classList.add("holiday-name");
                holidayLabel.textContent = holidays[monthDay];
                dateCell.appendChild(holidayLabel);
            }

            // Event labels with delete button
            if(events && events[fullDate]){
                events[fullDate].forEach((ev, index)=>{
                    const evLabel = document.createElement("span");
                    evLabel.classList.add("event-name");
                    evLabel.textContent = ev.title;

                    // DELETE BUTTON
                    const deleteBtn = document.createElement("button");
                    deleteBtn.textContent = "×";
                    deleteBtn.classList.add("delete-event-btn");
                    deleteBtn.addEventListener("click",(e)=>{
                        e.stopPropagation(); // prevent modal opening
                        if(confirm(`Delete event "${ev.title}"?`)){
                            deleteEvent(fullDate, index);
                        }
                    });

                    evLabel.appendChild(deleteBtn);
                    dateCell.appendChild(evLabel);
                });
            }

            // Click date → add event
            dateCell.addEventListener("click",()=>{
                eventDateInput.value = fullDate;
                eventModal.style.display="block";
            });

            calendar.appendChild(dateCell);
        }
    }

    function deleteEvent(date, index){
        fetch(`/delete_event/${date}/${index}`, {method: "POST"})
        .then(()=> location.reload());
    }

    prevMonthBtn.addEventListener("click",()=>{
        currentMonth--;
        if(currentMonth<0){currentMonth=11;currentYear--;}
        renderCalendar(currentMonth,currentYear);
    });

    nextMonthBtn.addEventListener("click",()=>{
        currentMonth++;
        if(currentMonth>11){currentMonth=0;currentYear++;}
        renderCalendar(currentMonth,currentYear);
    });

    closeModal.addEventListener("click",()=>{
        eventModal.style.display="none";
    });

    renderCalendar(currentMonth,currentYear);
});

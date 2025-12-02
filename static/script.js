// Placeholder for future interactivity
console.log("Project KALMA loaded");
function filterTasks(view) {
    const today = new Date();
    const tasks = document.querySelectorAll("#taskList li");

    tasks.forEach(task => {
        const dueDate = new Date(task.getAttribute("data-due"));
        const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));

        let show = false;
        if (view === "daily" && diffDays <= 1) show = true;
        else if (view === "weekly" && diffDays <= 7) show = true;
        else if (view === "monthly" && diffDays <= 30) show = true;

        task.style.display = show ? "list-item" : "none";
    });
}
const leaves = document.querySelectorAll(".leaf");
leaves.forEach(leaf => {
  leaf.style.animationDuration = (8 + Math.random() * 7) + "s";
  leaf.style.opacity = 0.4 + Math.random() * 0.4;
});

// Mood Modal Controls
function openMoodTracker() {
  document.getElementById("moodModal").style.display = "flex";
}

function closeMoodTracker() {
  document.getElementById("moodModal").style.display = "none";
}

// Mood Buttons
document.querySelectorAll(".mood-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const mood = btn.dataset.mood;
    alert("You selected: " + mood + " 🌿");
  });
});

// Donut chart for tasks (requires completed & pending to be defined in HTML)
const ctx = document.getElementById('taskChart')?.getContext('2d');
if (ctx) {
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending'],
            datasets: [{
                data: [completed, pending],
                backgroundColor: ['#4CAF50', '#F44336'],
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}




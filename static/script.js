// Placeholder for future interactivity
console.log("Project KALMA loaded");

// ---------- Task Filtering ----------
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

// ---------- Leaf Animation ----------
const leaves = document.querySelectorAll(".leaf");
leaves.forEach(leaf => {
  leaf.style.animationDuration = (8 + Math.random() * 7) + "s";
  leaf.style.opacity = 0.4 + Math.random() * 0.4;
});

// ---------- Mood Tracker Modal Controls ----------
function openMoodTracker() {
  const modal = document.getElementById("moodModal");
  if(modal) modal.style.display = "flex";
}

function closeMoodTracker() {
  const modal = document.getElementById("moodModal");
  if(modal) modal.style.display = "none";
}

// ---------- Mood Buttons Handling ----------
document.addEventListener("DOMContentLoaded", () => {
    // Check if there are mood buttons in the modal
    document.querySelectorAll(".mood-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const mood = btn.dataset.mood;
        const tips = WELLNESS_TIPS[mood] || [];
        const quote = QUOTES[Math.floor(Math.random() * QUOTES.length)];
        alert(`Mood: ${mood}\nTip: ${tips[0]}\nQuote: "${quote}" 🌿`);
        closeMoodTracker();
      });
    });

    // Optional: handle mood select dropdown if no buttons
    const moodSelect = document.getElementById("mood");
    if(moodSelect) {
        moodSelect.addEventListener("change", () => {
            const mood = moodSelect.value;
            const tips = WELLNESS_TIPS[mood] || [];
            const quote = QUOTES[Math.floor(Math.random() * QUOTES.length)];
            alert(`Mood: ${mood}\nTip: ${tips[0]}\nQuote: "${quote}" 🌿`);
        });
    }
});

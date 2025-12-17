from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Data Model --------------------

class Task(BaseModel):
    id: str
    title: str
    completed: bool = False

tasks: list[Task] = []

QUOTES = [
    "Small progress is still progress.",
    "One step at a time.",
    "Consistency beats intensity.",
    "You’re building momentum.",
]

# -------------------- Frontend (UI) --------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Today's Focus</title>
<script src="https://cdn.tailwindcss.com"></script>

<style>
@keyframes fade {{
  from {{ opacity: 0; transform: translateY(4px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.fade {{ animation: fade 0.3s ease-out; }}
</style>
</head>

<body class="bg-slate-50 min-h-screen flex justify-center p-8">
  <div class="w-full max-w-md">
    <h1 class="text-xl font-semibold text-gray-900">Today’s Focus</h1>
    <p class="text-sm text-gray-500 mt-1">Keep moving, one task at a time</p>

    <div class="mt-6 flex gap-2">
      <input id="taskInput"
        class="flex-1 rounded-xl border border-gray-200 px-4 py-3
               focus:outline-none focus:ring-2 focus:ring-emerald-400"
        placeholder="What do you want to work on?" />
      <button onclick="addTask()"
        class="rounded-xl bg-gray-900 text-white px-5 hover:bg-gray-800 transition">
        Add
      </button>
    </div>

    <div id="quote" class="mt-3 text-sm text-emerald-600 fade hidden"></div>

    <div class="mt-6">
      <div class="flex justify-between text-xs text-gray-500 mb-1">
        <span>Progress</span>
        <span id="progressText">0%</span>
      </div>
      <div class="h-1.5 bg-gray-200 rounded-full">
        <div id="progressBar"
          class="h-1.5 bg-emerald-500 rounded-full transition-all"
          style="width:0%"></div>
      </div>
    </div>

    <ul id="taskList" class="mt-6 space-y-2"></ul>
  </div>

<script>
const QUOTES = {QUOTES};

async function fetchTasks() {{
  const res = await fetch('/tasks');
  return res.json();
}}

async function renderTasks() {{
  const tasks = await fetchTasks();
  const list = document.getElementById("taskList");
  list.innerHTML = "";

  let completed = 0;

  tasks.forEach(task => {{
    if (task.completed) completed++;

    const li = document.createElement("li");
    li.className =
      "flex justify-between items-center rounded-xl border bg-white px-4 py-3";

    li.innerHTML = `
      <div class="flex items-center gap-2">
        <input type="checkbox" ${task.completed ? "checked" : ""}
          onchange="toggleTask('${task.id}')">
        <span class="${task.completed ? "line-through text-gray-400" : ""}">
          ${task.title}
        </span>
      </div>
      <button onclick="deleteTask('${task.id}')"
        class="text-gray-400 hover:text-red-500">✕</button>
    `;

    list.appendChild(li);
  }});

  const progress = tasks.length
    ? Math.round((completed / tasks.length) * 100)
    : 0;

  document.getElementById("progressText").innerText = progress + "%";
  document.getElementById("progressBar").style.width = progress + "%";
}}

async function addTask() {{
  const input = document.getElementById("taskInput");
  if (!input.value.trim()) return;

  await fetch(`/tasks?title=${{encodeURIComponent(input.value)}}`, {{
    method: "POST"
  }});

  const quote = document.getElementById("quote");
  quote.innerText =
    '"' + QUOTES[Math.floor(Math.random() * QUOTES.length)] + '"';
  quote.classList.remove("hidden");

  input.value = "";
  renderTasks();
}}

async function toggleTask(id) {{
  await fetch(`/tasks/${{id}}`, {{ method: "PUT" }});
  renderTasks();
}}

async function deleteTask(id) {{
  await fetch(`/tasks/${{id}}`, {{ method: "DELETE" }});
  renderTasks();
}}

renderTasks();
</script>
</body>
</html>
"""

# -------------------- Backend APIs --------------------

@app.get("/tasks")
def list_tasks():
    return tasks

@app.post("/tasks")
def add_task(title: str):
    task = Task(id=str(uuid4()), title=title)
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}")
def toggle_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            task.completed = not task.completed
            return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    global tasks
    tasks = [t for t in tasks if t.id != task_id]
    return {"success": True}

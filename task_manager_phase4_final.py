import streamlit as st
from datetime import datetime, date
import pandas as pd

st.set_page_config(page_title="Personal Task Manager", layout="wide")

# --- Helper functions ---

def format_due_date(due_date_str):
    try:
        dt = datetime.strptime(due_date_str, "%Y/%m/%d")
        return dt.date()
    except Exception:
        return None

def priority_color(priority):
    return {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }.get(priority, "blue")

def load_tasks():
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    return st.session_state.tasks

def save_task(task):
    st.session_state.tasks.append(task)

def filter_tasks(tasks, keyword):
    if not keyword:
        return tasks
    keyword = keyword.lower()
    return [t for t in tasks if
            keyword in t['name'].lower() or
            keyword in t['description'].lower() or
            keyword in t['status'].lower()]

# --- UI ---

st.title("📋 Personal Task Manager (Phase 4 Final)")

with st.expander("➕ Add New Task"):
    with st.form("task_form", clear_on_submit=True):
        name = st.text_input("Task Name")
        description = st.text_area("Description")
        due_date_str = st.date_input("Due Date")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])

        submitted = st.form_submit_button("Add Task")
        if submitted:
            if not name:
                st.warning("Task Name is required!")
            else:
                task = {
                    "name": name.strip(),
                    "description": description.strip(),
                    "due_date": due_date_str.strftime("%Y/%m/%d"),
                    "priority": priority,
                    "status": status
                }
                save_task(task)
                st.success("✅ Task added successfully!")

tasks = load_tasks()

# Search / Filter
st.markdown("### 🔍 Search / Filter Tasks")
search = st.text_input("Enter a keyword to filter by Task, Description, or Status")
filtered_tasks = filter_tasks(tasks, search)

# Task List Display
st.markdown("### 📑 Your Task List")
if filtered_tasks:
    for t in filtered_tasks:
        due = format_due_date(t["due_date"])
        due_str = due.strftime("%Y-%m-%d") if due else "No due date"
        col1, col2, col3, col4 = st.columns([3, 5, 2, 2])
        with col1:
            st.markdown(f"**{t['name']}**")
            st.markdown(f"_{t['description']}_")
        with col2:
            st.markdown(f"**Status:** {t['status']}")
        with col3:
            st.markdown(f"**Due:** {due_str}")
        with col4:
            color = priority_color(t['priority'])
            st.markdown(f"**Priority:** <span style='color:{color};font-weight:bold'>{t['priority']}</span>", unsafe_allow_html=True)
        st.markdown("---")
else:
    st.info("No tasks to show.")

# Summary and Stats
st.markdown("### 📊 Task Overview")

total_tasks = len(tasks)
due_today = sum(1 for t in tasks if format_due_date(t["due_date"]) == date.today())
overdue = sum(1 for t in tasks if format_due_date(t["due_date"]) and format_due_date(t["due_date"]) < date.today() and t["status"] != "Completed")
completed = sum(1 for t in tasks if t["status"] == "Completed")
percent_completed = (completed / total_tasks * 100) if total_tasks > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📌 Total Tasks", total_tasks)
col2.metric("📅 Due Today", due_today)
col3.metric("⚠️ Overdue", overdue)
col4.metric("✅ Completed", completed)
col5.metric("📈 % Completed", f"{percent_completed:.1f}%")

# Task Count by Status Bar Chart
status_counts = pd.Series([t["status"] for t in tasks]).value_counts()
st.bar_chart(status_counts.rename_axis("Status").reset_index(name="Count").set_index("Status"))

# Task Count by Priority Bar Chart
priority_counts = pd.Series([t["priority"] for t in tasks]).value_counts()
st.bar_chart(priority_counts.rename_axis("Priority").reset_index(name="Count").set_index("Priority"))

st.markdown("### 📅 Calendar View (Grouped by Due Date)")

# Group tasks by due date (date object)
tasks_by_date = {}
for t in tasks:
    due = format_due_date(t["due_date"])
    if due:
        tasks_by_date.setdefault(due, []).append(t)

if tasks_by_date:
    for due_date_key in sorted(tasks_by_date.keys()):
        st.markdown(f"**{due_date_key.strftime('%Y-%m-%d')}**")
        for task in tasks_by_date[due_date_key]:
            st.markdown(f"- {task['name']} - {task['status']} - Priority: {task['priority']}")
else:
    st.info("No tasks with due dates to show.")


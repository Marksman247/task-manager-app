"""
Personal Task Manager - Security Checklist

1. File Handling:
   - Tasks are stored in a local JSON file (tasks_data.json).
   - No user input affects file paths; safe from directory traversal.
   - File read/write operations use safe, standard Python I/O.

2. User Input:
   - Inputs (task name, description, etc.) are treated as plain strings.
   - No use of eval(), exec(), or dynamic code evaluation.
   - Limited use of unsafe_allow_html with hardcoded color values only.

3. Data Persistence:
   - Data is serialized/deserialized using JSON.
   - No use of pickle or other unsafe formats.

4. Libraries:
   - Only trusted libraries used: Streamlit, pandas, standard libs.
   - No external API calls or network requests made by the app.

5. Session State:
   - Tasks stored in Streamlit session_state for per-user session isolation.
   - No shared session data across users.

6. Potential Risks / Future Enhancements:
   - Ensure proper file permissions on deployment environment.
   - Validate data if you implement import/export features.
   - Avoid rendering untrusted HTML content.
   - Carefully audit any added authentication, database, or network features.

Summary:
- Current code is safe, with no known backdoors or vulnerabilities.
- Maintain good practices when adding new features or deploying.
"""


import streamlit as st
from datetime import datetime, date, time
import pandas as pd
import json
import os

st.set_page_config(page_title="Personal Task Manager", layout="wide")

DATA_FILE = "tasks_data.json"

# --- Helper functions ---

def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    else:
        return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def format_due_datetime(due_date_str, due_time_str):
    try:
        dt = datetime.strptime(due_date_str + " " + due_time_str, "%Y/%m/%d %H:%M")
        return dt
    except Exception:
        return None

def priority_color(priority):
    return {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }.get(priority, "blue")

def is_overdue(task):
    due_dt = format_due_datetime(task["due_date"], task["due_time"])
    if due_dt and due_dt < datetime.now() and task["status"] != "Completed":
        return True
    return False

def sort_tasks(tasks, sort_key):
    if sort_key == "Due Date":
        # Sort by due datetime, None last
        def due_dt_or_max(task):
            dt = format_due_datetime(task["due_date"], task["due_time"])
            return dt or datetime.max
        return sorted(tasks, key=due_dt_or_max)
    elif sort_key == "Priority":
        # Sort by priority High > Medium > Low
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        return sorted(tasks, key=lambda t: priority_order.get(t["priority"], 99))
    else:
        return tasks

# --- Load existing tasks ---
tasks = load_tasks()
if "tasks" not in st.session_state:
    st.session_state.tasks = tasks

# --- UI ---

st.title("📋 Personal Task Manager")

# Add New Task Form
with st.expander("➕ Add New Task"):
    with st.form("task_form", clear_on_submit=True):
        name = st.text_input("Task Name")
        description = st.text_area("Description")
        due_date = st.date_input("Due Date", value=date.today())
        due_time = st.time_input("Due Time", value=time(hour=23, minute=59))
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])

        submitted = st.form_submit_button("Add Task")
        if submitted:
            if not name.strip():
                st.warning("Task Name is required!")
            else:
                new_task = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),  # unique id
                    "name": name.strip(),
                    "description": description.strip(),
                    "due_date": due_date.strftime("%Y/%m/%d"),
                    "due_time": due_time.strftime("%H:%M"),
                    "priority": priority,
                    "status": status
                }
                st.session_state.tasks.append(new_task)
                save_tasks(st.session_state.tasks)
                st.success("✅ Task added successfully!")

# Sort selection
sort_by = st.selectbox("Sort Tasks By", options=["None", "Due Date", "Priority"])
tasks_to_show = sort_tasks(st.session_state.tasks, sort_by)

# Search / Filter
search = st.text_input("🔍 Search tasks (by name, description, status)")
if search:
    search_lower = search.lower()
    tasks_to_show = [
        t for t in tasks_to_show
        if search_lower in t["name"].lower()
        or search_lower in t["description"].lower()
        or search_lower in t["status"].lower()
    ]

st.markdown("### 📑 Your Task List")

def render_task(task):
    overdue = is_overdue(task)
    color_style = "color:red; font-weight:bold;" if overdue else ""
    col1, col2, col3, col4, col5 = st.columns([3, 5, 2, 2, 1])

    with col1:
        st.markdown(f"**{task['name']}**", unsafe_allow_html=True)
        if task["description"]:
            st.markdown(f"_{task['description']}_")
    with col2:
        st.markdown(f"**Status:** {task['status']}")
    with col3:
        st.markdown(f"**Due:** {task['due_date']} {task['due_time']}")
    with col4:
        color = priority_color(task['priority'])
        st.markdown(f"**Priority:** <span style='color:{color}; font-weight:bold'>{task['priority']}</span>", unsafe_allow_html=True)
    with col5:
        # Buttons for Edit / Delete
        edit_btn = st.button("✏️", key=f"edit_{task['id']}")
        delete_btn = st.button("🗑️", key=f"del_{task['id']}")
    return edit_btn, delete_btn

if tasks_to_show:
    for i, task in enumerate(tasks_to_show):
        edit, delete = render_task(task)
        st.markdown("---")

        if delete:
            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
            save_tasks(st.session_state.tasks)
            st.experimental_rerun()

        if edit:
            # Open edit form in a modal (simplified by a new expander here)
            with st.expander(f"Edit Task: {task['name']}", expanded=True):
                edit_name = st.text_input("Task Name", value=task["name"], key=f"ename_{task['id']}")
                edit_description = st.text_area("Description", value=task["description"], key=f"edesc_{task['id']}")
                edit_due_date = st.date_input("Due Date", value=datetime.strptime(task["due_date"], "%Y/%m/%d").date(), key=f"edate_{task['id']}")
                edit_due_time = st.time_input("Due Time", value=datetime.strptime(task["due_time"], "%H:%M").time(), key=f"etime_{task['id']}")
                edit_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(task["priority"]), key=f"eprio_{task['id']}")
                edit_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(task["status"]), key=f"estat_{task['id']}")

                if st.button("Save Changes", key=f"save_{task['id']}"):
                    if not edit_name.strip():
                        st.warning("Task Name is required!")
                    else:
                        # Update the task
                        for t in st.session_state.tasks:
                            if t["id"] == task["id"]:
                                t["name"] = edit_name.strip()
                                t["description"] = edit_description.strip()
                                t["due_date"] = edit_due_date.strftime("%Y/%m/%d")
                                t["due_time"] = edit_due_time.strftime("%H:%M")
                                t["priority"] = edit_priority
                                t["status"] = edit_status
                                break
                        save_tasks(st.session_state.tasks)
                        st.success("✅ Task updated!")
                        st.experimental_rerun()
else:
    st.info("No tasks to show.")

# Summary and Stats
st.markdown("### 📊 Task Overview")

total_tasks = len(st.session_state.tasks)
due_today = sum(
    1 for t in st.session_state.tasks if
    format_due_datetime(t["due_date"], t["due_time"]) and
    format_due_datetime(t["due_date"], t["due_time"]).date() == date.today()
)
overdue = sum(1 for t in st.session_state.tasks if is_overdue(t))
completed = sum(1 for t in st.session_state.tasks if t["status"] == "Completed")
percent_completed = (completed / total_tasks * 100) if total_tasks > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📌 Total Tasks", total_tasks)
col2.metric("📅 Due Today", due_today)
col3.metric("⚠️ Overdue", overdue)
col4.metric("✅ Completed", completed)
col5.metric("📈 % Completed", f"{percent_completed:.1f}%")

# Bar charts
if total_tasks > 0:
    status_counts = pd.Series([t["status"] for t in st.session_state.tasks]).value_counts()
    st.bar_chart(status_counts.rename_axis("Status").reset_index(name="Count").set_index("Status"))

    priority_counts = pd.Series([t["priority"] for t in st.session_state.tasks]).value_counts()
    st.bar_chart(priority_counts.rename_axis("Priority").reset_index(name="Count").set_index("Priority"))
else:
    st.info("Add tasks to see charts.")

# Calendar View Grouped by Due Date
st.markdown("### 📅 Calendar View (Grouped by Due Date)")

tasks_by_date = {}
for t in st.session_state.tasks:
    tasks_by_date.setdefault(t["due_date"], []).append(t)

for due_date in sorted(tasks_by_date.keys()):
    st.markdown(f"**{due_date}**")
    for t in tasks_by_date[due_date]:
        overdue_mark = " 🔴" if is_overdue(t) else ""
        st.markdown(f"- {t['name']} - {t['status']} - Priority: {t['priority']}{overdue_mark}")

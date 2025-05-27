import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# App title
st.title("📋 Personal Task Manager (Phase 4)")

# Initialize session state for tasks
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=['Task', 'Description', 'Due Date', 'Status'])

# Sidebar for adding tasks
st.sidebar.header("➕ Add New Task")
task_name = st.sidebar.text_input("Task Name")
task_description = st.sidebar.text_area("Description")
due_date = st.sidebar.date_input("Due Date", value=datetime.today())
status = st.sidebar.selectbox("Status", ['Pending', 'In Progress', 'Completed'])

if st.sidebar.button("Add Task"):
    if task_name.strip() == "":
        st.sidebar.error("Task Name is required.")
    else:
        new_task = pd.DataFrame({
            'Task': [task_name],
            'Description': [task_description],
            'Due Date': [due_date.strftime('%Y-%m-%d')],
            'Status': [status]
        })
        st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
        st.sidebar.success("✅ Task added successfully!")

# Save and Load Options
st.sidebar.markdown("---")
if st.sidebar.button("💾 Save Tasks to CSV"):
    st.session_state.tasks.to_csv("tasks_data.csv", index=False)
    st.sidebar.success("Tasks saved to 'tasks_data.csv'")

if st.sidebar.button("📂 Load Tasks from CSV"):
    if os.path.exists("tasks_data.csv"):
        st.session_state.tasks = pd.read_csv("tasks_data.csv")
        st.sidebar.success("Tasks loaded from 'tasks_data.csv'")
    else:
        st.sidebar.error("No saved task file found.")

# Task Summary Dashboard
st.subheader("📊 Task Overview")

if not st.session_state.tasks.empty:
    total_tasks = len(st.session_state.tasks)
    today = date.today()
    due_today = len(st.session_state.tasks[st.session_state.tasks['Due Date'] == today.strftime('%Y-%m-%d')])
    overdue = len(st.session_state.tasks[pd.to_datetime(st.session_state.tasks['Due Date']) < pd.to_datetime(today)])

    completed = len(st.session_state.tasks[st.session_state.tasks['Status'] == 'Completed'])
    completion_pct = int((completed / total_tasks) * 100)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📌 Total Tasks", total_tasks)
    col2.metric("📅 Due Today", due_today)
    col3.metric("⚠️ Overdue", overdue)
    col4.metric("✅ Completed", completed)

    st.progress(completion_pct / 100)
    st.caption(f"📈 {completion_pct}% of tasks completed.")
else:
    st.info("No tasks yet. Add some from the sidebar!")

# Task Search/Filter
st.subheader("🔍 Search / Filter Tasks")
search_query = st.text_input("Enter keyword to filter by Task, Description, or Status")

# Apply search filter
if search_query:
    filtered_tasks = st.session_state.tasks[
        st.session_state.tasks.apply(lambda row: search_query.lower() in row['Task'].lower()
                                     or search_query.lower() in row['Description'].lower()
                                     or search_query.lower() in row['Status'].lower(), axis=1)
    ]
else:
    filtered_tasks = st.session_state.tasks

# Task List
st.subheader("📑 Your Task List")

if filtered_tasks.empty:
    st.info("No matching tasks found or no tasks added yet.")
else:
    for index, row in filtered_tasks.iterrows():
        # Assign color & emoji based on status
        if row['Status'] == 'Pending':
            status_color = '🟡 Pending'
        elif row['Status'] == 'In Progress':
            status_color = '🔵 In Progress'
        elif row['Status'] == 'Completed':
            status_color = '🟢 Completed'
        else:
            status_color = row['Status']

        with st.expander(f"{row['Task']} | {status_color} | Due: {row['Due Date']}"):
            st.write(f"**📝 Description:** {row['Description']}")
            st.write(f"**📅 Due Date:** {row['Due Date']}")
            st.write(f"**🔖 Status:** {status_color}")

            # Editable fields
            new_name = st.text_input(f"✏️ Edit Task Name ({index})", value=row['Task'], key=f"name_{index}")
            new_desc = st.text_area(f"✏️ Edit Description ({index})", value=row['Description'], key=f"desc_{index}")
            new_due = st.date_input(f"📅 Edit Due Date ({index})", value=pd.to_datetime(row['Due Date']), key=f"due_{index}")
            new_status = st.selectbox(f"📌 Edit Status ({index})", ['Pending', 'In Progress', 'Completed'],
                                      index=['Pending', 'In Progress', 'Completed'].index(row['Status']),
                                      key=f"status_{index}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Update Task", key=f"update_{index}"):
                    st.session_state.tasks.at[index, 'Task'] = new_name
                    st.session_state.tasks.at[index, 'Description'] = new_desc
                    st.session_state.tasks.at[index, 'Due Date'] = new_due.strftime('%Y-%m-%d')
                    st.session_state.tasks.at[index, 'Status'] = new_status
                    st.success("✅ Task updated.")
                    st.experimental_rerun()

            with col2:
                if st.button("🗑️ Delete Task", key=f"delete_{index}"):
                    st.session_state.tasks.drop(index, inplace=True)
                    st.session_state.tasks.reset_index(drop=True, inplace=True)
                    st.success("🗑️ Task deleted.")
                    st.experimental_rerun()

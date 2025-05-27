
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# App title
st.title("📋 Personal Task Manager (Phase 2)")

# Initialize session state for task storage
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=['Task', 'Description', 'Due Date', 'Status'])

# Sidebar for adding a task
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

# Sidebar: Save and Load Options
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

# Task Search/Filter
st.subheader("🔍 Search / Filter Tasks")
search_query = st.text_input("Enter a keyword to filter by Task, Description, or Status")

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
        with st.expander(f"{row['Task']} - {row['Status']} (Due: {row['Due Date']})"):
            st.write(f"**Description:** {row['Description']}")
            st.write(f"**Due Date:** {row['Due Date']}")
            st.write(f"**Status:** {row['Status']}")

            new_name = st.text_input(f"Edit Task Name ({index})", value=row['Task'], key=f"name_{index}")
            new_desc = st.text_area(f"Edit Description ({index})", value=row['Description'], key=f"desc_{index}")
            new_due = st.date_input(f"Edit Due Date ({index})", value=pd.to_datetime(row['Due Date']), key=f"due_{index}")
            new_status = st.selectbox(f"Edit Status ({index})", ['Pending', 'In Progress', 'Completed'],
                                      index=['Pending', 'In Progress', 'Completed'].index(row['Status']),
                                      key=f"status_{index}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Task", key=f"update_{index}"):
                    st.session_state.tasks.at[index, 'Task'] = new_name
                    st.session_state.tasks.at[index, 'Description'] = new_desc
                    st.session_state.tasks.at[index, 'Due Date'] = new_due.strftime('%Y-%m-%d')
                    st.session_state.tasks.at[index, 'Status'] = new_status
                    st.success("✅ Task updated successfully.")
                    st.experimental_rerun()

            with col2:
                if st.button("Delete Task", key=f"delete_{index}"):
                    st.session_state.tasks.drop(index, inplace=True)
                    st.session_state.tasks.reset_index(drop=True, inplace=True)
                    st.success("🗑️ Task deleted successfully.")
                    st.experimental_rerun()

# Task Statistics Dashboard
st.subheader("📊 Task Overview")
if st.session_state.tasks.empty:
    st.info("No tasks to analyze.")
else:
    status_counts = st.session_state.tasks['Status'].value_counts()
    st.write("### Task Count by Status")
    st.bar_chart(status_counts)

    total_tasks = len(st.session_state.tasks)
    pending_tasks = status_counts.get('Pending', 0)
    in_progress_tasks = status_counts.get('In Progress', 0)
    completed_tasks = status_counts.get('Completed', 0)

    st.write(f"**Total Tasks:** {total_tasks}")
    st.write(f"**Pending:** {pending_tasks}")
    st.write(f"**In Progress:** {in_progress_tasks}")
    st.write(f"**Completed:** {completed_tasks}")

# Tasks Grouped by Due Date (Simple Calendar-like Listing)
st.subheader("📅 Tasks Grouped by Due Date")
if not st.session_state.tasks.empty:
    grouped = st.session_state.tasks.groupby('Due Date')
    for due_date, tasks_on_date in grouped:
        st.markdown(f"### {due_date}")
        for _, task in tasks_on_date.iterrows():
            st.write(f"- {task['Task']} ({task['Status']})")
else:
    st.info("No tasks to show.")

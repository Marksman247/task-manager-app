import streamlit as st
import pandas as pd
from datetime import datetime
import os
from st_aggrid import AgGrid, GridOptionsBuilder

# App title
st.title("📋 Personal Task Manager (Phase 4 Final)")

# Initialize session state for task storage
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=['Task', 'Description', 'Due Date', 'Priority', 'Status'])

# Sidebar for adding a task
st.sidebar.header("➕ Add New Task")
task_name = st.sidebar.text_input("Task Name")
task_description = st.sidebar.text_area("Description")
due_date = st.sidebar.date_input("Due Date", value=datetime.today())
priority = st.sidebar.selectbox("Priority", ['High', 'Medium', 'Low'])
status = st.sidebar.selectbox("Status", ['Pending', 'In Progress', 'Completed'])

if st.sidebar.button("Add Task"):
    if task_name.strip() == "":
        st.sidebar.error("Task Name is required.")
    else:
        new_task = pd.DataFrame({
            'Task': [task_name],
            'Description': [task_description],
            'Due Date': [due_date.strftime('%Y-%m-%d')],
            'Priority': [priority],
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

if search_query:
    filtered_tasks = st.session_state.tasks[
        st.session_state.tasks.apply(lambda row: search_query.lower() in row['Task'].lower() 
                                     or search_query.lower() in row['Description'].lower()
                                     or search_query.lower() in row['Status'].lower(), axis=1)
    ]
else:
    filtered_tasks = st.session_state.tasks

# Helper: Color for status
def get_status_color(status):
    if status == 'Pending':
        return 'orange'
    elif status == 'In Progress':
        return 'blue'
    elif status == 'Completed':
        return 'green'
    else:
        return 'gray'

# Task List with edit/delete
st.subheader("📑 Your Task List")
if filtered_tasks.empty:
    st.info("No matching tasks found or no tasks added yet.")
else:
    for index, row in filtered_tasks.iterrows():
        due_date_obj = pd.to_datetime(row['Due Date'])
        today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
        overdue = due_date_obj < today and row['Status'] != 'Completed'
        due_today = due_date_obj == today

        with st.expander(f"{row['Task']} - :{get_status_color(row['Status'])}[{row['Status']}] (Due: {row['Due Date']})"):
            if due_today:
                st.warning("📌 Task is due today!")
            elif overdue:
                st.error("⚠️ Task is overdue!")

            st.write(f"**Description:** {row['Description']}")
            st.write(f"**Priority:** {row['Priority']}")
            st.write(f"**Due Date:** {row['Due Date']}")
            st.write(f"**Status:** :{get_status_color(row['Status'])}[{row['Status']}]")

            new_name = st.text_input(f"Edit Task Name ({index})", value=row['Task'], key=f"name_{index}")
            new_desc = st.text_area(f"Edit Description ({index})", value=row['Description'], key=f"desc_{index}")
            new_due = st.date_input(f"Edit Due Date ({index})", value=due_date_obj, key=f"due_{index}")
            new_priority = st.selectbox(f"Edit Priority ({index})", ['High', 'Medium', 'Low'],
                                        index=['High', 'Medium', 'Low'].index(row['Priority']), key=f"prio_{index}")
            new_status = st.selectbox(f"Edit Status ({index})", ['Pending', 'In Progress', 'Completed'],
                                      index=['Pending', 'In Progress', 'Completed'].index(row['Status']),
                                      key=f"status_{index}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Task", key=f"update_{index}"):
                    st.session_state.tasks.at[index, 'Task'] = new_name
                    st.session_state.tasks.at[index, 'Description'] = new_desc
                    st.session_state.tasks.at[index, 'Due Date'] = new_due.strftime('%Y-%m-%d')
                    st.session_state.tasks.at[index, 'Priority'] = new_priority
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
    priority_counts = st.session_state.tasks['Priority'].value_counts()

    st.write("### 📈 Task Count by Status")
    st.bar_chart(status_counts)

    st.write("### 🎨 Task Count by Priority")
    st.bar_chart(priority_counts)

    total_tasks = len(st.session_state.tasks)
    st.write(f"**Total Tasks:** {total_tasks}")

    # 📌 Task Summary Metrics
    today_str = datetime.today().strftime('%Y-%m-%d')
    due_today = len(st.session_state.tasks[st.session_state.tasks['Due Date'] == today_str])
    overdue = len(st.session_state.tasks[
        (pd.to_datetime(st.session_state.tasks['Due Date']) < pd.to_datetime(today_str)) &
        (st.session_state.tasks['Status'] != 'Completed')
    ])
    completed = len(st.session_state.tasks[st.session_state.tasks['Status'] == 'Completed'])

    completion_pct = int((completed / total_tasks) * 100)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📌 Total Tasks", total_tasks)
    col2.metric("📅 Due Today", due_today)
    col3.metric("⚠️ Overdue", overdue)
    col4.metric("✅ Completed", completed)

    st.progress(completion_pct / 100)
    st.caption(f"📈 {completion_pct}% of tasks completed.")

# Clean spacing
st.markdown("---")

# Calendar View with AgGrid
st.subheader("📅 Calendar View (Grouped by Due Date)")

if st.session_state.tasks.empty:
    st.info("No tasks to display in calendar view.")
else:
    df = st.session_state.tasks.copy()
    df['Due Date'] = pd.to_datetime(df['Due Date'])
    df = df.sort_values('Due Date')

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_default_column(editable=True, groupable=True, filterable=True)
    gb.configure_column("Due Date", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
    grid_options = gb.build()

    AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode='MODEL_CHANGED',
        theme='fresh',
        height=350,
        fit_columns_on_grid_load=True
    )

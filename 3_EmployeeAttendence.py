import streamlit as st
import pandas as pd
from io import BytesIO

# Initialize session state
if "attendance_data" not in st.session_state:
    st.session_state.attendance_data = []

st.title("🕒 Employee Attendance Tracker")

# Attendance Form
with st.form("attendance_form"):
    emp_id = st.text_input("Employee ID")
    emp_name = st.text_input("Employee Name")
    status = st.selectbox("Attendance Status", ["Present", "Absent", "Remote", "On Leave"])
    date = st.date_input("Select Date", pd.Timestamp.now().date())
    submitted = st.form_submit_button("Submit Attendance")

    if submitted:
        st.session_state.attendance_data.append({
            "Date": date,
            "Employee ID": emp_id,
            "Employee Name": emp_name,
            "Status": status,
            "Timestamp": pd.Timestamp.now()
        })
        st.success("Attendance recorded!")

# Display Attendance Table
if st.session_state.attendance_data:
    df = pd.DataFrame(st.session_state.attendance_data)
    st.subheader("📋 Attendance Records")
    st.dataframe(df)

    # Excel Download
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance')
        return output.getvalue()

    excel_data = to_excel(df)
    st.download_button(
        label="📥 Download Attendance as Excel",
        data=excel_data,
        file_name="employee_attendance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No attendance records yet. Please submit the form above.")

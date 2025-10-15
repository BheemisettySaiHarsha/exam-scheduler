import streamlit as st
import pandas as pd

def load_csv(path: str):
    """Loads a CSV file and handles errors."""
    try:
        # Assuming all necessary data is pre-processed and ready to load
        return pd.read_csv(path)
    except Exception as e:
        # Streamlit error handling
        st.error(f"Error loading {path}. Please ensure the file is in the correct location: {e}")
        return pd.DataFrame()

# Title and config
st.set_page_config(page_title="Exam Schedule (Preview)", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    </style>
    """, unsafe_allow_html=True)

st.title("🗓️ Mid-Term Schedule")

# File loading (ensure these are present in the root or adjust paths)
# NOTE: In a real-world scenario, you might upload these files directly via st.file_uploader
students_df = load_csv("Students.csv")
venues_df = load_csv("Venues.csv")

# Validate loaded data
if students_df.empty or venues_df.empty:
    st.warning("One or both CSV files are missing or failed to load. Ensure Students.csv and Venues.csv are present.")
    # Stop the app execution if critical data is missing
    st.stop()

# UI
with st.sidebar:
    st.header("Search")
    roll_input = st.text_input("Enter Roll Number", help="Case-insensitive search (e.g., B22EE083)")

    # The button is primarily for mobile users or for clear intent, but the logic runs on input change anyway
    if st.button("Search"):
        pass  

# Process input if provided
if roll_input:
    roll_upper = str(roll_input).strip().upper()
    
    # Normalize Roll No column existence check
    if "Roll No" not in students_df.columns:
        st.error("The 'Students.csv' file is missing the 'Roll No' column.")
        st.stop()

    # Case-insensitive match on Roll Number
    matched = students_df[students_df["Roll No"].astype(str).str.upper() == roll_upper]

    if matched.empty:
        st.error(f"No student found with Roll No: **{roll_input}**")
    else:
        # Show student details (take first match)
        student = matched.iloc[0]
        st.subheader("Student Details")
        st.markdown(f"**Name:** {student.get('Student Name','N/A')}")
        st.markdown(f"**Email:** {student.get('Email','N/A')}")

        # Build exam schedule rows (deduplicate by Course Code)
        courses = matched.drop_duplicates(subset=["Course Code"])[
            ["Date", "Time", "Course Code", "Course Name", "Instructor 1"]
        ]

        # Gather venue/rooms per course
        schedule_rows = []
        for _, row in courses.iterrows():
            code = str(row["Course Code"])
            venue_rows = venues_df[venues_df["Course Code"].astype(str) == code]
            
            # Extract main venue (assuming one main venue per course code entry)
            venue = venue_rows.iloc[0]["Venue"] if not venue_rows.empty else "Not Assigned"
            # Extract all unique rooms associated with this course code
            rooms = ", ".join(venue_rows["Room"].astype(str).unique()) if not venue_rows.empty else "-"
            
            schedule_rows.append({
                "Date": row["Date"],
                "Time": row["Time"],
                "Course Code": code,
                "Course Name": row["Course Name"],
                "Instructor": row["Instructor 1"],
                "Venue": venue,
                "Rooms": rooms
            })

        schedule_df = pd.DataFrame(schedule_rows)
        
        # --- MODIFICATION START ---
        # Set the index to start from 1 instead of 0
        schedule_df.index = range(1, len(schedule_df) + 1)
        # --- MODIFICATION END ---

        st.subheader("Exam Schedule")
        # Display the DataFrame
        st.dataframe(schedule_df, height=300, use_container_width=True)
else:
    st.info("Enter a roll number in the sidebar and click Search to view results.")
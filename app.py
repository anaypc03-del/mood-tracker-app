import streamlit as st
import pandas as pd
import datetime
import os

# 1. Setup & Configuration
st.set_page_config(page_title="Mood Log Lite", page_icon="📝", layout="centered")
st.title("📝 Mood Log Lite")
st.write("A lightweight tool to track your emotional well-being over time.")

DATA_FILE = "mood_log.csv"

# Helper functions to load and save data locally
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Timestamp", "Date", "Mood", "Intensity", "Notes"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Load existing entries into session state
if "mood_df" not in st.session_state:
    st.session_state.mood_df = load_data()

# 2. Mood Logging Form
st.subheader("How are you feeling right now?")
with st.form("mood_form", clear_on_submit=True):
    # Mood selectors
    mood_options = ["😊 Happy", "🥱 Tired", "😔 Sad", "😠 Angry", "🧠 Focused", "🧘 Calm", "🌀 Anxious"]
    selected_mood = st.selectbox("Select your core mood:", mood_options)
    
    # Optional metadata
    intensity = st.slider("Mood Intensity (1 = Barely, 10 = Extremely)", 1, 10, 5)
    notes = st.text_area("Optional Notes (What's making you feel this way?)", placeholder="Write reflections here...")
    
    submit_button = st.form_submit_button("Log Mood")

# Handle form submission
if submit_button:
    now = datetime.datetime.now()
    new_entry = {
        "Timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "Date": now.strftime("%Y-%m-%d"),
        "Mood": selected_mood,
        "Intensity": intensity,
        "Notes": notes
    }
    
    # Append data and save
    st.session_state.mood_df = pd.concat([st.session_state.mood_df, pd.DataFrame([new_entry])], ignore_index=True)
    save_data(st.session_state.mood_df)
    st.success("Mood logged successfully!")

# 3. Analytics & Visualization Dashboard
df = st.session_state.mood_df

if not df.empty:
    st.divider()
    st.subheader("📊 Your Mood Analytics")
    
    # Quick Summary Metrics
    total_logs = len(df)
    most_frequent_mood = df["Mood"].mode()[0] if not df["Mood"].empty else "N/A"
    avg_intensity = round(df["Intensity"].astype(float).mean(), 1)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logs", total_logs)
    col2.metric("Top Mood", most_frequent_mood)
    col3.metric("Avg Intensity", f"{avg_intensity}/10")
    
    # Trend Chart
    st.write("#### Mood Breakdown")
    mood_counts = df["Mood"].value_counts()
    st.bar_chart(mood_counts)
    
    # History Log View
    st.write("#### Recent Entries")
    st.dataframe(
        df[["Timestamp", "Mood", "Intensity", "Notes"]].sort_values(by="Timestamp", ascending=False),
        use_container_width=True
    )
    
    # Option to reset data
    if st.button("Clear All Data"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.session_state.mood_df = pd.DataFrame(columns=["Timestamp", "Date", "Mood", "Intensity", "Notes"])
        st.rerun()
else:
    st.info("No moods logged yet. Use the form above to log your first mood entry!")

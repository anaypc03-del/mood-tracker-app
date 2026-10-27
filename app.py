import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Mood Tracker App", page_icon="😃", layout="centered"
)

# Initialize session state to store mood entries
if "mood_data" not in st.session_state:
    st.session_state.mood_data = pd.DataFrame(
        columns=["Name", "Date", "Mood", "Note", "Predicted Mood"]
    )

st.title("😃 Mood Tracker App")
st.subheader("Welcome!")

# --- Input Form ---
with st.form("mood_form"):
    user_name = st.text_input("Your name", placeholder="Enter your name")

    selected_mood = st.selectbox(
        "How are you feeling today?",
        ["Happy", "Excited", "Calm", "Neutral", "Sad", "Anxious", "Stressed"],
    )

    note = st.text_area(
        "Add a note (Optional)", placeholder="Write a few thoughts about your day..."
    )

    # Simulated AI Predicted Mood based on simple keywords or selection
    ai_prediction = (
        "Positive"
        if selected_mood in ["Happy", "Excited", "Calm"]
        else "Neutral"
    )
    st.write(f"**AI Predicted Mood:** {ai_prediction}")

    submitted = st.form_submit_button("Save Entry")

    if submitted:
        if user_name.strip() == "":
            st.warning("Please enter your name before saving.")
        else:
            new_entry = pd.DataFrame(
                [
                    {
                        "Name": user_name,
                        "Date": pd.Timestamp.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Mood": selected_mood,
                        "Note": note,
                        "Predicted Mood": ai_prediction,
                    }
                ]
            )
            st.session_state.mood_data = pd.concat(
                [st.session_state.mood_data, new_entry], ignore_index=True
            )
            st.success("Mood entry saved successfully!")

st.divider()

# --- Mood History ---
st.header("📅 Mood History")
if not st.session_state.mood_data.empty:
    st.dataframe(st.session_state.mood_data, use_container_width=True)
else:
    st.info("No mood entries recorded yet. Fill out the form above to start!")

# --- Mood Distribution & Trend Visualizations ---
if not st.session_state.mood_data.empty:
    st.header("📊 Mood Distribution")
    mood_counts = st.session_state.mood_data["Mood"].value_counts()
    st.bar_chart(mood_counts)

    st.header("📈 Sentiment Trend Over Time")
    # Mapping moods to numerical scores for a simple trend line
    mood_scores = {
        "Excited": 5,
        "Happy": 4,
        "Calm": 3,
        "Neutral": 2,
        "Anxious": 1,
        "Stressed": 1,
        "Sad": 0,
    }
    trend_data = st.session_state.mood_data.copy()
    trend_data["Score"] = trend_data["Mood"].map(mood_scores)
    trend_data["Date"] = pd.to_datetime(trend_data["Date"])
    trend_data = trend_data.set_index("Date")
    st.line_chart(trend_data["Score"])

st.divider()

# --- Export Data ---
st.header("📤 Export Data")
if not st.session_state.mood_data.empty:
    csv_data = st.session_state.mood_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="mood_tracker_data.csv",
        mime="text/csv",
    )
else:
    st.write("No data available to export.")

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()
conn = sqlite3.connect("mood_tracker.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS moods (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mood TEXT, note TEXT, date TEXT, sentiment REAL)""")
cols = [row[1] for row in cursor.execute("PRAGMA table_info(moods)").fetchall()]
if "name" not in cols:
    cursor.execute("ALTER TABLE moods ADD COLUMN name TEXT")
    cursor.execute("UPDATE moods SET name = 'Guest' WHERE name IS NULL")
    conn.commit()

st.title("😃 Mood Tracker App")
st.subheader("Welcome!")
person_name = st.text_input("Your name")
mood = st.selectbox("How are you feeling today?", ["Happy", "Sad", "Neutral", "Angry", "Excited"])
note = st.text_area("Add a note (Optional)")
sentiment_score = sia.polarity_scores(note)["compound"]
predicted_mood = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
st.write(f"AI Predicted Mood: {predicted_mood}")

if st.button("Save Entry"):
    if not person_name.strip():
        st.error("Please enter your name first.")
    else:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO moods (username, name, mood, note, date, sentiment) VALUES (?, ?, ?, ?, ?, ?)", ("Guest", person_name.strip(), mood, note, date, sentiment_score))
        conn.commit()
        st.success("Mood logged successfully!")

st.subheader("📅 Mood History")
df = pd.read_sql_query("SELECT * FROM moods ORDER BY date DESC", conn)
if not df.empty:
    st.dataframe(df[["date", "name", "mood", "note"]], hide_index=True)
    st.subheader("📊 Mood Distribution")
    mood_counts = df["mood"].value_counts()
    fig, ax = plt.subplots()
    mood_counts.plot(kind="bar", color=["green", "red", "gray", "orange", "blue"], ax=ax)
    st.pyplot(fig)
    st.subheader("📈 Sentiment Trend Over Time")
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["sentiment"], marker="o", linestyle="-")
    ax.axhline(0, color="black", linestyle="--")
    st.pyplot(fig)
    st.subheader("📤 Export Data")
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="mood_data.csv", mime="text/csv")
else:
    st.info("No mood entries found. Start tracking today!")
conn.close()

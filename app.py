import streamlit as st
import requests
import json
import os
import csv
from datetime import datetime
import uuid
from collections import Counter

# ----------------------------
# Cache dictionary
# ----------------------------
cache = {}

# ----------------------------
# Files
# ----------------------------
SAVE_FILE = "saved_words.json"
LOG_FILE = "user_search_log.csv"

# ----------------------------
# Unique session-based user ID
# ----------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# ----------------------------
# Load saved words
# ----------------------------
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        saved_words = json.load(f)
else:
    saved_words = []

# ----------------------------
# Translation Function with cache
# ----------------------------
def translate_to_french(text):
    if text in cache:
        return cache[text]

    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": "en|fr"
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        translation = data['responseData']['translatedText']
        cache[text] = translation
        return translation
    else:
        return "Translation error"

# ----------------------------
# Logging Function
# ----------------------------
def log_search(user_id, search_text):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "user_id", "search_text"])
        writer.writerow([datetime.now().isoformat(), user_id, search_text])

# ----------------------------
# Recommendation Function
# ----------------------------
def get_top_recommendations(n=5):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        words = [row["search_text"] for row in reader if row["search_text"].strip()]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(n)]

# ----------------------------
# Streamlit App
# ----------------------------
st.title("?? FrancoLearn - English to French Translator")

# Show recommendations
top_words = get_top_recommendations()
if top_words:
    st.subheader("?? Recommended Words to Learn")
    st.write(", ".join(top_words))

word = st.text_input("Enter an English word:")

if word:
    with st.spinner("Translating..."):
        french_translation = translate_to_french(word)
        if french_translation:
            st.success("Translation complete!")
            st.write(f"**French Translation:** {french_translation}")

            # Log the search
            log_search(st.session_state.user_id, word)
            st.info("? Search logged for recommendations!")

            # Save button
            if st.button("?? Save this word"):
                entry = {"english": word, "french": french_translation}
                if entry not in saved_words:
                    saved_words.append(entry)
                    with open(SAVE_FILE, "w", encoding="utf-8") as f:
                        json.dump(saved_words, f, ensure_ascii=False, indent=2)
                    st.success("? Word saved successfully!")
                else:
                    st.info("?? Word already saved.")

# Show saved words
if st.button("?? Show saved words"):
    st.subheader("Saved Words List")
    if saved_words:
        for i, entry in enumerate(saved_words, start=1):
            st.write(f"{i}. **{entry['english']}** ? *{entry['french']}*")
    else:
        st.warning("No words saved yet.")

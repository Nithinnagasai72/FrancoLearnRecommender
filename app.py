import streamlit as st
import requests
import json
import os

# ----------------------------
# Cache dictionary
# ----------------------------
cache = {}

# ----------------------------
# File to save words
# ----------------------------
SAVE_FILE = "saved_words.json"

# Load saved words from file
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
# Streamlit App
# ----------------------------
st.title("📘 FrancoLearn - English to French Translator")

word = st.text_input("Enter an English word:")

if word:
    with st.spinner("Translating..."):
        french_translation = translate_to_french(word)
        if french_translation:
            st.success("Translation complete!")
            st.write(f"**French Translation:** {french_translation}")

            # Save button
            if st.button("💾 Save this word"):
                entry = {"english": word, "french": french_translation}
                if entry not in saved_words:
                    saved_words.append(entry)
                    with open(SAVE_FILE, "w", encoding="utf-8") as f:
                        json.dump(saved_words, f, ensure_ascii=False, indent=2)
                    st.success("✅ Word saved successfully!")
                else:
                    st.info("ℹ️ Word already saved.")

# Show saved words
if st.button("📋 Show saved words"):
    st.subheader("Saved Words List")
    if saved_words:
        for i, entry in enumerate(saved_words, start=1):
            st.write(f"{i}. **{entry['english']}** → *{entry['french']}*")
    else:
        st.warning("No words saved yet.")


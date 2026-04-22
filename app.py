import streamlit as st
import pickle
import requests
import os
import time

st.set_page_config(page_title="AI Customer Support", layout="centered")

@st.cache_resource
def load_resources():
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

model, vectorizer = load_resources()

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def call_llm(prompt, retries=2):
    for _ in range(retries):
        try:
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": 80,
                    "temperature": 0.3
                }
            }

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=15
            )

            data = response.json()

            if isinstance(data, dict) and "error" in data:
                time.sleep(1.5)
                continue

            return data[0]["generated_text"]

        except:
            time.sleep(1)
    return None

@st.cache_data(show_spinner=False)
def cached_llm(prompt):
    return call_llm(prompt)

def classify_category(text):
    vec = vectorizer.transform([text.lower()])
    return model.predict(vec)[0]

def adjust_category(text, predicted):
    text_lower = text.lower()

    negative_words = [
        "broken", "damaged", "not working", "defective",
        "problem", "issue", "delay", "late",
        "not delivered", "not received"
    ]

    positive_words = [
        "good", "great", "excellent", "amazing", "love"
    ]

    if any(n in text_lower for n in negative_words):
        return "Complaint"

    if any(p in text_lower for p in positive_words):
        return "Feedback"

    return predicted

def detect_sentiment_fallback(text):
    text_lower = text.lower()

    negative_words = [
        "problem","issue","delay","late","not delivered",
        "not received","bad","terrible","frustrated",
        "unhappy","broken","damaged","defective",
        "not satisfied","not very satisfied","could have been better"
    ]

    positive_words = [
        "good","great","love","excellent","amazing",
        "thank you","thanks","appreciate"
    ]

    if any(n in text_lower for n in negative_words):
        return "Negative", "😡"

    if any(p in text_lower for p in positive_words):
        return "Positive", "😊"

    return "Neutral", "🙂"

def llm_analyze_and_respond(text, category):
    prompt = f"""
You are a customer support AI.

Analyze the query and respond.

Rules:
- If complaint or issue → sentiment = Negative
- If mixed → Negative
- If clearly happy → Positive

Return strictly in this format:
Sentiment: <Positive/Negative/Neutral>
Response: <short 1-2 sentence reply>

User Query: {text}
Category: {category}
"""

    result = cached_llm(prompt)

    if not result:
        sentiment, icon = detect_sentiment_fallback(text)

        if sentiment == "Positive":
            reply = "You're welcome! We're glad we could help 😊"
        elif sentiment == "Negative":
            reply = f"I'm sorry for the issue regarding {category}. Let me help resolve it."
        else:
            reply = f"I understand your query about {category}. Let me assist you."

        return sentiment, icon, reply

    result_lower = result.lower()

    if "sentiment:" in result_lower and "response:" in result_lower:
        try:
            sentiment_part = result_lower.split("sentiment:")[1].split("response:")[0].strip()
            response_part = result.split("Response:")[1].strip()

            if "negative" in sentiment_part:
                return "Negative", "😡", response_part
            elif "positive" in sentiment_part:
                return "Positive", "😊", response_part
            else:
                return "Neutral", "🙂", response_part
        except:
            pass

    sentiment, icon = detect_sentiment_fallback(text)
    return sentiment, icon, result

def is_valid_query(text):
    keywords = [
        "order", "product", "delivery", "refund",
        "account", "payment", "service", "experience"
    ]
    return any(word in text.lower() for word in keywords)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(to right, #fdfbfb, #ebedee); }
.title { font-size:40px; font-weight:800; color:#1e293b; text-align:center; margin-bottom:20px; }
.msg-user { background:#3b82f6; color:white; padding:12px; border-radius:15px; margin:10px 0; text-align:right; width:fit-content; margin-left:auto; }
.msg-bot { background:white; color:#1e293b; padding:12px; border-radius:15px; margin:10px 0; border:1px solid #e2e8f0; width:fit-content; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">AI Customer Query Analyzer</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    role_class = "msg-user" if msg["role"] == "user" else "msg-bot"
    emoji = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f'<div class="{role_class}">{emoji} {msg["content"]}</div>', unsafe_allow_html=True)

user_input = st.chat_input("Ask your query...")

if user_input:
    if not is_valid_query(user_input):
        reply = "I can help with orders, delivery, and product issues. Please ask a related query 😊"
        category = "Unknown"
        sentiment_label, icon = "Neutral", "🙂"
    else:
        category = classify_category(user_input)
        category = adjust_category(user_input, category)

        sentiment_label, icon, reply = llm_analyze_and_respond(user_input, category)

    full_response = f"{reply}\n\n📌 {category} | {icon} {sentiment_label}"

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.rerun()
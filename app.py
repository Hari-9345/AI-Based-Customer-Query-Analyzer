import streamlit as st
import pickle
import time
import requests
import os
st.set_page_config(page_title="AI Customer Support", layout="centered")
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
}

def query_huggingface(prompt, retries=3):
    for _ in range(retries):
        try:
            res = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            result = res.json()

            if isinstance(result, dict) and "error" in result:
                time.sleep(2)
                continue

            return result
        except:
            time.sleep(1)
    return None
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
def is_greeting(text):
    greetings = ["hi", "hello", "hey"]
    return text.lower().strip() in greetings

def is_valid_query(text):
    keywords = ["order", "product", "delivery", "refund", "account", "payment"]
    return any(word in text.lower() for word in keywords)
def predict_category(text):
    text_lower = text.lower()

    if any(w in text_lower for w in ["broken", "damaged", "late", "issue", "problem"]):
        return "Complaint"
    if any(w in text_lower for w in ["help", "support", "change", "update", "track"]):
        return "Request"

    vec = vectorizer.transform([text_lower])
    return model.predict(vec)[0]
def detect_sentiment(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["bad", "broken", "delay", "problem", "issue"]):
        return "😡 Negative"
    if any(w in text_lower for w in ["good", "great", "love", "excellent"]):
        return "😊 Positive"
    prompt = f"Classify sentiment: Positive, Negative or Neutral.\nText: {text}\nAnswer:"
    result = query_huggingface(prompt)

    if not result:
        return "🙂 Neutral"

    output = result[0]['generated_text']

    if "Positive" in output:
        return "😊 Positive"
    elif "Negative" in output:
        return "😡 Negative"
    else:
        return "🙂 Neutral"
def generate_response(query, category, sentiment):
    q = query.lower()
    if "broken" in q or "damaged" in q:
        return "We’re really sorry your product arrived damaged 😔 We will replace or refund it immediately."

    if "delivery" in q:
        return "We apologize for the delivery issue. Please check your tracking details or contact support."
    prompt = f"""
    You are a professional customer support assistant.

    Query: {query}
    Category: {category}
    Sentiment: {sentiment}

    Give a helpful and polite response:
    """

    result = query_huggingface(prompt)

    if not result:
        return "We’re here to help! Please try again."

    return result[0]['generated_text']

if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("""
    <div style="text-align:center; margin-top:200px;">
        <h1 style="color:#3b82f6;">AI Support Assistant</h1>
        <p style="color:#555;">Starting your assistant...</p>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(1.5)
    st.session_state.loaded = True
    st.rerun()
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #fdfbfb, #ebedee, #e0f7fa, #fce7f3);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}
.main, .block-container {background: transparent !important;}
.title {text-align:center;font-size:42px;font-weight:bold;color:#2563eb;}
.chat-box {max-width:700px;margin:auto;}
.msg-user {background:#3b82f6;color:white;padding:12px;border-radius:20px;margin:10px;text-align:right;}
.msg-bot {background:#f3f4f6;color:#111;padding:12px;border-radius:20px;margin:10px;}
</style>
""", unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = []
st.markdown('<div class="title">AI-Based Customer Query Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user"> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot"> {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
user_input = st.chat_input("Ask your query...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    time.sleep(1)
    if is_greeting(user_input):
        category = "General"
        sentiment = "🙂 Neutral"
        reply = "Hello! How can I assist you today? 😊"

    elif not is_valid_query(user_input):
        category = "Unknown"
        sentiment = "🙂 Neutral"
        reply = "I can help with orders, delivery, and product issues. Please ask related queries 😊"

    else:
        category = predict_category(user_input)
        sentiment = detect_sentiment(user_input)
        reply = generate_response(user_input, category, sentiment)

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{reply}\n\n📌 {category} |  {sentiment}"
    })

    st.rerun()

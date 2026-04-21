import streamlit as st
import pickle
import re
import time
import requests
import os
st.set_page_config(page_title="AI Customer Support", layout="centered")
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
headers = {
    "Authorization": f"Bearer {os.getenv('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')}"
}

def query_huggingface(prompt):
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        return response.json()
    except:
        return None
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

.main, .block-container {
    background: transparent !important;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #2563eb;
}

.hero {
    text-align: center;
    color: #444;
}

.chat-box {
    max-width: 700px;
    margin: auto;
}

.msg-user {
    background: #3b82f6;
    color: white;
    padding: 12px;
    border-radius: 20px 20px 5px 20px;
    margin: 10px 0;
    text-align: right;
}

.msg-bot {
    background: #f3f4f6;
    color: #111;
    padding: 12px;
    border-radius: 20px 20px 20px 5px;
    margin: 10px 0;
}

.typing span {
    height: 8px;
    width: 8px;
    margin: 0 2px;
    background-color: #3b82f6;
    border-radius: 50%;
    display: inline-block;
    animation: blink 1.4s infinite both;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
    0% {opacity: 0.2;}
    20% {opacity: 1;}
    100% {opacity: 0.2;}
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
</style>
""", unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    model = pickle.load(open("model.pkl", "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
    st.session_state.model = model
    st.session_state.vectorizer = vectorizer
else:
    model = st.session_state.model
    vectorizer = st.session_state.vectorizer
def predict_category(text):
    X = vectorizer.transform([text.lower()])
    return model.predict(X)[0]
def detect_sentiment(text):
    prompt = f"""
    Analyze sentiment as Positive, Negative, or Neutral.

    Text: {text}
    Sentiment:
    """
    result = query_huggingface(prompt)

    try:
        output = result[0]['generated_text']
    except:
        return "🙂 Neutral"

    if "Positive" in output:
        return "😊 Positive"
    elif "Negative" in output:
        return "😡 Negative"
    else:
        return "🙂 Neutral"
def generate_response(query, category, sentiment):
    prompt = f"""
    You are a helpful customer support assistant.

    User Query: {query}
    Category: {category}
    Sentiment: {sentiment}

    Give a polite and helpful response:
    """
    result = query_huggingface(prompt)

    try:
        return result[0]['generated_text']
    except:
        return "We’re here to help! Please try again."
st.markdown('<div class="title">AI-Based Customer Query Analyzer</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <h2>👋 Welcome!</h2>
        <p>I'm here to help you 😊</p>
        <p style="opacity:0.6;">Ask your issue below 👇</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot"> {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
user_input = st.chat_input("Ask your query...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    placeholder = st.empty()
    placeholder.markdown('<div class="typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
    time.sleep(1)

    category = predict_category(user_input)        # ML model
    sentiment = detect_sentiment(user_input)       # LLM
    reply = generate_response(user_input, category, sentiment)  # LLM

    placeholder.empty()

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{reply}\n\n📌 {category} | 💡 {sentiment}"
    })

    st.rerun()

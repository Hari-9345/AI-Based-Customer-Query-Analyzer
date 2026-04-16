import streamlit as st
import pickle
import re
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="AI Customer Support", layout="centered")

# ------------------ SPLASH ------------------
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

# ------------------ LOVABLE CSS ------------------
st.markdown("""
<style>

/* ANIMATED BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #fdfbfb, #ebedee, #e0f7fa, #fce7f3);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}

/* REMOVE DARK */
.main, .block-container {
    background: transparent !important;
}

/* REMOVE FLOATING BAR */
[data-testid="stChatFloatingInputContainer"] {
    background: transparent !important;
    box-shadow: none !important;
}

/* TITLE */
.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #2563eb;
}

/* HERO */
.hero {
    text-align: center;
    color: #444;
}

/* CHAT CONTAINER */
.chat-box {
    max-width: 700px;
    margin: auto;
}

/* USER BUBBLE */
.msg-user {
    background: #3b82f6;
    color: white;
    padding: 12px;
    border-radius: 20px 20px 5px 20px;
    margin: 10px 0;
    text-align: right;
}

/* BOT BUBBLE */
.msg-bot {
    background: #f3f4f6;
    color: #111;
    padding: 12px;
    border-radius: 20px 20px 20px 5px;
    margin: 10px 0;
}

/* INPUT */
[data-testid="stChatInput"] {
    background: #ffffff !important;
    color: #111 !important;
    border-radius: 30px !important;
    padding: 12px !important;
    border: 2px solid #e5e7eb !important;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
    max-width: 700px;
    margin: auto;
}

/* TYPING DOTS */
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

# ------------------ SESSION ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ LOAD MODEL ------------------
if "model" not in st.session_state:
    model = pickle.load(open("model.pkl", "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
    st.session_state.model = model
    st.session_state.vectorizer = vectorizer
else:
    model = st.session_state.model
    vectorizer = st.session_state.vectorizer

# ------------------ FUNCTIONS ------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def predict_category(text):
    X = vectorizer.transform([clean_text(text)])
    return model.predict(X)[0]

def detect_sentiment(text):
    t = text.lower()

    negative_words = [
        "not", "no", "never", "failed", "error",
        "problem", "issue", "wrong", "delay",
        "didn't", "did not", "missing", "lost"
    ]

    positive_words = [
        "thanks", "thank you", "good", "great",
        "resolved", "working", "fine"
    ]

    if any(word in t for word in negative_words):
        return "😡 Negative"
    elif any(word in t for word in positive_words):
        return "😊 Positive"
    else:
        return "🙂 Neutral"

def generate_response(query, category):
    responses = {
        "Login Issues and Error Messages":
            "We’re sorry you're facing trouble logging in 💙 Try resetting your password.",
        "Order Delivery Issues":
            "We understand the delay 😔 Please check tracking or contact support.",
        "Return and Exchange":
            "You can return or exchange easily from your orders 😊",
        "Invoice and Payment":
            "Download your invoice from your orders page."
    }
    return responses.get(category, "We’re here to help! Please share more details 💙")

# ------------------ TITLE ------------------
st.markdown('<div class="title">AI-Based Customer Query Analyzer</div>', unsafe_allow_html=True)

# ------------------ HERO ------------------
if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <h2>👋 Welcome!</h2>
        <p>I'm here to help you 😊</p>
        <p style="opacity:0.6;">Ask your issue below 👇</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------ CHAT ------------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ INPUT ------------------
user_input = st.chat_input("Ask your query...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # typing animation
    placeholder = st.empty()
    placeholder.markdown('<div class="typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
    time.sleep(1)

    category = predict_category(user_input)
    sentiment = detect_sentiment(user_input)
    reply = generate_response(user_input, category)

    placeholder.empty()

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{reply}\n\n📌 {category} | 💡 {sentiment}"
    })

    st.rerun()
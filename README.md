#AI-Based-Customer-Query-Analyzer 

This project is a simple AI-based customer support system that I built as part of my final year project. The goal was to create a chatbot that can understand customer queries, classify them, and provide appropriate responses automatically.

---

##  About the Project

In real-world applications, companies receive a large number of customer queries every day. Handling all of them manually can be time-consuming.

So, I developed this system to:

* Automatically identify the type of customer query
* Understand whether the user is happy or facing an issue
* Provide a suitable response instantly

The system is designed mainly for **e-commerce support scenarios** like login issues, order problems, refunds, etc.

---

##  Features

* Classifies customer queries into categories like:

  * Login Issues
  * Order Delivery Problems
  * Returns & Exchanges
  * Payment / Invoice

* Detects sentiment:

  * Positive 😊
  * Neutral 🙂
  * Negative 😡

* Generates simple and helpful responses

* Clean and interactive UI using Streamlit

---

##  Technologies Used

* Python
* Scikit-learn (SVM model)
* Streamlit
* Pandas & NumPy

---

## ⚙️ How to Run the Project

1. Install the required libraries:

```
pip install -r requirements.txt
```

2. Run the application:

```
streamlit run app.py
```

3. Open the browser and start chatting with the bot.

---

##  Example

**Input:**
I am not able to login to my account

**Output:**
Category: Login Issues
Sentiment: Negative
Response: Please try resetting your password or verifying your account.

---

##  How It Works

* The input text is cleaned and processed
* A trained machine learning model predicts the category
* A rule-based approach is used for sentiment detection
* Based on the category, a predefined response is generated

---

##  Limitations

* Sentiment analysis is rule-based (not fully AI-driven)
* Works best for English queries
* May not handle completely unrelated inputs perfectly

---

##  Future Improvements

* Add support for multiple languages (like Tamil)
* Use advanced NLP models for better accuracy
* Integrate voice input and voice response
* Deploy as a web application

---

  Author

Harihara Suthan G
Karthikeyan K

---

 Note

This project is built for learning and demonstration purposes.

---

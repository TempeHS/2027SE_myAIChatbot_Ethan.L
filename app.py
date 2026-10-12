from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer

app = Flask(__name__)

chatbot = ChatBot(
    "StudentBot",  # name of the chatbot
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///chatbot_database.sqlite3",
)

trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")
list_trainer = ListTrainer(chatbot)

# Train on school-related conversations
list_trainer.train(
    [
        "What subjects do you like?",
        "I find all subjects interesting, but I really enjoy helping with coding!",
        "Can you help with homework?",
        "I can try to help explain concepts, but you should do your own work!",
        "Who made you?",
        "I was created by a talented Year 9 student at Tempe High School!",
    ]
)

# Train on greetings
list_trainer.train(
    [
        "Good morning!",
        "Good morning! How can I help you today?",
        "Good afternoon!",
        "Good afternoon! What would you like to chat about?",
    ]
)


@app.route("/")
def home():
    """this is serve as the main chat page"""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages and return bot responses."""
    # Get the message from the request
    data = request.get_json()
    user_message = data.get("message", "")

    # Basic input validation
    if not user_message:
        return jsonify({"respond": "Please enter a message"})

    if len(user_message) > 500:
        return jsonify(
            {"respond": "Message too long! Please keep it under 500 characters."}
        )

    if check_for_crisis(user_message):
        return jsonify({"respond": CRISIS_RESPOND})

    # Get the chatbot's response
    bot_respond = chatbot.get_response(user_message)
    return jsonify({"response": str(bot_respond)})


CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "self harm",
    "dont want to live",
    "don't want to live",
    "want to die",
]

CRISIS_RESPOND = """I am concerned about what you've shared. Please know that you're not alone. 
If you're in crisis, please reach out for support:

- Lifeline: 13 11 14 (24/7)
- Kids Helpline: 1800 55 1800
- Beyond Blue: 1300 22 4636

I'm just a chatbot and can't provide the support you need, but these services have trained conselors ready to help right now. """


def check_for_crisis(message):
    """Check if message contains crisis keywords."""
    message_lower = message.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            return True
        return False


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

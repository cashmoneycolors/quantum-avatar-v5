from flask import Flask, request, jsonify
from quantum_avatar.nlp.chat import ChatBot
from quantum_avatar.vision.image_generator import ImageGenerator
from quantum_avatar.business.business_logic import BusinessLogic
from quantum_avatar.autonomy.autonomous_executor import AutonomousExecutor

app = Flask(__name__)

chatbot = ChatBot()
image_gen = ImageGenerator()
business = BusinessLogic()
executor = AutonomousExecutor()


@app.route("/")
def home():
    return "Willkommen beim Quantum-Avatar!"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    response = chatbot.respond(message)
    return jsonify({"response": response})


@app.route("/generate_image", methods=["POST"])
def generate_image():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "Default image")
    # In reality, generate and return image path or base64
    image_gen.generate_image(prompt)
    return jsonify({"image": "Generated"})


@app.route("/earn_points", methods=["POST"])
def earn_points():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "default")
    action = data.get("action", "purchase")
    result = business.virtual_earnings(user_id, action)
    return jsonify(result)


@app.route("/autonomous_action", methods=["POST"])
def autonomous_action():
    data = request.get_json(silent=True) or {}
    state = data.get("state", {})
    action = executor.autonomous_decision(state)
    return jsonify({"action": action})


if __name__ == "__main__":
    app.run(debug=True)

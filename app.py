import random
from flask import Flask, request, jsonify
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import torch
import json

# Load the intents and model
with open('intents.json', 'r') as f:
    intents = json.load(f)

# Load model data
FILE = "data.pth"
data = torch.load(FILE)
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# Initialize Flask app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Tokenize and prepare input
    sentence = tokenize(message)
    X = bag_of_words(sentence, all_words)
    X = torch.from_numpy(X).float().unsqueeze(0).to(device)

    # Get model output
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    # Find response from intents
    response = None
    for intent in intents['intents']:
        if tag == intent["tag"]:
            response = random.choice(intent["responses"])

    # If no response found, fallback
    if not response:
        response = "I'm not sure I understand that."

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

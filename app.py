from flask import Flask, render_template, request, jsonify
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('user_input')
    
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Salesperson: {user_input}\n\niObject:",
        temperature=0.9,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6
    )

    response_text = response.choices[0].text.strip().replace("Salesperson", "iObject")

    return jsonify(response_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

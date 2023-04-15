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
    
    # Your OpenAI API code here
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"User question: {user_input}\n\niObject:",
        temperature=0.9,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6
    )

    return jsonify(response.choices[0].text.strip())

if __name__ == '__main__':
    app.run(debug=True)

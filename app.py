import re
from flask import Flask, render_template, request, jsonify
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

objections = {
    "We're using your competitor": "And how are you finding them? If you don’t mind me asking, why did you choose to go with them?",
    "Your product is too expensive": "Cost is an important consideration but I believe we can actually save you money. Can we set up a time for me to explain how?",
    "I don't see any ROI potential": "There’s definitely potential. I’d love to show you and explain how. Are you available this week for a more detailed call?",
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('user_input')

    prompt = f"A prospective client mentioned, \"{user_input}\" How would you address this concern?\n\nSales Sensei:"

    response = openai.Completion.create(
        model="davinci:ft-personal-2023-04-17-22-02-12",
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=2,
        presence_penalty=2,
        stop=["END", "A prospective client mentioned"]
    )

    response_text = response.choices[0].text.strip()
    response_text = re.search(r'(.*[.!?])', response_text).group(0)  # Extract the response up to the last complete sentence

    return jsonify(response_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
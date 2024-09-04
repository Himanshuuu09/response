from flask import Flask, request, jsonify
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
from flask_cors import CORS
import asyncio

load_dotenv()

app = Flask(__name__)
CORS(app)

# Set your Google AI API key
genai.configure(api_key=os.environ.get("GOOGLE_AI_API_KEY"))

# Set up cache

# Compile regex patterns once
tf_pattern = re.compile(r'"thought_process":\s*"([^"]+)"')
def generate_response(question, answer, emotions):
    prompt = f"""
Analyze the following information to determine the candidate's thought process for selecting the given answer. The analysis should consider the candidate's emotional state.

- Question: {question}
- Given Answer: {answer}
- Candidate's Emotions: {emotions}

Provide the reasoning behind why the candidate selected the answer. Format the response as JSON under the heading "thought_process" with the following structure:

{{
  "thought_process": ""
}}
"""
    pattern = tf_pattern
    model = genai.GenerativeModel(model_name="gemini-pro")
    response = model.generate_content(prompt)
    generated_text = response.text
    # Print or log the response to inspect its structure
    # print(generated_text)  # Or use logging if necessary
    matches = pattern.findall(generated_text)
    print(generated_text)
    print(matches)
    mcq_data = []
    mcq_data.append({
                "reason": matches,
            })

    
    return mcq_data

async def process_questions(data):

    question = data.get("question", "")
    answer = data.get("answer", "")
    emotions = data.get("emotions", "")
    if not all([question,answer,emotions]):
        return {"error": "Missing data"}, 400
    else:
        mcq_data = generate_response(question,answer,emotions)
        return {"result": mcq_data, "message": "all questions", "success": True}, 200


@app.route("/response", methods=["POST"])
def generate_question_endpoint():
    """API endpoint to generate questions and answers."""
    data = request.json
    print("workingg")
    response, status_code = asyncio.run(process_questions(data))
    return jsonify(response), status_code

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)

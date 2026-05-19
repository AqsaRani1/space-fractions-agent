app.py
```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
import random

app = Flask(__name__)
CORS(app)

# PostgreSQL connection details
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'space_fractions')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')

# Sample questions to use if the database is empty
SAMPLE_QUESTIONS = [
    {
        "id": 1,
        "question": "What is 1/4 + 1/4?",
        "answer_options": ["1/2", "2/4", "1/8", "3/4"],
        "correct_answer": "1/2"
    },
    {
        "id": 2,
        "question": "What is 3/4 - 1/4?",
        "answer_options": ["1/4", "1/2", "2/4", "3/4"],
        "correct_answer": "1/2"
    },
    # Add more sample questions as needed
]

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns 200 OK if the app is running.
    """
    return jsonify({'status': 'OK'}), 200

@app.route('/api/questions', methods=['GET'])
def get_all_questions():
    """
    Retrieves all questions from the database.
    Returns the questions as a JSON array.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute("SELECT id, question, answer_options, correct_answer FROM questions")
        questions = [
            {
                "id": row[0],
                "question": row[1],
                "answer_options": row[2],
                "correct_answer": row[3]
            } for row in cur.fetchall()
        ]
        cur.close()
        conn.close()
        return jsonify(questions)
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/random', methods=['GET'])
def get_random_question():
    """
    Retrieves a random question from the database.
    Returns the question and its answer options as JSON.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute("SELECT id, question, answer_options, correct_answer FROM questions ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        if row:
            question = {
                "id": row[0],
                "question": row[1],
                "answer_options": row[2],
                "correct_answer": row[3]
            }
            cur.close()
            conn.close()
            return jsonify(question)
        else:
            # If the database is empty, use the sample questions
            random_question = random.choice(SAMPLE_QUESTIONS)
            return jsonify(random_question)
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/<int:id>/check', methods=['POST'])
def check_answer(id):
    """
    Checks if the provided answer is correct for the question with the given ID.
    Expects a JSON body with the "answer" field.
    Returns a JSON object with the "is_correct" and "correct_answer" fields.
    """
    try:
        answer = request.json.get('answer')
        if not answer:
            return jsonify({'error': 'No answer provided'}), 400

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute("SELECT correct_answer FROM questions WHERE id = %s", (id,))
        row = cur.fetchone()
        if row:
            correct_answer = row[0]
            is_correct = answer.strip() == correct_answer.strip()
            result = {
                "is_correct": is_correct,
                "correct_answer": correct_answer
            }
            cur.close()
            conn.close()
            return jsonify(result)
        else:
            return jsonify({'error': f'Question with ID {id} not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions', methods=['POST'])
def add_question():
    """
    Adds a new question to the database.
    Expects a JSON body with the "question", "answer_options", and "correct_answer" fields.
    Returns the newly created question as JSON.
    """
    try:
        question = request.json.get('question')
        answer_options = request.json.get('answer_options')
        correct_answer = request.json.get('correct_answer')

        if not question or not answer_options or not correct_answer:
            return jsonify({'error': 'Missing required fields'}), 400

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO questions (question, answer_options, correct_answer) VALUES (%s, %s, %s) RETURNING id", (question, answer_options, correct_answer))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "id": new_id,
            "question": question,
            "answer_options": answer_options,
            "correct_answer": correct_answer
        }), 201
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```
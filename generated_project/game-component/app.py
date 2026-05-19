Here is a complete Python Flask app for the GameComponent of Space Fractions:

```python
from flask import Flask, jsonify, request
import psycopg2
import redis
import requests
import jwt
from functools import wraps

app = Flask(__name__)
app.config.from_object('config')

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host=app.config['DB_HOST'],
    database=app.config['DB_NAME'],
    user=app.config['DB_USER'],
    password=app.config['DB_PASSWORD']
)

# Connect to Redis cache
r = redis.Redis(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    db=app.config['REDIS_DB']
)

# JWT token verification middleware
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'a valid token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'token is invalid'}), 401

        return f(*args, **kwargs)
    
    return decorator

# GET /health
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status":"healthy","service":"GameComponent"})

# GET /api/play
@app.route('/api/play', methods=['GET'])
@token_required
def play():
    try:
        # Create new game in DB
        cur = conn.cursor()
        cur.execute("INSERT INTO games (score) VALUES (0) RETURNING id")
        game_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        # Get first question from QuestionComponent
        response = requests.get('http://localhost:3001/api/question')
        question = response.json()

        return jsonify({
            'gameId': game_id,
            'question': question
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST /api/answer
@app.route('/api/answer', methods=['POST'])
@token_required
def answer():
    try:
        data = request.get_json()
        game_id = data['gameId']
        question_id = data['questionId']
        player_answer = data['answer']

        # Check answer via QuestionComponent
        response = requests.post('http://localhost:3001/api/answer', json={
            'questionId': question_id,
            'answer': player_answer
        })
        result = response.json()

        # Update score in Redis and DB
        score = r.get(f'game:{game_id}:score')
        if score:
            score = int(score)
        else:
            cur = conn.cursor()
            cur.execute("SELECT score FROM games WHERE id = %s", (game_id,))
            score = cur.fetchone()[0]
            conn.commit()
            cur.close()

        score += result['score']
        r.set(f'game:{game_id}:score', score)

        cur = conn.cursor()
        cur.execute("UPDATE games SET score = %s WHERE id = %s", (score, game_id))
        conn.commit()
        cur.close()

        # Get next question from QuestionComponent
        response = requests.get(f'http://localhost:3001/api/question/{result["nextQuestionId"]}')
        next_question = response.json()

        return jsonify({
            'result': result['result'],
            'score': score,
            'nextQuestion': next_question
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET /api/score
@app.route('/api/score', methods=['GET'])
@token_required
def get_score():
    try:
        game_id = request.args.get('gameId')
        
        # Get score from Redis
        score = r.get(f'game:{game_id}:score')
        if score:
            return jsonify({'score': int(score)})
        
        # Get score from DB
        cur = conn.cursor()
        cur.execute("SELECT score FROM games WHERE id = %s", (game_id,))
        row = cur.fetchone()
        if row:
            score = row[0]
            r.set(f'game:{game_id}:score', score)
            return jsonify({'score': score})
        else:
            return jsonify({'error': 'Game not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
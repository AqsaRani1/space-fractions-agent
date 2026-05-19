```python
import json
from unittest.mock import patch
from flask.testing import FlaskClient

def test_health_check(client: FlaskClient):
    """
    Test that the health check endpoint returns a 200 status code.
    """
    response = client.get('/health')
    assert response.status_code == 200

def test_start_game(client: FlaskClient):
    """
    Test that the start game endpoint returns a gameId and a question.
    """
    with patch('app.GameComponent.start_game') as mock_start_game:
        mock_start_game.return_value = {'gameId': '1234', 'question': 'What is 1/2 + 1/4?'}
        response = client.post('/start')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'gameId' in data
        assert 'question' in data

def test_correct_answer(client: FlaskClient):
    """
    Test that a correct answer increases the score.
    """
    with patch('app.GameComponent.check_answer') as mock_check_answer:
        mock_check_answer.return_value = {'score': 10}
        response = client.post('/answer', json={'gameId': '1234', 'answer': '3/4'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert data['score'] == 10

def test_wrong_answer(client: FlaskClient):
    """
    Test that a wrong answer keeps the score the same.
    """
    with patch('app.GameComponent.check_answer') as mock_check_answer:
        mock_check_answer.return_value = {'score': 0}
        response = client.post('/answer', json={'gameId': '1234', 'answer': '1/2'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert data['score'] == 0

def test_get_score(client: FlaskClient):
    """
    Test that the get score endpoint returns the correct score.
    """
    with patch('app.GameComponent.get_score') as mock_get_score:
        mock_get_score.return_value = {'score': 10}
        response = client.get('/score/1234')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert data['score'] == 10

def test_invalid_game_id(client: FlaskClient):
    """
    Test that an invalid gameId returns a 404 error.
    """
    with patch('app.GameComponent.check_answer') as mock_check_answer:
        mock_check_answer.return_value = {'error': 'Invalid gameId'}
        response = client.post('/answer', json={'gameId': 'invalid', 'answer': '3/4'})
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

def test_missing_fields(client: FlaskClient):
    """
    Test that missing required fields returns a 400 error.
    """
    response = client.post('/answer', json={'answer': '3/4'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
```
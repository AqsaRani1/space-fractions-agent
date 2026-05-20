const express = require('express');
const axios = require('axios');
const { Client } = require('pg');
const redis = require('redis');

const app = express();
app.use(express.json());

// Connect to PostgreSQL
const pgClient = new Client({
  connectionString: 'postgres://user:password@localhost:5432/mydb'
});
pgClient.connect();

// Connect to Redis
const redisClient = redis.createClient({
  host: 'localhost',
  port: 6379
});
redisClient.on('error', (err) => console.log('Redis Client Error', err));
redisClient.connect();

// # FR-1: Play game
app.post('/play', async (req, res) => {
  try {
    // Authenticate and authorize user
    const authUser = await axios.post('/users/authenticate', req.body.credentials);

    // Retrieve a question
    const question = await axios.get('/questions/random');

    // Process user's answer
    const isCorrect = await processAnswer(authUser.id, question.id, req.body.answer);

    // Save game state
    await pgClient.query('INSERT INTO games (user_id, question_id, correct) VALUES ($1, $2, $3)', [authUser.id, question.id, isCorrect]);

    res.status(200).json({ question, isCorrect });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'An error occurred while playing the game' });
  }
});

async function processAnswer(userId, questionId, answer) {
  // # NFR-1: Performance
  const cachedAnswer = await redisClient.get(`question:${questionId}:answer`);
  if (cachedAnswer) {
    return answer === cachedAnswer;
  }

  // Retrieve the correct answer from the QuestionComponent
  const { data: question } = await axios.get(`/questions/${questionId}`);
  const isCorrect = answer === question.answer;

  // Cache the correct answer
  await redisClient.set(`question:${questionId}:answer`, question.answer, 'EX', 3600);

  return isCorrect;
}

app.listen(3000, () => {
  console.log('GameComponent server started on port 3000');
});
const express = require('express');
const axios = require('axios');

const app = express();

// FR-1: Play game
app.get('/play', async (req, res) => {
  try {
    // Get question from QuestionComponent
    const question = await axios.get('http://question-component/api/question');

    // Authenticate and authorize user via UserComponent
    const user = await axios.get('http://user-component/api/user', {
      headers: {
        Authorization: req.headers.authorization,
      },
    });

    // Process game logic
    const result = await processGameLogic(question, user);

    res.json(result);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// NFR-1: Performance
async function processGameLogic(question, user) {
  // Implement game logic
  const answer = await calculateFractionAnswer(question, user);
  return { question, answer };
}

async function calculateFractionAnswer(question, user) {
  // Implement fraction calculation logic
  return 0.5;
}

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`GameComponent service running on port ${port}`);
});
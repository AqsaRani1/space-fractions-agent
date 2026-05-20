const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const app = express();
app.use(express.json());

// Users data store
const users = [];

// User authentication
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  // Find user
  const user = users.find(u => u.username === username);
  if (!user) {
    return res.status(401).json({ error: 'Invalid username or password' });
  }

  // Verify password
  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    return res.status(401).json({ error: 'Invalid username or password' });
  }

  // Generate JWT token
  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
  res.json({ token });
});

app.post('/register', async (req, res) => {
  const { username, password } = req.body;

  // Check if user already exists
  if (users.some(u => u.username === username)) {
    return res.status(400).json({ error: 'Username already registered' });
  }

  // Hash password
  const passwordHash = await bcrypt.hash(password, 10);

  // Create new user
  const newUser = { id: users.length + 1, username, passwordHash };
  users.push(newUser);

  res.status(201).json(newUser);
});

// Middleware to authenticate user
const authenticate = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = users.find(u => u.id === decoded.userId);
    next();
  } catch (err) {
    return res.status(403).json({ error: 'Invalid token' });
  }
};

// Authorize user
app.get('/profile', authenticate, (req, res) => {
  res.json(req.user);
});

module.exports = app;
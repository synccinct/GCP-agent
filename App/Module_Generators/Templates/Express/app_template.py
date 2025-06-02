EXPRESS_TEMPLATE = """
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'API is running' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

module.exports = app;
"""

EXPRESS_AUTH_MIDDLEWARE_TEMPLATE = """
const jwt = require('jsonwebtoken');

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

module.exports = { authenticateToken };
"""

EXPRESS_ROUTES_TEMPLATE = """
const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');

// Public routes
router.post('/auth/login', async (req, res) => {
  try {
    // Login logic here
    res.json({ message: 'Login successful' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Protected routes
router.get('/users', authenticateToken, async (req, res) => {
  try {
    // Get users logic here
    res.json({ users: [] });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/users', authenticateToken, async (req, res) => {
  try {
    // Create user logic here
    res.json({ message: 'User created successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
"""

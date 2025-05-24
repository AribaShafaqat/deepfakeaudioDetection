const express = require('express');
const authenticateToken = require('../middlewares/middleware'); // Import the middleware
const router = express.Router();

// Protected route - Only accessible with a valid JWT token
router.get('/profile', authenticateToken, (req, res) => {
    res.json({ message: 'Welcome to your profile', user: req.user });
});

module.exports = router;

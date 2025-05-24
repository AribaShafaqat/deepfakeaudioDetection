const jwt = require('jsonwebtoken');
require('dotenv').config(); // to load variables from .env

// Middleware to check if user is authenticated
const authenticateToken = (req, res, next) => {
    // Get the token from request header
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (!token) {
        return res.status(401).json({ message: 'No token, authorization denied' });
    }

    // Verify the token
    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ message: 'Token is not valid' });
        }

        req.user = user;
        next(); // move to the next middleware/route handler
    });
};

module.exports = authenticateToken;

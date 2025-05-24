const express = require('express');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const jwt = require('jsonwebtoken');
const connectDB = require('../db'); // Adjust the path as needed
require('dotenv').config();
const router = express.Router();

// Google OAuth Configuration
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: 'http://localhost:5000/auth/google/callback'

}, async (token, tokenSecret, profile, done) => {
  const { id, displayName, emails } = profile;
  const email = emails[0].value;

  try {
    const db = await connectDB();
    const [users] = await db.execute('SELECT * FROM users WHERE email = ?', [email]);

    if (users.length === 0) {
      // If the user doesn't exist, create a new record
      await db.execute('INSERT INTO users (name, email, is_verified) VALUES (?, ?, 1)', [displayName, email]);
    }

    await db.end();
    return done(null, profile); // This will serialize the user
  } catch (err) {
    console.error(err);
    return done(err);
  }
}));

// Serialize and deserialize user (for session management)
passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((user, done) => done(null, user));

// Google Auth route
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// Google callback route
router.get('/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    // Successful authentication
    const user = req.user;
    const token = jwt.sign(
      { id: user.id, email: user.emails[0].value },
      process.env.JWT_SECRET, { expiresIn: '1h' }
    );
    res.status(200).json({ message: 'Logged in successfully with Google', token });
  }
);
// Google callback route
router.get('/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    res.redirect('http://localhost:5000/home.html'); // 🔁 REDIRECT TO FRONTEND PAGE
  }
);

module.exports = router;

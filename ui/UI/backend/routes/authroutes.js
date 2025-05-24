const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const connectDB = require('../db');
const { sendOTP } = require('../utils/mfa');

router.post('/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) {
    return res.status(400).json({ message: 'All fields are required.' });
  }

 

  try {
    const db = await connectDB();
    const [existing] = await db.execute('SELECT * FROM users WHERE email = ?', [email]);
    if (existing.length > 0) {
      await db.end();
      return res.status(400).json({ message: 'Email already in use.' });
    }

    const hashed = await bcrypt.hash(password, 10);

    // Generate OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString(); // Generate OTP (6 digits)

    // Insert user into the database, including OTP and is_verified set to 0
    const result = await db.execute(
      'INSERT INTO users (name, email, password, is_verified, otp) VALUES (?, ?, ?, ?, ?)',
      [name, email, hashed, 0, otp]
    );
    await db.end();

    // Send OTP via email (assuming sendOTP function works properly)
    await sendOTP(email, otp);
    console.log(`Generated OTP for ${email}: ${otp}`);

    res.status(201).json({ message: 'User registered. Check your email for the OTP.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error.' });
  }
});
// 🔓 Login route
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password required.' });
  }

  try {
    const db = await connectDB();
    const [users] = await db.execute('SELECT * FROM users WHERE email = ?', [email]);
    if (users.length === 0) {
      await db.end();
      return res.status(400).json({ message: 'Invalid credentials.' });
    }

    const user = users[0];
    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      await db.end();
      return res.status(400).json({ message: 'Invalid credentials.' });
    }

    if (user.is_verified === 0) {
      await db.end();
      return res.status(403).json({ message: 'OTP verification required.' });
    }

    const token = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET, { expiresIn: '1h' });
    await db.end();
    res.status(200).json({ message: 'Login successful.', token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error.' });
  }
});
// 🔓 OTP verification route
// 
const jwtSecret = process.env.JWT_SECRET ; // Use environment variable in real apps

router.post('/verify-otp', async (req, res) => {
  const { email, otp } = req.body;
  if (!email || !otp) {
    return res.status(400).json({ message: 'Email and OTP are required.' });
  }

  try {
    const db = await connectDB();
    const [users] = await db.execute('SELECT * FROM users WHERE email = ?', [email]);
    if (users.length === 0) {
      await db.end();
      return res.status(404).json({ message: 'User not found.' });
    }

    const user = users[0];
    if (user.is_verified === 1) {
      // ⚠️ Already verified: Return a token anyway
      const token = jwt.sign({ id: user.id, email: user.email }, jwtSecret, { expiresIn: '1h' });
      await db.end();
      return res.status(200).json({ message: 'Already verified.', token });
    }

    if (user.otp !== otp) {
      await db.end();
      return res.status(400).json({ message: 'Invalid OTP.' });
    }

    // ✅ Mark as verified and clear OTP
    await db.execute(
      'UPDATE users SET is_verified = 1, otp = NULL WHERE email = ?',
      [email]
    );

    // ✅ Generate token
    const token = jwt.sign({ id: user.id, email: user.email }, jwtSecret, { expiresIn: '1h' });
    await db.end();

    res.status(200).json({ message: 'OTP verified successfully.', token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error.' });
  }
});


const verifyToken = require('../middlewares/verifyToken'); // make sure this middleware exists

router.get('/me', verifyToken, async (req, res) => {
  try {
    const db = await connectDB();
    const [rows] = await db.execute('SELECT id, name, email FROM users WHERE id = ?', [req.user.id]);
    await db.end();

    if (rows.length === 0) {
      return res.status(404).json({ message: 'User not found.' });
    }

    res.status(200).json(rows[0]);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;


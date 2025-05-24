const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const dotenv = require('dotenv');
dotenv.config();
require('dotenv').config();
console.log('Loaded email:', process.env.EMAIL_USER);
require('dotenv').config();
const connectDB = require('./db');



// Initialize express app
const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());


// Import routes
const authRoutes = require('./routes/authroutes');

// Setup Routes
app.use('/auth', authRoutes);
app.use('/api/auth', authRoutes);


// ✅ API route to fetch users
app.get('/api/users', async (req, res) => {
  try {
    console.log('Attempting to connect to DB...');
    const conn = await connectDB();
    console.log('Connected, executing query...');

    const [rows] = await conn.execute('SELECT name, email, is_verified FROM users');
    console.log('Query successful:', rows);

    res.json(rows);
  } catch (err) {
    console.error(' Error fetching users:', err.message);
    res.status(500).json({ error: 'Database error' });
  }
});
app.delete('/users/:email', async (req, res) => {
  try {
    const conn = await connectDB();
    const email = req.params.email;
    await conn.execute('DELETE FROM users WHERE email = ?', [email]);
    res.json({ success: true });
  } catch (err) {
    console.error('Error deleting user:', err);
    res.status(500).json({ error: 'Database error' });
  }
});
app.get('/api/user_count', async (req, res) => {
  try {
    const conn = await connectDB();
    const [rows] = await conn.execute('SELECT COUNT(*) as count FROM users');
    res.json({ count: rows[0].count });
  } catch (err) {
    console.error('Error fetching user count:', err.message);
    res.status(500).json({ error: 'Database error' });
  }
});

app.post('/insert-prediction', async (req, res) => {
  const { filename, result, date } = req.body;
  try {
    const connection = await connectDB();  // Connect to DB
    await connection.execute(
      'INSERT INTO predictions (filename, result, date) VALUES (?, ?, ?)',
      [filename, result, date]
    );
    res.status(200).send('Prediction inserted successfully');
  } catch (err) {
    console.error('Error inserting prediction:', err);
    res.status(500).send('Error inserting prediction');
  }
});
app.get('/api/predictions', async (req, res) => {
  try {
    const connection = await connectDB();
    const [rows] = await connection.execute('SELECT filename, result, date FROM predictions');
    console.log('Fetched predictions:', rows);
    res.json(rows);
  } catch (err) {
    console.error('Error fetching predictions:', err);
    res.status(500).send('Error fetching predictions');
  }
});



// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});


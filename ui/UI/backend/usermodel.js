const db = require('./db'); // Import your MySQL connection

// Function to find a user by email
const findUserByEmail = (email, callback) => {
    const query = 'SELECT * FROM users WHERE email = ?';
    db.query(query, [email], (err, result) => {
        if (err) {
            console.log('Error querying the database:', err);
            callback(err, null);
        } else {
            callback(null, result[0]); // Return the first result
        }
    });
};

// Function to create a new user
const createUser = (username, email, password, callback) => {
    const query = 'INSERT INTO users (username, email, password) VALUES (?, ?, ?)';
    db.query(query, [username, email, password], (err, result) => {
        if (err) {
            console.log('Error inserting user into database:', err);
            callback(err, null);
        } else {
            callback(null, result);
        }
    });
};

module.exports = {
    findUserByEmail,
    createUser
};

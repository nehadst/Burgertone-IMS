const express = require('express');
const mysql = require('mysql');
const dotenv = require('dotenv');
const app = express();

dotenv.config(); // Load environment variables

// Database Connection
const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

db.connect((err) => {
  if (err) {
    console.error('Database connection failed:', err);
    return;
  }
  console.log('Connected to the database.');
});

app.use(express.json()); // Middleware to parse JSON requests

// Basic route to confirm server setup
app.get('/', (req, res) => {
  res.send('BurgerTone Inventory System API');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

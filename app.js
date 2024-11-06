const mysql = require('mysql2');
const express = require('express');
const dotenv = require('dotenv');

dotenv.config();

// Validate required environment variables
const requiredEnvVars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME'];
for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
        console.error(`Missing required environment variable: ${envVar}`);
        process.exit(1);
    }
}

const app = express();

// Add basic middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Database configuration
const dbConfig = {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    port: process.env.DB_PORT ? parseInt(process.env.DB_PORT) : 3306,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
};

// Create connection pool
const pool = mysql.createPool(dbConfig);

// Enhance error logging
pool.getConnection((err, connection) => {
    if (err) {
        console.error('Failed to connect to database:', {
            errorCode: err.code,
            errorNumber: err.errno,
            errorMessage: err.message,
            errorStack: err.stack,
            sqlState: err.sqlState,
            fatal: err.fatal
        });
        
        // Common error codes
        switch(err.code) {
            case 'ER_ACCESS_DENIED_ERROR':
                console.error('Access denied - check username and password');
                break;
            case 'ECONNREFUSED':
                console.error('Connection refused - check if MySQL is running');
                break;
            case 'ER_BAD_DB_ERROR':
                console.error('Database does not exist');
                break;
        }
        process.exit(1);
    }
    console.log('Successfully connected to MySQL database!');
    connection.release();
    startServer();
});

// Start server
function startServer() {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
    });
}

// Handle application termination
process.on('SIGINT', async () => {
    try {
        await pool.end();
        console.log('Database pool closed.');
        process.exit(0);
    } catch (err) {
        console.error('Error closing pool:', err);
        process.exit(1);
    }
});

// Export pool for use in other modules
module.exports = {
    pool: pool.promise()
};

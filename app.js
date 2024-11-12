const express = require('express');
const dotenv = require('dotenv');
const { pool } = require('./db');  // Import pool from db.js

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

// Import route handlers
const ingredientRoutes = require('./routes/ingredients');
const menuRoutes = require('./routes/menuItems');
const reportRoutes = require('./routes/reports');

// Add CORS middleware
const cors = require('cors');
app.use(cors());

// Add routes
app.use('/api/ingredients', ingredientRoutes);
app.use('/api/menu', menuRoutes);
app.use('/api/reports', reportRoutes);

// Middleware to check inventory levels
app.use(async (req, res, next) => {
    try {
        const [lowStockItems] = await pool.query(`
            SELECT * FROM Ingredients 
            WHERE quantity <= threshold
        `);
        
        if (lowStockItems.length > 0) {
            wss.clients.forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify({
                        type: 'LOW_STOCK_ALERT',
                        items: lowStockItems
                    }));
                }
            });
        }
    } catch (error) {
        console.error('Error checking inventory levels:', error);
    }
    next();
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

startServer();

// works
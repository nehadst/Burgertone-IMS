const express = require('express');
const dotenv = require('dotenv');
const { pool } = require('./db');
const WebSocket = require('ws');
const cors = require('cors');

dotenv.config();

// Validate environment variables
const requiredEnvVars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME'];
for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
        console.error(`Missing required environment variable: ${envVar}`);
        process.exit(1);
    }
}

const app = express();

// Create single server instance
const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

// WebSocket setup
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    console.log('New client connected');
    ws.on('close', () => console.log('Client disconnected'));
  });

    


// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());

// Inventory check middleware - Place this before routes
app.use(async (req, res, next) => {
  console.log('Inventory check middleware executed');
  console.log('Request Method:', req.method);
  console.log('Request Path:', req.path);
  console.log('Original URL:', req.originalUrl);
    next(); // Proceed to the next middleware or route handler
  
    // After response is sent, check if inventory needs to send alerts
    if (req.method === 'PATCH' && req.path.startsWith('/api/ingredients')) {
      try {
        console.log('Checking low stock items...');
        const [lowStockItems] = await pool.query(`
          SELECT * FROM Ingredients 
          WHERE quantity <= threshold
        `);
        console.log('Low stock items:', lowStockItems);
        if (lowStockItems.length > 0) {
          console.log('Low stock items:', lowStockItems);
          wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(
                JSON.stringify({
                  type: 'LOW_STOCK_ALERT',
                  items: lowStockItems,
                })
              );
            }
          });
        } else {
          console.log('No low stock items. Sending clear alerts to clients.');
          // No low stock items, send clear alerts message
          wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(
                JSON.stringify({
                  type: 'CLEAR_ALERTS',
                })
              );
            }
          });
        }
      } catch (error) {
        console.error('Error checking inventory levels:', error);
      }
    }
  });



// Routes
const ingredientRoutes = require('./routes/ingredients');
const menuRoutes = require('./routes/menuItems');
const reportRoutes = require('./routes/reports');

app.use('/api/ingredients', ingredientRoutes);
app.use('/api/menu', menuRoutes);
app.use('/api/reports', reportRoutes);


// Cleanup
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
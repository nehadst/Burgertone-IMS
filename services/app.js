const express = require('express');
const dotenv = require('dotenv');
const { pool } = require('../db');
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

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());

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

// Inventory check middleware - Place this before routes



// Routes
const ingredientRoutes = require('./routes for js/ingredients');
const menuRoutes = require('./routes for js/menuItems');
const reportRoutes = require('./routes for js/reports');

app.use('/api/ingredients', ingredientRoutes);
app.use('/api/menu', menuRoutes);
app.use('/api/reports', reportRoutes);

app.use(async (req, res, next) => {
  try {
      const [lowStockItems] = await pool.query(`
          SELECT * FROM Ingredients 
          WHERE quantity <= threshold
      `);
      
      if (lowStockItems.length > 0) {
          wss.clients.forEach((client) => {
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

app.get('/test-alert', (req, res) => {
  wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({
              type: 'LOW_STOCK_ALERT',
              message: 'This is a test alert for low stock'
          }));
      }
  });
  res.send('Test alert sent to all clients');
});

setInterval(async () => {
  try {
      const [lowStockItems] = await pool.query(`
          SELECT * FROM Ingredients 
          WHERE quantity <= threshold
      `);

      if (lowStockItems.length > 0) {
          console.log('Low stock items detected:', lowStockItems);
          wss.clients.forEach((client) => {
              if (client.readyState === WebSocket.OPEN) {
                  console.log('Sending automatic low stock alert to client');
                  client.send(JSON.stringify({
                      type: 'LOW_STOCK_ALERT',
                      items: lowStockItems
                  }));
              }
          });
      }
  } catch (error) {
      console.error('Error in scheduled inventory check:', error);
  }
}, 6000);


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
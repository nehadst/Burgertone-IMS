
const express = require('express');
const router = express.Router();
const { pool } = require('../app');

// Get inventory usage report
router.get('/usage', async (req, res) => {
    try {
        const [rows] = await pool.query(`
            SELECT 
                i.name,
                i.unit,
                SUM(CASE WHEN it.change_by < 0 THEN ABS(it.change_by) ELSE 0 END) as usage_amount,
                DATE_FORMAT(it.timestamp, '%Y-%m-%d') as date
            FROM Inventory_Transactions it
            JOIN Ingredients i ON it.ingredient_id = i.id
            WHERE it.change_by < 0
            GROUP BY i.name, i.unit, DATE_FORMAT(it.timestamp, '%Y-%m-%d')
            ORDER BY date DESC
        `);
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get current stock levels
router.get('/stock-levels', async (req, res) => {
    try {
        const [rows] = await pool.query(`
            SELECT 
                name,
                quantity,
                threshold,
                unit,
                CASE 
                    WHEN quantity <= threshold THEN 'LOW'
                    WHEN quantity <= threshold * 1.5 THEN 'MEDIUM'
                    ELSE 'GOOD'
                END as stock_status
            FROM Ingredients
            ORDER BY 
                CASE 
                    WHEN quantity <= threshold THEN 1
                    WHEN quantity <= threshold * 1.5 THEN 2
                    ELSE 3
                END
        `);
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
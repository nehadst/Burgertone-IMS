
const express = require('express');
const router = express.Router();
const { pool } = require('../app');

// Get all menu items
router.get('/', async (req, res) => {
    try {
        const [rows] = await pool.query('SELECT * FROM Menu_Items');
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Add new menu item
router.post('/', async (req, res) => {
    const { name, combo } = req.body;
    try {
        const [result] = await pool.query(
            'INSERT INTO Menu_Items (name, combo) VALUES (?, ?)',
            [name, combo]
        );
        res.status(201).json({ id: result.insertId });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update menu item
router.put('/:id', async (req, res) => {
    const { name, combo } = req.body;
    try {
        await pool.query(
            'UPDATE Menu_Items SET name = ?, combo = ? WHERE id = ?',
            [name, combo, req.params.id]
        );
        res.json({ message: 'Updated successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Delete menu item
router.delete('/:id', async (req, res) => {
    try {
        await pool.query('DELETE FROM Menu_Items WHERE id = ?', [req.params.id]);
        res.json({ message: 'Deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
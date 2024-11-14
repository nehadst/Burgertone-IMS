
const express = require('express');
const router = express.Router();
const { pool } = require('../db');

// Get all ingredients
router.get('/', async (req, res) => {
    try {
        const [rows] = await pool.query('SELECT * FROM Ingredients');
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Add new ingredient
router.post('/', async (req, res) => {
    const { name, unit, quantity, threshold } = req.body;
    try {
        const [result] = await pool.query(
            'INSERT INTO Ingredients (name, unit, quantity, threshold) VALUES (?, ?, ?, ?)',
            [name, unit, quantity, threshold]
        );
        res.status(201).json({ id: result.insertId });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update ingredient quantity
router.patch('/:id', async (req, res) => {
    const { quantity } = req.body;
    const { id } = req.params;
    console.log(`Received PATCH request for ingredient ID ${id} with quantity ${quantity}`);

    try {
        await pool.query(
            'UPDATE Ingredients SET quantity = ? WHERE id = ?',
            [quantity, req.params.id]
        );
        res.json({ message: 'Updated successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Delete ingredient
router.delete('/:id', async (req, res) => {
    try {
        await pool.query('DELETE FROM Ingredients WHERE id = ?', [req.params.id]);
        res.json({ message: 'Deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
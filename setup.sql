-- Create the database
CREATE DATABASE IF NOT EXISTS burgertone_inventory;

-- Use the database
USE burgertone_inventory;

-- Create the inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    threshold DECIMAL(10, 2) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

- Insert sample data
INSERT INTO inventory (name, quantity, unit, threshold)
VALUES 
    (1, 'Beef Patty', 100, 'pcs', 20),
    (2, 'Cheddar Cheese', 50, 'lbs', 5),
    (3, 'Lettuce', 30, 'lbs', 10);
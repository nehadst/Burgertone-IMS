-- Create the database
CREATE DATABASE IF NOT EXISTS burgertone_inventory;

-- Use the database
USE burgertone_inventory;

-- Create the Ingredients table
CREATE TABLE IF NOT EXISTS Ingredients(
	id INT auto_increment PRIMARY KEY,
    NAME VARCHAR (255) NOT NULL,
    UNIT VARCHAR(255) NOT NULL,
    QUANTITY DECIMAL (10,2) NOT NULL,
    THRESHOLD DECIMAL (10,2) NOT NULL);

-- Insert sample data
INSERT INTO inventory (name, quantity, unit, threshold)
VALUES 
    (1, 'Beef Patty', 100, 'pcs', 20),
    (2, 'Cheddar Cheese', 50, 'lbs', 5),
    (3, 'Lettuce', 30, 'lbs', 10);
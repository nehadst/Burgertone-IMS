CREATE DATABASE IF NOT EXISTS burgertone_inventory;

USE burgertone_inventory;

-- Create base tables first (no foreign keys)
CREATE TABLE IF NOT EXISTS Ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL,
    UNIT VARCHAR(255) NOT NULL,
    QUANTITY DECIMAL(10,2) NOT NULL,
    THRESHOLD DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS Menu_Items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL,
    COMBO BOOLEAN
);

CREATE TABLE IF NOT EXISTS Sides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    default_side BOOLEAN DEFAULT FALSE
);

-- Then create tables with foreign keys (after their referenced tables exist)
CREATE TABLE IF NOT EXISTS Menu_Item_Ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    menu_item_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20),
    FOREIGN KEY (menu_item_id) REFERENCES Menu_Items(id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id)
);

CREATE TABLE IF NOT EXISTS Combo_Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    menu_item_id INT NOT NULL,
    side_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (menu_item_id) REFERENCES Menu_Items(id),
    FOREIGN KEY (side_id) REFERENCES Sides(id)
);

CREATE TABLE IF NOT EXISTS Inventory_Transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_id INT NOT NULL,
    change_by DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id)
);


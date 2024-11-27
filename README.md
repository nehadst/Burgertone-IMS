# Burgertone Inventory Management System (IMS)

Welcome to the **Burgertone Inventory Management System**, a robust and intelligent platform designed to streamline restaurant operations by integrating daily sales data, managing inventory, and enhancing decision-making processes. Built specifically for Burgertone, this system leverages modern technologies to improve efficiency, reduce waste, and ensure optimal stock levels for smooth operations.

---

## 🚀 Features

### 1. Data Integration
- **TouchBistro Integration**:
  - Automates data import from daily CSV exports using a custom Selenium web scraper.
  - Consolidates daily sales, inventory usage, and performance metrics into a unified database.
- **Real-time Updates**:
  - Ensures the latest data is always available for reporting and analysis.

### 2. Inventory Management
- **Stock Tracking**:
  - Monitors inventory levels and sends low-stock alerts.
- **Predictive Restocking**:
  - Uses AI-powered analytics to predict inventory needs based on sales trends, holidays, and historical data.
- **Ingredient Usage Monitoring**:
  - Tracks ingredient depletion based on daily sales.

### 3. Employee Scheduling (Planned for Future Updates)
- Optimizes staff schedules based on projected busy periods.
- Minimizes labor costs while maintaining efficient operations.

### 4. Reporting and Analytics
- **Interactive Dashboards**:
  - Provides insights into daily, weekly, and monthly sales trends using Chart.js.
- **Custom Reports**:
  - Exports inventory and sales reports for operational planning.
- **Shift Analysis**:
  - Evaluates employee productivity and peak working hours (future feature).

### 5. User-Friendly Interface
- **Admin Panel**:
  - Allows managers to manually upload CSV files, adjust inventory levels, and generate reports.
- **Secure Access**:
  - Implements role-based authentication for secure data handling.

---

## 🛠️ Technology Stack

### Frontend
- **React.js**: Interactive and responsive user interface.
- **Chart.js**: Real-time visualizations for inventory and sales data.

### Backend
- **Python (Flask)**: Backend logic and API development.
- **SQL**: Database for storing and managing inventory, sales, and employee data.

### Data Integration
- **Selenium**: Web scraper for automating TouchBistro data exports.
- **Pandas**: Data cleaning and transformation.

### Other Tools
- **TouchBistro POS**: Source of sales and inventory data.
- **Docker**: For containerization and easy deployment.

---

## 📊 Architecture

1. **Data Collection**:
   - Selenium scraper automates daily data exports from TouchBistro.
   - CSV files are parsed and transformed using Pandas.

2. **Data Storage**:
   - All data is stored in a SQL database, designed for efficient querying and reporting.

3. **User Interface**:
   - React.js frontend allows managers to view inventory levels, visualize trends, and manage operations.

4. **AI and Analytics**:
   - Predictive algorithms provide restocking suggestions and employee scheduling insights.

---

## 📖 Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Burgertone-IMS.git
cd Burgertone-IMS

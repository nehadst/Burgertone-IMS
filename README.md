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
- **GCP & SQL**: Databases for storing and managing inventory, sales, and employee data.

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

## 📅 Roadmap

- [x] Automate daily CSV exports using Selenium.
- [x] Integrate TouchBistro data into the IMS database.
- [x] Create low-stock notifications.
- [x] Build React-based dashboards with real-time visualizations.
- [x] Implement predictive analytics for inventory restocking.
- [x] Develop employee scheduling optimization feature.
- [ ] Create APIs for third-party integrations (e.g., accounting software).


## 🤝 Contributing

I welcome contributions to the Burgertone Inventory Management System! Here's how you can get involved:

### 🛠️ How to Contribute

1. **Fork the Repository**:  
   - Click the "Fork" button on the top-right corner of the repository page to create your copy of the project.

2. **Clone Your Fork**:  
   - Clone the repository to your local machine:
     ```bash
     git clone https://github.com/yourusername/Burgertone-IMS.git
     cd Burgertone-IMS
     ```

3. **Create a Branch**:  
   - Create a new branch for your feature or bug fix:
     ```bash
     git checkout -b feature/your-feature-name
     ```

4. **Make Changes**:  
   - Implement your feature, enhancement, or bug fix.
   - Ensure your changes adhere to the project's style and standards.

5. **Test Your Changes**:  
   - Run existing tests and, if applicable, write new tests for your changes.
   - Make sure all tests pass before proceeding.

6. **Commit Your Changes**:  
   - Add descriptive and meaningful commit messages:
     ```bash
     git add .
     git commit -m "Add a detailed description of your changes"
     ```

7. **Push to Your Fork**:  
   - Push your changes to your forked repository:
     ```bash
     git push origin feature/your-feature-name
     ```

8. **Open a Pull Request**:  
   - Go to the original repository and click "New Pull Request."
   - Provide a clear description of your changes and link any related issues.

---

### ✨ Guidelines for Contributions

- Ensure all code follows the project's style guide.
- Write clear, concise, and descriptive commit messages.
- Include comments and documentation where necessary.
- Run tests to ensure your changes do not introduce bugs.
- Be respectful and collaborative in your communication with other contributors.

---

### 🧑‍💻 Need Help?

If you're unsure about where to start or have any questions, feel free to open an issue or contact me via email. I am happy to help you contribute to the project!
Or you can simply contact me at [nehad.st@gmail.com](mailto:nehad.st@gmail.com)


---

### 📝 License

This project is licensed under the **MIT License**. 

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, subject to the following conditions:

- Include the original copyright notice and this permission notice in all copies or substantial portions of the Software.

For more details, see the [LICENSE](LICENSE) file.

---

## 🙌 Acknowledgments

I would like to thank the following for their contributions and support:

- **TouchBistro** for providing the point-of-sale data used in this project.
- **React.js**, **Flask**, **Chart.js**, and **Selenium**: The open-source tools that made this project possible.
- The Burgertone team for inspiration and input on inventory management challenges.

---

## 📞 Contact

We’d love to hear from you! Feel free to reach out through any of the following channels:

- **Connect on LinkedIn**: [Nehad Shikh Trab](https://linkedin.com/in/nehad-st)
- **Email**: [nehad.st@gmail.com](mailto:nehad.st@gmail.com)
- **Visit the Restaurant**: Check out Burgertone's official page at [burgertone.com](https://burgertone.com)

I appreciate your interest in the Burgertone Inventory Management System. Whether you have feedback, suggestions, or just want to say hello, don't hesitate to get in touch!



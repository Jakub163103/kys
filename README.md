# Know Your $avings

## Overview

Know Your $avings is a web application designed to help users track, compare, and optimize their finances effortlessly. The app provides powerful data insights, allowing users to see how much they can save on bills, subscriptions, insurance, and more.

## Features

- **User Authentication**: Secure sign-up and login functionality.
- **Expense Tracking**: Users can add and categorize their expenses.
- **Income Management**: Users can update their income and currency.
- **Data Visualization**: Interactive charts to visualize expenses by category.
- **Responsive Design**: Optimized for both desktop and mobile devices.

## Technologies Used

- **Backend**: Flask
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Charting Library**: Chart.js for data visualization
- **Styling**: Custom CSS for a modern look and feel

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Jakub163103/kys.git
   cd Know-Your-Savings
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```bash
   flask run
   ```

6. Open your browser and go to `http://127.0.0.1:5000`.

## Usage

- **Sign Up**: Create a new account to start tracking your finances.
- **Log In**: Access your account to view and manage your expenses.
- **Add Expenses**: Input your expenses and categorize them for better tracking.
- **View Insights**: Use the dashboard to visualize your spending and savings.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Flask community for their support and resources.
- Special thanks to the developers of Chart.js for their excellent charting library.

# 🏧 ATM Simulation Program

This is a command-line ATM simulation program written in Python. It allows users to manage a virtual bank account with basic ATM functionalities. All account data is stored in a MySQL database.

## Features

- Create an account (with automatically generated account number)
- Deposit money
- Withdraw money
- View account balance
- Delete an account
- PIN must be a 4-digit number
- Persistent data storage using MySQL

## Requirements

- Python 3.6 or higher
- MySQL Server (v8.0.16 or higher recommended)
- `mysql-connector-python` library

Install the required Python package with:

```bash
pip install mysql-connector-python
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/atm-simulation.git
   cd atm-simulation
   ```

2. Create a `config.py` file in the project directory with your database credentials:
   ```python
   MYSQL_HOST = "localhost"
   MYSQL_USER = "your_username"
   MYSQL_PASSWORD = "your_password"
   MYSQL_DATABASE = "atm_db"
   ```

3. Make sure MySQL is running, then execute the schema file:
   ```bash
   mysql -u your_username -p < schema.sql
   ```

   This will:
   - Create the `atm_db` database
   - Create the `accounts` table
   - Add a trigger to auto-generate account numbers
   - Enforce 4-digit PINs with a `CHECK` constraint

   > ⚠️ The PIN constraint requires MySQL 8.0.16+ for regex support in `CHECK`.

4. Run the Python program:
   ```bash
   python main.py
   ```

   Use the on-screen menu to:
   - Create a new account
   - Log in and deposit, withdraw, view balance, or delete the account

## Notes

- This project is intended for learning and educational purposes.
- It does not implement secure authentication or encryption.
- Please avoid using real personal or financial information.

## License

This project is open source. Feel free to modify it to suit your needs.
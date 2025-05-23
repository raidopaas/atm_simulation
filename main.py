import config
from bank_account import BankAccount
import mysql.connector
from decimal import Decimal, InvalidOperation
import sys
import re

conn = mysql.connector.connect(
	host=config.MYSQL_HOST,
	user=config.MYSQL_USER,
	password=config.MYSQL_PASSWORD,
	database=config.MYSQL_DATABASE
)

cursor = conn.cursor()

def execute_transaction(cursor, conn, query, params=(), fetch="none", on_success=None):

	try:
		cursor.execute(query, params)

		result = None
		if fetch == "one":
			result = cursor.fetchone()

		conn.commit()
	
		if on_success:
			on_success()

		#"ok" case is used when deleting an account
		return result if fetch != "none" else "ok"

	except mysql.connector.Error as err:
		print(f"Database error: {err}")
		conn.rollback()
		return "error"
	except Exception as e:
		print(f"Unexpected error: {e}")
		conn.rollback()
		return "error"

def create_account(cursor, conn, name, pin, initial_deposit):
	new_id = None

	def after_insert():
		nonlocal new_id
		new_id = cursor.lastrowid

    # Insert new account
	insert_result = execute_transaction(
		cursor,
		conn,
		"INSERT INTO accounts (name, pin, balance) VALUES (%s, %s, %s)",
		(name, pin, initial_deposit),
		on_success=after_insert
	)

	if new_id is None:
		print("New ID could not be retrieved.")
		return

	# Fetch new account number
	result = execute_transaction(
		cursor,
		conn,
		"SELECT account_nr FROM accounts WHERE account_id = %s",
		(new_id,),
		fetch="one"
	)

	if result:
		new_account_nr = result[0]
		print(f"New account successfully created, your account number is: {new_account_nr}")
	else:
		print("Account was created but account number could not be retrieved.")


# Handles user authentication
def login():
	while True:
		account_nr = input("Enter your account number (or type 'exit' to quit): ")

		if account_nr == "exit":
			print("Exiting...")
			return None

		query = "SELECT * FROM accounts WHERE account_nr = %s"
		params = (account_nr,)
		result = execute_transaction(
			cursor, 
			conn, 
			query, 
			params, 
			fetch="one"
		)

		if result == "error":
			break
		elif result is None:
			print("No account found.")
			continue # Ask again
		else:
			print("Account found.")

		pin_attempts = 3
		while True:
			pin_input = input("Enter your pin number: ")

			if pin_input == str(result[3]):
				print("Login successful")
				account = BankAccount(result[0], result[1], result[2], result[3], result[4])
				break # Exit PIN loop
			else:
				pin_attempts -= 1
				if pin_attempts == 0:
					print("Incorrect PIN, your card is now locked")
					sys.exit()
				print(f"Incorrect PIN, {pin_attempts} attempts remaining")
		return account # Exit outer loop once login is successful

def print_main_menu():
	menu = """
Select an option:
1. Login to my account
2. Create an account
(0. Close the program)
"""
	print(menu)

def print_menu():
	menu = """
Select an option:
1. Deposit
2. Withdraw
3. View balance
4. Delete account
0. Log out
"""
	print(menu)

def run_commands(option, account):
	match option:
		case 1:
			try:
				deposit_amount = Decimal(input("Enter an amount to be deposited: "))
				account.deposit(deposit_amount)
				query = "UPDATE accounts SET balance = %s WHERE account_nr = %s"
				params = (account.balance, account.account_number)
				execute_transaction(
					cursor, 
					conn, 
					query, 
					params, 
					on_success=lambda: print(f"Successfully deposited ${deposit_amount}")
				)
			except InvalidOperation:
				print("Invalid input. Please enter a valid number.")
			except ValueError as e:
				print(f"Invalid input: {e}")

		case 2:
			try:
				withdraw_amount = Decimal(input("Enter an amount to be withdrawn: "))
				account.withdraw(withdraw_amount)
				query = "UPDATE accounts SET balance = %s WHERE account_nr = %s"
				params = (account.balance, account.account_number)
				execute_transaction(
					cursor, 
					conn, 
					query, 
					params, 
					on_success=lambda: print(f"Successfully withdrawn ${withdraw_amount}")
				)
			except InvalidOperation:
				print("Invalid input. Please enter a valid number.")
			except ValueError as e:
				print(f"Invalid input: {e}")
		case 3:
			account.check_balance()
		case 4:
			if account.balance > 0:
				print("You need to withdraw your remaining balance before you can delete your account")
			else:
				ask_confirmation = input("Are you sure you want to delete you account? (Y/N) ")
				if ask_confirmation == "Y":
					query = "DELETE FROM accounts WHERE account_nr = %s"
					params = (account.account_number,)
					status = execute_transaction(
						cursor, 
						conn, 
						query, 
						params
					)
					if status == "ok":
						print("Your account is successfully deleted")
						return "deleted"
					else:
						print("An error occurred. Your account was not deleted.")
	return None

def begin_interaction(account):
	while True:
		print_menu()
		option = input("Enter you option: ")
		if option.isdigit() and 0 <= int(option) <= 4:
			option = int(option)
			if option == 0:
				print("Session is closed")
				break
			result = run_commands(option, account)
			if result == "deleted":
				break # Exit loop to go back to main menu
		else:
			print("Please enter a number between 0 and 4")

def start_session(option):
	match option:
		case 1:
			account = login()
			if account:
				begin_interaction(account)
		case 2:
			name = input("Enter account holder's name: ")
			pin = input("Enter a 4-digit pin: ")
			while not re.fullmatch(r"\d{4}", pin):
				print("Invalid PIN: must be exactly 4 digits.")
				pin = input("Enter a 4-digit pin: ")

			while True:
				try:
					initial_deposit = Decimal(input("Enter your initial deposit: "))
					if initial_deposit < 0:
						print("Deposit cannot be negative.")
						continue
					break # Valid and positive input
				except InvalidOperation:
					print("Invalid input. Please enter a valid number.")

			create_account(
				cursor, 
				conn, 
				name, 
				pin, 
				initial_deposit
			)

def welcome():
	while True:
		print("What would you like to do?")
		print_main_menu()
		option = input("Enter you option: ")
		if option.isdigit() and 0 <= int(option) <= 2:
			option = int(option)
			if option == 0:
				sys.exit()
			start_session(option)
		else:
			print("Please enter a number between 1 and 2")

def main():
	print("Welcome to the ATM simulation program")
	welcome()

# This makes sure that main() only runs when this file is executed directly,
# not when it's imported from another file.
if __name__ == "__main__":
    main()

cursor.close()
conn.close()
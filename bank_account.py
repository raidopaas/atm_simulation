class BankAccount:
	def __init__(self, account_id, account_number, name, pin, balance=0):
		self.account_id = account_id
		self.account_number = account_number
		self.name = name
		self.pin = pin
		self.balance = balance

	def deposit(self, amount):
		if amount <= 0:
			raise ValueError("Deposit amount must be positive.")
		self.balance += amount

	def withdraw(self, amount):
		if amount <= 0:
			raise ValueError("Withdraw amount must be positive.")
		if amount > self.balance:
			raise ValueError("Insufficient funds.")
		self.balance -= amount

	def check_balance(self):
		print(f"{self.name}'s account with number {self.account_number} balance is ${self.balance}")
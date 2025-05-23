CREATE DATABASE IF NOT EXISTS atm_db;
USE atm_db;

CREATE TABLE IF NOT EXISTS accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    account_nr VARCHAR(6) UNIQUE,
    name VARCHAR(100) NOT NULL,
    pin CHAR(4) NOT NULL CHECK (pin REGEXP '[0-9]{4}$'),
    balance DECIMAL(10,2) DEFAULT 0.00
);

DELIMITER $$

CREATE TRIGGER before_insert_accounts
BEFORE INSERT ON accounts
FOR EACH ROW
BEGIN
    IF NEW.account_nr IS NULL THEN
        SET NEW.account_nr = CONCAT('EE', LPAD(
            (SELECT AUTO_INCREMENT
             FROM INFORMATION_SCHEMA.TABLES
             WHERE TABLE_NAME = 'accounts'
             AND TABLE_SCHEMA = DATABASE()), 4, '0'));
    END IF;
END$$

DELIMITER ;
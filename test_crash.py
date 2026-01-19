import bcrypt
import mysql.connector as connector
import config

print("--- Test 1: Testing bcrypt ---")
try:
    password = b"testpassword"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    print("bcrypt test PASSED.")
except Exception as e:
    print(f"!!! bcrypt test FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Test 2: Testing MySQL Connection ---")
try:
    connection = connector.connect(**config.mysql_credentials)
    print("MySQL connection PASSED.")
    connection.close()
except Exception as e:
    print(f"!!! MySQL connection FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Test complete ---")
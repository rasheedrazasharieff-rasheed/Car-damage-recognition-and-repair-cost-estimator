import mysql.connector as connector
import config
import traceback

print("--- Testing MySQL Connection (V2) ---")
print("This test will try two different connection methods.\n")

# Test 1: Using 'use_pure=True' (avoids C-extension crash)
try:
    print(f"Attempt 1: Connecting to host from config ('{config.mysql_credentials['host']}') using pure Python...")
    
    # use_pure=True forces it to use the Python-only implementation
    connection = connector.connect(**config.mysql_credentials, use_pure=True) 
    
    print("Attempt 1 PASSED.")
    connection.close()
except Exception as e:
    print(f"!!! Attempt 1 FAILED: {e}")
    traceback.print_exc()

print("\n-----------------------------------\n")

# Test 2: Forcing host to 'localhost' (in case 127.0.0.1 is the issue)
try:
    print("Attempt 2: Connecting to host: 'localhost' using pure Python...")
    
    # Create a copy of credentials and change host
    local_creds = config.mysql_credentials.copy()
    local_creds['host'] = 'localhost'
    
    connection = connector.connect(**local_creds, use_pure=True)
    print("Attempt 2 PASSED.")
    connection.close()
except Exception as e:
    print(f"!!! Attempt 2 FAILED: {e}")
    traceback.print_exc()

print("\n--- Test complete ---")
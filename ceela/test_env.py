# test_env.py - paste this exactly
import os
from dotenv import load_dotenv

print("Current working directory:", os.getcwd())  # should be C:\ceela

load_dotenv()  # this loads .env

db_url = os.getenv("DATABASE_URL")
print("Loaded DATABASE_URL:", db_url)  # should NOT be None

if db_url is None:
    print("ERROR: .env not loaded! Check file name, location, or content.")
    if os.path.exists(".env"):
        print(".env file EXISTS.")
        with open(".env", "r") as f:
            print("First line of .env:", f.readline().strip())
    else:
        print(".env file DOES NOT EXIST in current directory.")
else:
    print("SUCCESS: DATABASE_URL loaded correctly.")
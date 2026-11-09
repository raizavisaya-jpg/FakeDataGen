
from database import create_tables
from authentication import register_user, login_user
from generator import generate_records, save_records

# Initialize database
create_tables()

# Login using our existing test account
success, message = login_user("testuser", "test123")
print(message)

if success:
    # Generate 10 fictional records
    records = generate_records(10)

    # Save records under the test user's account
    saved_count = save_records(records, 1)

    print(f"{saved_count} records saved successfully!")

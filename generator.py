
from faker import Faker
from database import connect_db

# Initialize Faker
fake = Faker()


def generate_records(quantity=10):
    """Generate fictional user records."""

    if quantity < 10:
        raise ValueError("Generate at least 10 records.")

    records = []

    for _ in range(quantity):
        record = {
            "full_name": fake.name(),
            "email": fake.email(),
            "address": fake.street_address(),
            "birthdate": fake.date_of_birth(
                minimum_age=18,
                maximum_age=60
            ).isoformat(),
            "mobile_number": fake.phone_number(),
            "job": fake.job(),
            "company": fake.company(),
            "city": fake.city(),
            "country": fake.country(),
            "zipcode": fake.postcode()
        }

        records.append(record)

    return records


def save_records(records, user_id):
    """Save generated records to SQLite database."""

    connection = connect_db()
    cursor = connection.cursor()

    try:
        for record in records:
            cursor.execute("""
                INSERT INTO generated_data (
                    user_id,
                    full_name,
                    email,
                    address,
                    birthdate,
                    mobile_number,
                    job,
                    company,
                    city,
                    country,
                    zipcode
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                record["full_name"],
                record["email"],
                record["address"],
                record["birthdate"],
                record["mobile_number"],
                record["job"],
                record["company"],
                record["city"],
                record["country"],
                record["zipcode"]
            ))

        connection.commit()
        return len(records)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

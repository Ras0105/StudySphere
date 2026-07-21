"""
generate_env.py

Creates a ".env" file for local development/testing, without touching
or exposing the real project owner's ".env".

Run this AFTER activating the virtual environment:
    python generate_env.py

It will:
  1. Ask you for MongoDB / database / email details (press Enter on any
     of them to leave a placeholder you can fill in by hand later).
  2. Auto-generate a random SECRET_KEY for you.
  3. Write everything to a new ".env" file in this folder, matching
     the structure the app expects.

Safe to run multiple times — it will ask before overwriting an existing
".env".
"""

import os
import secrets

ENV_PATH = ".env"


def ask(prompt, placeholder):
    value = input(f"{prompt}: ").strip()
    if not value:
        print(f"  (left blank — using placeholder, edit .env later)")
        return placeholder
    return value


def main():
    if os.path.exists(ENV_PATH):
        overwrite = input(f'"{ENV_PATH}" already exists. Overwrite it? (y/N): ').strip().lower()
        if overwrite != "y":
            print("Cancelled. Existing .env left untouched.")
            return

    print("\nPress Enter on any question to leave a placeholder for later.\n")

    mongodb_uri = ask(
        "MONGODB_URI (e.g. mongodb+srv://user:pass@cluster.mongodb.net)",
        "mongodb+srv://your_username:your_password@your_cluster.mongodb.net",
    )
    database_name = ask("DATABASE_NAME", "your_database_name")
    email_address = ask("EMAIL_ADDRESS", "your_email@example.com")
    email_app_password = ask("EMAIL_APP_PASSWORD", "your_email_app_password")
    staff_registration_code = ask("STAFF_REGISTRATION_CODE", "your_staff_registration_code")

    secret_key = secrets.token_hex(32)

    with open(ENV_PATH, "w") as f:
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write(f"MONGODB_URI={mongodb_uri}\n")
        f.write(f"DATABASE_NAME={database_name}\n")
        f.write(f"EMAIL_ADDRESS={email_address}\n")
        f.write(f"EMAIL_APP_PASSWORD={email_app_password}\n")
        f.write(f"STAFF_REGISTRATION_CODE={staff_registration_code}\n")

    print(f'\n".env" created successfully with a freshly generated SECRET_KEY.')
    print("Edit it any time to update values.")


if __name__ == "__main__":
    main()
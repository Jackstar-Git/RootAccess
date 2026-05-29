from werkzeug.security import generate_password_hash
from typing import Optional


def main() -> None:
    print("=" * 70)
    print("Password Hash Generator for users.json")
    print("=" * 70)
    print()

    while True:
        try:
            username: str = input("Enter username (or 'quit' to exit): ").strip()
            
            if username.lower() == "quit":
                print("\nExiting.")
                break
            
            if not username:
                print("Username cannot be empty. Please try again.\n")
                continue
            
            password: str = input(f"Enter password for '{username}': ").strip()
            
            if not password:
                print("Password cannot be empty. Please try again.\n")
                continue
            
            # Confirm password
            password_confirm: str = input("Confirm password: ").strip()
            
            if password != password_confirm:
                print("Passwords do not match. Please try again.\n")
                continue
            
            # Generate hash
            password_hash: str = generate_password_hash(password, method='scrypt')
            
            # Display the hash
            print()
            print("-" * 70)
            print(f"Hash for user '{username}':")
            print("-" * 70)
            print(password_hash)
            print()
            
            # Generate a template JSON entry
            print("Template for users.json entry:")
            print("-" * 70)
            template: str = f'''
{{
  "username": {{
    "password_hash": "{password_hash}",
    "permissions": [
      "view_dashboard"
    ]
  }}
}}
'''.replace("username", username).strip()
            print(template)
            print("-" * 70)
            print()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()

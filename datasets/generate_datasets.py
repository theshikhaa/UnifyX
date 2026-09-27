import os
import csv
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_demo_datasets():
    """Generates the 4 core demonstration CSV datasets."""
    datasets = {
        "database_a": {
            "file": "hr_database.csv",
            "headers": ["employee_id", "full_name", "email", "mobile_number"],
            "rows": [
                ["E-1001", "John Doe", "john@gmail.com", "+91 98765-43210"],
                ["E-1002", "Sarah Connor", "sarah.c@cyberdyne.com", "9876500001"],
                ["E-1003", "Robert Bruce", "robert@bruce.org", "9876500002"],
                ["E-1004", "Alex Mercer", "alex.m@gentek.com", "+91 91234-56789"],
                ["E-1005", "Emily Watson", "emily.watson@hr.com", "9876500005"],
            ]
        },
        "database_b": {
            "file": "customer_database.csv",
            "headers": ["customer_id", "name", "email_id", "contact_no", "address"],
            "rows": [
                ["C-8812", "John Doe ", " JOHN@GMAIL.COM ", "9876543210", "124 Marine Drive, Mumbai"],
                ["C-8813", "Sarah Connor", "sarah.c@cyberdyne.com", "+1-555-0199", "742 Evergreen Terrace, Los Angeles"],
                ["C-8814", "Robert Bruce", "robert@bruce.org", "9876500002", "Highland Estate, Edinburgh"],
                ["C-8815", "Priya Patel", "priya.patel@gmail.com", "+91 99887-76655", "Park Street, Kolkata"],
                ["C-8816", "Vikram Singh", "vikram@singh.in", "N/A", "MG Road, Bengaluru"],
            ]
        },
        "database_c": {
            "file": "business_database.csv",
            "headers": ["username", "phone", "company", "city"],
            "rows": [
                ["johndoe", "+919876543210", "ABC Pvt Ltd", "Mumbai"],
                ["sconnor", "9876500001", "Cyberdyne Systems", "Los Angeles"],
                ["rbruce", "9876500002", "Bruce Enterprises", "Edinburgh"],
                ["ppatel", "9988776655", "Patel & Co", "Kolkata"],
                ["dev_user", "9111122233", "TechCorp", "Delhi"],
            ]
        },
        "database_d": {
            "file": "membership_database.csv",
            "headers": ["member_id", "email", "username"],
            "rows": [
                ["M-1024", "john@gmail.com", "johndoe"],
                ["M-1025", "sarah.c@cyberdyne.com", "sconnor"],
                ["M-1026", "robert@bruce.org", "rbruce"],
                ["M-1027", "alex.m@gentek.com", "amercer"],
                ["M-9999", "lonewolf@unknown.io", "null"],
            ]
        }
    }

    for db_key, data in datasets.items():
        folder_path = os.path.join(BASE_DIR, db_key)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, data["file"])
        
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data["headers"])
            writer.writerows(data["rows"])
        print(f"Created dataset: {file_path}")

def generate_large_dataset(count=10000, output_path=None):
    """Utility to generate large benchmark datasets for batch testing."""
    if not output_path:
        output_path = os.path.join(BASE_DIR, "large_benchmark_10k.csv")

    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "company.io"]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "full_name", "email_address", "phone_no"])
        
        for i in range(1, count + 1):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f"{fn.lower()}.{ln.lower()}{i}@{random.choice(domains)}"
            phone = f"+91 98{random.randint(10000000, 99999999)}"
            writer.writerow([f"UID-{i}", f"{fn} {ln}", email, phone])
            
    print(f"Generated large dataset with {count} records at: {output_path}")

if __name__ == "__main__":
    create_demo_datasets()

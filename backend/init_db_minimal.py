"""Minimal database init: creates tables + imports medicine.csv + seeds default merchant."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(override=True)

from config import get_database_uri
from models import db, Medicine, Merchant
from utils import hash_password

# Flask app with DB only — avoid importing routes (and thus voice_pipeline → Whisper)
from flask import Flask

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Tables created.")

    # Seed default merchant
    if not Merchant.query.filter_by(username="admin").first():
        merchant = Merchant(
            username="admin",
            password=hash_password("123456"),
            name="默认商家",
        )
        db.session.add(merchant)
        db.session.commit()
        print("Default merchant created (admin / 123456).")
    else:
        print("Default merchant already exists.")

    # Import medicine CSV
    if Medicine.query.first():
        print(f"Medicines table already has data ({Medicine.query.count()} rows). Skipping CSV import.")
    else:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "medicine.csv")
        if not os.path.exists(csv_path):
            print(f"ERROR: medicine.csv not found at {csv_path}")
            sys.exit(1)

        count = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 9:
                    continue
                medicine = Medicine(
                    name=row[0].strip(),
                    category=row[1].strip(),
                    price=float(row[2].strip()),
                    spec=row[3].strip(),
                    manufacturer=row[4].strip(),
                    desc=row[5].strip(),
                    usage=row[6].strip(),
                    notice=row[7].strip(),
                    symptoms=row[8].strip(),
                    on_sale=True,
                )
                db.session.add(medicine)
                count += 1

        db.session.commit()
        print(f"Imported {count} medicines from medicine.csv.")

print("Database initialization complete.")

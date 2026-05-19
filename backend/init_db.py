import pymysql

from config import get_mysql_config, load_env
from app import create_app
from models import Merchant, db
from utils import hash_password


def ensure_database(connection_config):
    base_config = connection_config.copy()
    database_name = base_config.pop("database", "")
    if not database_name:
        raise ValueError("DB_NAME is required to create the database")

    base_config.pop("auth_plugin", None)

    with pymysql.connect(**base_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` DEFAULT CHARACTER SET utf8mb4"
            )


def run_migrations():
    load_env()
    mysql_config = get_mysql_config()

    print("MySQL config:", mysql_config)
    ensure_database(mysql_config)

    app = create_app()
    with app.app_context():
        db.create_all()

        if not Merchant.query.filter_by(username="admin").first():
            merchant = Merchant(
                username="admin",
                password=hash_password("123456"),
                name="默认商家",
            )
            db.session.add(merchant)
            db.session.commit()

    print("Database and tables are ready (SQLAlchemy).")


if __name__ == "__main__":
    run_migrations()

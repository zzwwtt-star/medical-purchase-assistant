import os

from dotenv import load_dotenv


def load_env():
    load_dotenv(override=True)


def get_mysql_config():
    config = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "graduation_design"),
        "charset": "utf8mb4",
        "autocommit": True,
    }

    auth_plugin = os.getenv("DB_AUTH_PLUGIN", "").strip()
    if auth_plugin:
        config["auth_plugin"] = auth_plugin

    return config


def get_database_uri():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "graduation_design")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

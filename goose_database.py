"""
Database utilities for GOOSE
"""

import sqlite3
from goose_config import DATABASE_PATH


def get_connection():
    """Get a database connection"""
    return sqlite3.connect(DATABASE_PATH)


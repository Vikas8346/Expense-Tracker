import sqlite3
from datetime import datetime
from contextlib import contextmanager

DATABASE = 'expenses.db'

@contextmanager
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database with tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                merchant TEXT,
                date TEXT NOT NULL,
                description TEXT,
                receipt_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_expense(amount, category, merchant, date, description, receipt_image=None):
    """Add a new expense to the database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (amount, category, merchant, date, description, receipt_image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (amount, category, merchant, date, description, receipt_image))
        conn.commit()
        return cursor.lastrowid

def get_expenses():
    """Get all expenses"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
        expenses = [dict(row) for row in cursor.fetchall()]
        return expenses

def get_expense(expense_id):
    """Get a single expense"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_expense(expense_id):
    """Delete an expense"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()

def get_expenses_by_category(category):
    """Get expenses by category"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE category = ? ORDER BY date DESC', (category,))
        expenses = [dict(row) for row in cursor.fetchall()]
        return expenses

def get_expenses_by_date_range(start_date, end_date):
    """Get expenses within a date range"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date DESC',
            (start_date, end_date)
        )
        expenses = [dict(row) for row in cursor.fetchall()]
        return expenses

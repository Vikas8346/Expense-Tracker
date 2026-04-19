from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func

db = SQLAlchemy()

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    merchant = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Other')
    date = db.Column(db.Date, nullable=False)
    items = db.Column(db.Text)  # Comma-separated items
    image_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'merchant': self.merchant,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'items': self.items,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Expense {self.id}: {self.merchant} - ₹{self.amount}>'

def init_db(app):
    """Initialize database with app context."""
    with app.app_context():
        db.create_all()

def save_expense(merchant, amount, category, date, items, image_path=None):
    """Save a new expense to the database."""
    try:
        expense = Expense(
            merchant=merchant,
            amount=float(amount),
            category=category,
            date=date,
            items=items,
            image_path=image_path
        )
        db.session.add(expense)
        db.session.commit()
        return expense.id
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return None
    finally:
        db.session.close()

def get_all_expenses():
    """Get all expenses ordered by date (newest first)."""
    try:
        expenses = Expense.query.order_by(Expense.date.desc()).all()
        return [exp.to_dict() for exp in expenses]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_expenses_by_category(category):
    """Get expenses filtered by category."""
    try:
        expenses = Expense.query.filter_by(category=category).order_by(Expense.date.desc()).all()
        return [exp.to_dict() for exp in expenses]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_category_totals():
    """Get total spending by category."""
    try:
        totals = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).group_by(Expense.category).all()

        result = {}
        for category, total, count in totals:
            result[category] = {
                'total': round(float(total) if total else 0, 2),
                'count': count
            }
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return {}

def get_monthly_totals(months=6):
    """Get total spending by month for the last N months."""
    try:
        # Get last N months of data
        today = datetime.now()
        start_date = today - timedelta(days=30*months)

        expenses = Expense.query.filter(Expense.date >= start_date).all()

        monthly = {}
        for exp in expenses:
            month_key = exp.date.strftime('%Y-%m')
            if month_key not in monthly:
                monthly[month_key] = 0
            monthly[month_key] += exp.amount

        return dict(sorted(monthly.items()))
    except Exception as e:
        print(f"Database error: {e}")
        return {}

def get_total_spent():
    """Get total amount spent."""
    try:
        total = db.session.query(func.sum(Expense.amount)).scalar()
        return round(float(total) if total else 0, 2)
    except Exception as e:
        print(f"Database error: {e}")
        return 0.0

def get_total_spent_this_month():
    """Get total spent in current month."""
    try:
        today = datetime.now()
        month_start = today.replace(day=1)

        total = db.session.query(func.sum(Expense.amount)).filter(
            Expense.date >= month_start
        ).scalar()
        return round(float(total) if total else 0, 2)
    except Exception as e:
        print(f"Database error: {e}")
        return 0.0

def get_transaction_count():
    """Get total number of expenses."""
    try:
        return Expense.query.count()
    except Exception as e:
        print(f"Database error: {e}")
        return 0

def get_top_category():
    """Get the category with highest spending."""
    try:
        totals = get_category_totals()
        if not totals:
            return {'category': 'N/A', 'amount': 0}
        top = max(totals.items(), key=lambda x: x[1]['total'])
        return {
            'category': top[0],
            'amount': top[1]['total']
        }
    except Exception as e:
        print(f"Database error: {e}")
        return {'category': 'N/A', 'amount': 0}

def get_recent_expenses(limit=5):
    """Get recent N expenses."""
    try:
        expenses = Expense.query.order_by(Expense.date.desc()).limit(limit).all()
        return [exp.to_dict() for exp in expenses]
    except Exception as e:
        print(f"Database error: {e}")
        return []

def delete_expense(expense_id):
    """Delete an expense by ID."""
    try:
        expense = Expense.query.get(expense_id)
        if expense:
            # Delete image file if exists
            if expense.image_path and os.path.exists(expense.image_path):
                import os
                os.remove(expense.image_path)
            db.session.delete(expense)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        db.session.close()

def update_expense(expense_id, merchant, amount, category, date, items):
    """Update an existing expense."""
    try:
        expense = Expense.query.get(expense_id)
        if expense:
            expense.merchant = merchant
            expense.amount = float(amount)
            expense.category = category
            expense.date = date
            expense.items = items
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        db.session.close()

def get_spending_summary():
    """Get comprehensive spending summary for advice generation."""
    try:
        totals = get_category_totals()
        monthly = get_monthly_totals(3)

        summary = {
            'total_spent': get_total_spent(),
            'this_month': get_total_spent_this_month(),
            'by_category': totals,
            'monthly_trend': monthly,
            'transaction_count': get_transaction_count()
        }
        return summary
    except Exception as e:
        print(f"Database error: {e}")
        return {}

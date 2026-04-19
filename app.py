import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from core.db import (
    db, init_db, save_expense, get_all_expenses, delete_expense,
    get_category_totals, get_monthly_totals, get_total_spent,
    get_total_spent_this_month, get_transaction_count, get_top_category,
    get_recent_expenses, update_expense, get_spending_summary, get_expenses_by_category
)
from core.ocr import extract_text_from_receipt, extract_from_pdf
from core.claude_ai import analyze_receipt, generate_financial_advice

# Load environment variables
load_dotenv()

# Configure Tesseract OCR path for Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(TESSERACT_PATH):
    os.environ['PATH'] = TESSERACT_PATH + os.pathsep + os.environ.get('PATH', '')
    import pytesseract
    pytesseract.pytesseract.pytesseract_cmd = os.path.join(TESSERACT_PATH, 'tesseract.exe')
    print("[INFO] Tesseract OCR configured successfully")
else:
    print("[WARNING] Tesseract OCR not found at", TESSERACT_PATH)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize database
db.init_app(app)
init_db(app)

CATEGORIES = ['Food', 'Transport', 'Shopping', 'Health', 'Entertainment', 'Utilities', 'Other']

CATEGORY_COLORS = {
    'Food': '#1D9E75',
    'Transport': '#378ADD',
    'Shopping': '#7F77DD',
    'Health': '#E24B4A',
    'Entertainment': '#D4537E',
    'Utilities': '#EF9F27',
    'Other': '#888780'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page with metrics and recent expenses."""
    metrics = {
        'total_spent': get_total_spent(),
        'this_month': get_total_spent_this_month(),
        'transactions': get_transaction_count(),
        'top_category': get_top_category()
    }

    category_totals = get_category_totals()
    categories_data = []
    for cat in CATEGORIES:
        if cat in category_totals:
            categories_data.append({
                'name': cat,
                'amount': category_totals[cat]['total'],
                'color': CATEGORY_COLORS[cat]
            })
        else:
            categories_data.append({
                'name': cat,
                'amount': 0,
                'color': CATEGORY_COLORS[cat]
            })

    recent = get_recent_expenses(5)

    return render_template('index.html',
                         metrics=metrics,
                         categories=categories_data,
                         recent_expenses=recent)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload receipt page."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('upload'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('upload'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed: JPG, PNG, PDF', 'error')
            return redirect(url_for('upload'))

        try:
            # Save file
            filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Extract text based on file type
            try:
                if filename.lower().endswith('.pdf'):
                    ocr_text = extract_from_pdf(filepath)
                else:
                    ocr_text = extract_text_from_receipt(filepath)

                if not ocr_text:
                    flash('❌ Could not extract text from receipt. Please ensure the receipt is clear and readable.', 'error')
                    return redirect(url_for('upload'))

            except RuntimeError as ocr_error:
                # Better error message for Tesseract issues
                error_msg = str(ocr_error)
                if "Tesseract" in error_msg or "tesseract" in error_msg:
                    flash(
                        f'⚠️ {error_msg}\n\n'
                        f'Quick fix: Download Tesseract from https://github.com/UB-Mannheim/tesseract/wiki',
                        'error'
                    )
                else:
                    flash(f'❌ OCR Error: {error_msg}', 'error')
                return redirect(url_for('upload'))

            # Analyze with Claude
            analysis = analyze_receipt(ocr_text)

            # Store in session for result page
            session_data = {
                'merchant': analysis.get('merchant', 'Unknown'),
                'amount': analysis.get('amount', 0),
                'category': analysis.get('category', 'Other'),
                'date': analysis.get('date', datetime.now().strftime('%Y-%m-%d')),
                'items': analysis.get('items', ''),
                'image_path': filepath,
                'ocr_text': ocr_text
            }

            return render_template('result.html', expense=session_data, categories=CATEGORIES)

        except Exception as e:
            flash(f'❌ Error processing receipt: {str(e)}', 'error')
            return redirect(url_for('upload'))

    return render_template('upload.html')

@app.route('/save', methods=['POST'])
def save():
    """Save analyzed expense to database."""
    try:
        data = request.get_json() if request.is_json else request.form

        merchant = data.get('merchant', 'Unknown')
        amount = data.get('amount', 0)
        category = data.get('category', 'Other')
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        items = data.get('items', '')
        image_path = data.get('image_path', '')

        # Validate
        try:
            amount = float(amount)
        except ValueError:
            return jsonify({'error': 'Invalid amount'}), 400

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date_obj = datetime.now().date()

        # Save to database
        expense_id = save_expense(merchant, amount, category, date_obj, items, image_path)

        if expense_id:
            if request.is_json:
                return jsonify({'success': True, 'expense_id': expense_id}), 201
            else:
                flash('Expense saved successfully!', 'success')
                return redirect(url_for('expenses'))
        else:
            if request.is_json:
                return jsonify({'error': 'Database error'}), 500
            else:
                flash('Error saving expense', 'error')
                return redirect(url_for('upload'))

    except Exception as e:
        error_msg = f'Error: {str(e)}'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('upload'))

@app.route('/expenses')
def expenses():
    """All expenses page with filtering."""
    category = request.args.get('category', '')

    if category and category in CATEGORIES:
        expenses_list = get_expenses_by_category(category)
    else:
        expenses_list = get_all_expenses()

    return render_template('expenses.html',
                         expenses=expenses_list,
                         categories=CATEGORIES,
                         selected_category=category,
                         category_colors=CATEGORY_COLORS)

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
    """Delete an expense."""
    if delete_expense(expense_id):
        flash('Expense deleted successfully', 'success')
    else:
        flash('Error deleting expense', 'error')

    return redirect(url_for('expenses'))

@app.route('/dashboard')
def dashboard():
    """Dashboard with charts."""
    category_totals = get_category_totals()
    monthly_totals = get_monthly_totals(6)

    # Prepare category data for charts
    chart_data = {
        'categories': [],
        'amounts': [],
        'colors': []
    }

    for cat in CATEGORIES:
        if cat in category_totals:
            chart_data['categories'].append(cat)
            chart_data['amounts'].append(category_totals[cat]['total'])
            chart_data['colors'].append(CATEGORY_COLORS[cat])

    # Prepare monthly data for line chart
    monthly_data = {
        'months': list(monthly_totals.keys()),
        'amounts': list(monthly_totals.values())
    }

    return render_template('dashboard.html',
                         chart_data=chart_data,
                         monthly_data=monthly_data,
                         category_colors=CATEGORY_COLORS)

@app.route('/advice')
def advice():
    """AI financial advice page."""
    summary = get_spending_summary()

    # Generate advice
    advice_text = generate_financial_advice(summary)

    # Parse tips (numbered list)
    tips = []
    for line in advice_text.split('\n'):
        if line.strip() and line[0].isdigit():
            tip = line.split('.', 1)[1].strip() if '.' in line else line
            tips.append(tip)

    # Budget limits (in rupees)
    budgets = {
        'Food': 5000,
        'Transport': 3000,
        'Shopping': 4000,
        'Health': 2000,
        'Entertainment': 2000,
        'Utilities': 2500,
        'Other': 1000
    }

    # Prepare budget vs actual
    budget_data = []
    category_totals = get_category_totals()

    for cat in CATEGORIES:
        total = category_totals.get(cat, {}).get('total', 0)
        budget = budgets.get(cat, 1000)
        percentage = min((total / budget * 100) if budget > 0 else 0, 100)

        budget_data.append({
            'category': cat,
            'actual': total,
            'budget': budget,
            'percentage': percentage,
            'color': CATEGORY_COLORS[cat]
        })

    return render_template('advice.html',
                         tips=tips[:4],
                         budget_data=budget_data,
                         summary=summary)

@app.route('/api/totals')
def api_totals():
    """API endpoint for category totals."""
    totals = get_category_totals()
    return jsonify(totals)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# 💰 AI Expense Tracker

A production-ready expense tracking web application powered by **Flask**, **Claude AI**, **Tesseract OCR**, and **SQLAlchemy**. Upload receipt images or PDFs, and let AI automatically extract, categorize, and analyze your spending with personalized financial advice.

## 🎯 Features

✨ **AI-Powered Receipt Analysis** - Claude API intelligently extracts merchant, amount, date, and category  
📸 **Advanced OCR** - Tesseract + OpenCV preprocessing for high-accuracy text extraction  
🏷️ **Auto-Categorization** - Intelligent categorization into Food, Transport, Shopping, Health, Entertainment, Utilities, Other  
📊 **Financial Dashboard** - Interactive charts (doughnut, bar, line) with Chart.js  
💡 **AI Financial Advice** - Personalized money-saving tips based on spending patterns  
💳 **Budget Tracking** - Visual budget vs actual progress bars with category limits  
🔍 **Expense Management** - View, filter, search, and delete expenses  
💾 **Persistent Storage** - SQLite database with SQLAlchemy ORM  
🎨 **Modern UI** - Clean flat design, fully responsive, Indian Rupee formatting  

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Routes](#api-routes)
- [Database Schema](#database-schema)
- [Color Scheme](#color-scheme)
- [Troubleshooting](#troubleshooting)

## 🛠 Tech Stack

- **Backend**: Flask 3.0+ (Python web framework)
- **AI**: Anthropic Claude API (claude-sonnet-4-20250514)
- **OCR**: Tesseract + OpenCV (image preprocessing)
- **Database**: SQLite + SQLAlchemy ORM
- **Frontend**: HTML5, CSS3 (flat design), JavaScript (vanilla)
- **Charts**: Chart.js 4.4
- **File Handling**: Werkzeug (secure uploads)

## 📦 Prerequisites

- **Python 3.8+**
- **Tesseract OCR** (system-level installation)
- **Claude API Key** (from [Anthropic Console](https://console.anthropic.com))

### Installing Tesseract

**Windows:**
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (default: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH if needed

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**Verify Installation:**
```bash
tesseract --version
```

## 🚀 Installation

1. **Clone and setup:**
```bash
git clone https://github.com/Vikas8346/Expense-Tracker.git
cd Expense-Tracker
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add:
# ANTHROPIC_API_KEY=sk-ant-...
# SECRET_KEY=your-random-secret-string
```

4. **Run application:**
```bash
python app.py
```

Visit: http://localhost:5000

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Anthropic Claude API
ANTHROPIC_API_KEY=your_api_key_here

# Flask Security
SECRET_KEY=random-secret-string-here
```

### Default Budget Limits (₹ INR)

| Category | Budget |
|----------|--------|
| Food | ₹5,000 |
| Transport | ₹3,000 |
| Shopping | ₹4,000 |
| Health | ₹2,000 |
| Entertainment | ₹2,000 |
| Utilities | ₹2,500 |
| Other | ₹1,000 |

## 📖 Usage

### 1. Upload Receipt
- Navigate to **Upload Receipt**
- Drag-drop or click to select JPG, PNG, or PDF
- App extracts text and sends to Claude AI
- Review and edit suggested values
- Click **Save Expense**

### 2. View Expenses
- Go to **Expenses** page
- Filter by category using pill buttons
- View all expenses in responsive table
- Delete expenses (with confirmation)

### 3. Dashboard
- **Doughnut Chart** - Spending distribution by category
- **Bar Chart** - Category breakdown (horizontal)
- **Line Chart** - 6-month spending trend

### 4. Financial Advice
- **AI Tips** - 4 personalized money-saving recommendations
- **Budget Tracking** - Progress bars showing actual vs budget per category
- Color-coded status: green (under), amber (nearing), red (over budget)

### 5. Home Dashboard
- **Metric Cards** - Total spent, this month, transaction count, top category
- **Category Breakdown** - Bar chart of spending by category
- **Recent Transactions** - Last 5 expenses table

## 📁 Project Structure

```
Expense-Tracker/
├── app.py                          # Flask app with all routes
├── core/
│   ├── __init__.py
│   ├── ocr.py                      # Tesseract + OpenCV preprocessing
│   ├── claude_ai.py                # Claude API integration
│   └── db.py                       # SQLAlchemy models & queries
├── templates/
│   ├── base.html                   # Navbar + layout
│   ├── index.html                  # Home with metrics
│   ├── upload.html                 # File upload
│   ├── result.html                 # AI result review & edit
│   ├── expenses.html               # All expenses table
│   ├── dashboard.html              # Charts
│   └── advice.html                 # Financial tips + budget
├── static/
│   ├── css/
│   │   └── style.css               # Responsive design system
│   └── uploads/                    # Receipt images (auto-created)
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore
├── README.md                       # This file
└── expense_tracker.db              # SQLite (auto-created)
```

## 🔌 API Routes

### Page Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home dashboard |
| GET | `/upload` | Upload receipt page |
| POST | `/upload` | Process receipt upload |
| GET | `/expenses` | View all expenses (optional `?category=`) |
| POST | `/delete/<id>` | Delete expense |
| GET | `/dashboard` | Charts dashboard |
| GET | `/advice` | Financial advice page |

### API Endpoints
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/save` | Save analyzed expense (JSON or form) |
| GET | `/api/totals` | Get category totals (JSON) |

## 🗄 Database Schema

### expenses table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AI | Primary key |
| merchant | VARCHAR(255) | NOT NULL | Store/business name |
| amount | FLOAT | NOT NULL | Expense amount (₹) |
| category | VARCHAR(50) | NOT NULL | Food/Transport/Shopping/Health/Entertainment/Utilities/Other |
| date | DATE | NOT NULL | Transaction date (YYYY-MM-DD) |
| items | TEXT | NULL | Comma-separated purchased items |
| image_path | VARCHAR(500) | NULL | Path to receipt image |
| created_at | DATETIME | DEFAULT now | Record creation timestamp |

**Indices:**
- `category` (for filtering)
- `date` (for sorting/trends)

## 🎨 Color Scheme

### Category Colors (Material-inspired)

| Category | Hex | Light BG | Dark Text |
|----------|-----|----------|-----------|
| Food | #1D9E75 | #E1F5EE | #085041 |
| Transport | #378ADD | #E6F1FB | #0C447C |
| Shopping | #7F77DD | #EEEDFE | #3C3489 |
| Health | #E24B4A | #FCEBEB | #791F1F |
| Entertainment | #D4537E | #FBEAF0 | #72243E |
| Utilities | #EF9F27 | #FAEEDA | #633806 |
| Other | #888780 | #F1EFE8 | #444441 |

### Design System

**Color Variables:**
- Primary: `#667eea` (Indigo)
- Text: `#1f2937` (Gray-900)
- Text-secondary: `#6b7280` (Gray-600)
- Border: `#e5e7eb` (Gray-200)

**Responsive Grid:**
- Desktop: 2-column (500px min)
- Tablet: 1-column
- Mobile (<640px): Optimized

## 🧠 How It Works

### Receipt Analysis Flow

```
1. Upload Receipt (JPG/PNG/PDF)
   ↓
2. OpenCV Preprocessing
   - Grayscale conversion
   - Denoising (fastNlMeansDenoising)
   - Bilateral filtering
   - Adaptive threshold
   - Morphological operations
   ↓
3. Tesseract OCR Extraction
   - Extract text from preprocessed image
   ↓
4. Claude API Analysis
   - Send OCR text to Claude Sonnet
   - Parse JSON response with merchant, amount, category, date, items
   ↓
5. User Review
   - Display extracted data
   - Allow manual edits
   ↓
6. Save to SQLite
   - Store in expenses table
   - Link receipt image
   ↓
7. Dashboard Updates
   - Charts refresh
   - Metrics recalculate
   - Advice regenerates
```

### Claude API Prompts

**Receipt Analysis:**
```
You are an expense analyzer. Given receipt OCR text, extract and return
ONLY a valid JSON object:
{
  "merchant": "store name",
  "amount": 0.0,
  "date": "YYYY-MM-DD or null",
  "category": "one of [Food/Transport/Shopping/Health/Entertainment/Utilities/Other]",
  "items": "comma-separated main items"
}
No explanation, no markdown, just JSON.
```

**Financial Advice:**
```
You are a friendly personal finance advisor for a college student in India.
Based on this spending summary, provide exactly 4 practical money-saving tips
as a numbered list. Be specific, use Indian context (UPI, local stores, etc).
Spending data: {summary}
```

## 📝 Dependencies

See `requirements.txt`:
```
flask>=3.0.0
flask-sqlalchemy>=3.0.0
anthropic>=0.25.0
pytesseract>=0.3.10
opencv-python>=4.9.0
Pillow>=10.0.0
SQLAlchemy>=2.0.0
python-dotenv>=1.0.0
PyMuPDF>=1.24.0
Werkzeug>=3.0.0
```

## 🐛 Troubleshooting

### Tesseract Not Found
```
pytesseract.TesseractNotFoundError: ...
```
**Solution:**
- Install Tesseract via OS package manager
- Windows: Use PATH or update `pytesseract.pytesseract.pytesseract_cmd`

### Claude API Errors
```
anthropic.AuthenticationError
```
**Solution:**
- Verify `ANTHROPIC_API_KEY` in `.env` is correct
- Check API key hasn't expired at [Console](https://console.anthropic.com)

### Database Locked
```
sqlite3.OperationalError: database is locked
```
**Solution:**
- Close any other connections
- Delete `expense_tracker.db` and restart (loses data)

### OCR Quality Poor
**Solutions:**
- Use high-resolution receipts (300+ DPI)
- Ensure good lighting in photos
- Keep receipt flat and centered
- Avoid shadows or glare

## 🚀 Performance Tips

- **Large PDFs:** Split into separate uploads
- **Batch Operations:** Dashboard caches chart data
- **Database:** Consider adding indexes for large datasets
- **Images:** Optimize before upload (compress if >2MB)

## 📱 Mobile Responsiveness

- Fully responsive grid layout
- Touch-friendly buttons and forms
- Responsive tables with horizontal scroll
- Mobile-optimized charts (Chart.js handles this)

## 🔒 Security Considerations

- ✅ `secure_filename()` for all uploads
- ✅ CSRF protection via Flask sessions
- ✅ No sensitive data in frontend
- ✅ SQL injection safe (SQLAlchemy ORM)
- ⚠️ Set strong `SECRET_KEY` in production
- ⚠️ Use HTTPS in production
- ⚠️ Implement rate limiting for API

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- [Chart.js](https://www.chartjs.org/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Multi-user authentication
- Recurring expense detection
- Export to CSV/PDF
- Budget alerts & notifications
- Mobile app (React Native)
- Dark mode
- Receipt image rotation detection

## 📄 License

MIT License - Free for personal and commercial use

## 👤 Author

**Vikas Thakur**  
GitHub: [@Vikas8346](https://github.com/Vikas8346)

---

Made with ❤️ using Flask, Claude AI, and OCR technology

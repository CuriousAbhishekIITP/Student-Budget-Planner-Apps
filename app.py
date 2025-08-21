
from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Required for server environments
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# File to store transactions
CSV_FILE = 'transactions.csv'

# Initialize CSV file with headers if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Category', 'Type', 'Amount', 'Description'])

def calculate_summary():
    """Calculate financial summary from transactions"""
    income = 0
    expenses = 0
    category_spending = {}
    transactions = []

    # Read transactions
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                amount = float(row['Amount'])
            except ValueError:
                continue
            
            if row['Type'] == 'Income':
                income += amount
            else:
                expenses += amount
                category_spending[row['Category']] = category_spending.get(row['Category'], 0) + amount
            
            transactions.append(row)

    # Calculate balance
    balance = income - expenses
    
    # Get top 3 spending categories
    top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return income, expenses, balance, top_categories, transactions

def generate_bar_chart():
    """Generate bar chart of expenses by category"""
    _, _, _, top_categories, _ = calculate_summary()
    
    if not top_categories:
        return None
    
    categories = [item[0] for item in top_categories]
    amounts = [item[1] for item in top_categories]
    
    plt.figure(figsize=(8, 4))
    plt.bar(categories, amounts, color=['#ff6b6b', '#4ecdc4', '#ffe66d'])
    plt.title('Top Spending Categories')
    plt.xlabel('Categories')
    plt.ylabel('Amount ($)')
    
    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    
    return image_base64

@app.route('/')
def index():
    """Main page with form and recent transactions"""
    income, expenses, balance, top_categories, transactions = calculate_summary()
    chart_image = generate_bar_chart()
    recent_transactions = transactions[-5:]  # Last 5 transactions
    
    return render_template('index.html', 
                           income=income, 
                           expenses=expenses, 
                           balance=balance,
                           top_categories=top_categories,
                           recent_transactions=recent_transactions,
                           chart_image=chart_image)

@app.route('/add', methods=['POST'])
def add_transaction():
    """Add a new transaction"""
    date = request.form['date']
    category = request.form['category']
    trans_type = request.form['type']
    amount = float(request.form['amount'])
    description = request.form['description']

    # Save to CSV
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, trans_type, amount, description])
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Change this to a random secret key

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    income = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(3), nullable=False, default='PLN')

    expenses = db.relationship('Expense', back_populates='user', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=True)

    user = db.relationship('User', back_populates='expenses')
    category = db.relationship('Category', back_populates='expenses')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    expenses = db.relationship('Expense', back_populates='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

@app.route('/')
def home():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        return render_template('home.html', user=user)
    return render_template('home.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission, e.g., save data or send email
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Implement your logic here
        return render_template('contact.html', success=True)
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('signup'))
        
        # Create a new user with hashed password
        new_user = User(email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Sign up successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if the user exists
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home page
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/app', methods=['GET', 'POST'])
def functional_app():
    user = User.query.get(session.get('user_id'))
    if not user:
        flash('Please log in to access the app.', 'warning')
        return redirect(url_for('login'))

    categories = Category.query.all()

    if request.method == 'POST':
        # Handle form submissions (income update, add expense, etc.)
        if 'income' in request.form:
            try:
                user.income = float(request.form.get('income'))
                user.currency = request.form.get('currency')
                db.session.commit()
                flash('Income updated successfully!', 'success')
            except ValueError:
                flash('Invalid income value.', 'danger')
        elif 'category' in request.form and 'amount' in request.form and 'date' in request.form:
            try:
                category_id = int(request.form.get('category'))
                amount = float(request.form.get('amount'))
                date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()

                # Check if an expense already exists for this category (ignoring date)
                existing_expense = Expense.query.filter_by(
                    user_id=user.id,
                    category_id=category_id
                ).first()

                if existing_expense:
                    # Add the new amount to the existing expense amount
                    existing_expense.amount += amount  # Changed from existing_expense.amount = amount
                    existing_expense.date = date  # Optionally update the date
                    flash('Expense amount added successfully!', 'success')
                else:
                    # Create a new expense
                    new_expense = Expense(
                        user_id=user.id,
                        category_id=category_id,
                        amount=amount,
                        date=date
                    )
                    db.session.add(new_expense)
                    flash('Expense added successfully!', 'success')

                db.session.commit()
            except ValueError:
                flash('Invalid expense data.', 'danger')
            except Exception as e:
                db.session.rollback()
                flash('Error adding expense. Please try again.', 'danger')

    # Calculate current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Calculate total expenses
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user.id,
        func.extract('year', Expense.date) == current_year,
        func.extract('month', Expense.date) == current_month
    ).scalar() or 0.0

    # Fetch individual expenses
    individual_expenses = Expense.query.filter(
        Expense.user_id == user.id,
        func.extract('year', Expense.date) == current_year,
        func.extract('month', Expense.date) == current_month
    ).all()

    # Safeguard against NoneType for income
    income = user.income if user.income is not None else 0.0

    # Calculate saved money
    saved_money = income - total_expenses

    # Prepare data for Chart.js
    monthly_expenses = db.session.query(
        Category.name.label('category_name'),
        func.sum(Expense.amount).label('total_amount')
    ).join(Expense).filter(
        Expense.user_id == user.id,
        func.extract('year', Expense.date) == current_year,
        func.extract('month', Expense.date) == current_month
    ).group_by(Category.name).all()

    # Prepare chart labels and values
    chart_labels = [expense.category_name for expense in monthly_expenses]
    chart_values = [float(expense.total_amount) for expense in monthly_expenses]

    return render_template(
        'app.html',
        user=user,
        total_expenses=total_expenses,
        individual_expenses=individual_expenses,
        categories=categories,
        chart_labels=json.dumps(chart_labels),
        chart_values=json.dumps(chart_values),
        saved_money=saved_money,
        current_month=current_month,
        current_year=current_year,
        monthly_expenses=monthly_expenses  # Ensure this is passed if used in the template
    )

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        flash('Please log in to edit expenses.', 'danger')
        return redirect(url_for('login'))

    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != session['user_id']:
        flash('You do not have permission to edit this expense.', 'danger')
        return redirect(url_for('functional_app'))

    if request.method == 'POST':
        category_id = request.form.get('category')  # Assuming category ID is sent
        try:
            expense.category_id = int(category_id)  # Assign category ID
            expense.amount = float(request.form.get('amount'))
            expense.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            db.session.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('functional_app'))
        except ValueError:
            flash('Invalid input. Please check your data.', 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error updating expense. Please try again.', 'danger')

    categories = Category.query.all()  # Fetch categories to populate the form
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 401

    user_id = session['user_id']
    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != user_id:
        return jsonify({'success': False, 'message': 'You do not have permission to delete this expense.'}), 403

    try:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully!', 'success')
        return jsonify({'success': True}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting expense: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting the expense.'}), 500

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name').strip()
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            flash('Category already exists. Please use a different name.', 'danger')
            return redirect(url_for('add_category'))

        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('functional_app'))

    categories = Category.query.all()  # Fetch categories to pass to the template
    return render_template('add_category.html', categories=categories)  # Pass categories to the template

@app.route('/expenses')
def view_expenses():
    if 'user_id' not in session:
        flash('Please log in to view your expenses.', 'danger')
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    expenses = Expense.query.filter_by(user_id=user.id).all()  # Fetch all expenses for the logged-in user

    return render_template('view_expenses.html', user=user, expenses=expenses)

@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category_to_delete = Category.query.get_or_404(category_id)
    
    # Optional: Check if the category is associated with any expenses
    if category_to_delete.expenses:
        flash('Cannot delete category because it is associated with existing expenses.', 'danger')
        return redirect(url_for('add_category'))
    
    db.session.delete(category_to_delete)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('add_category'))

if __name__ == "__main__":
    app.run(debug=True) 
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth
from app.forms import LoginForm, RegistrationForm
from app.models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # Redirect to appropriate dashboard based on role
            if not next_page or not next_page.startswith('/'):
                if user.role == 'admin':
                    next_page = url_for('dashboard.admin_dashboard')
                elif user.role in ['inspector', 'sho']:
                    next_page = url_for('dashboard.inspector_dashboard')
                elif user.role == 'clerk':
                    next_page = url_for('clerk.dashboard')
                elif user.role == 'malkhana':
                    next_page = url_for('malkhana.dashboard')
                elif user.role == 'forensic':
                    next_page = url_for('forensic.dashboard')
                elif user.role == 'court':
                    next_page = url_for('court.dashboard')
                else:
                    next_page = url_for('dashboard.officer_dashboard')
            return redirect(next_page)
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data,
                    full_name=form.full_name.data, badge_number=form.badge_number.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html', title='Forgot Password')

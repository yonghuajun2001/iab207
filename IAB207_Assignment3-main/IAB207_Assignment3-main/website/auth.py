from flask import Blueprint, flash, render_template, request, url_for, redirect
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User
from .forms import LoginForm,RegisterForm
from flask_login import login_user, login_required,logout_user
from . import db

#create a blueprint
authbp = Blueprint('auth', __name__)

#Login
@authbp.route('/Login',methods=['GET','POST'])
def login():
    loginform = LoginForm()
    error=None
    if(loginform.validate_on_submit()==True):
        username = loginform.username.data
        password = loginform.password.data
        u1 = User.query.filter_by(name=username).first()
        # need database in models for "User"
        if u1 is None:
            error='User does not exist or invalid username'
        #check the password - notice password hash function
        elif not check_password_hash(u1.password_hash, password): # takes the hash and password
            error='Incorrect password'
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(u1)
            flash('Succesfully login')
            return redirect(url_for('main.index'))
        else:
            flash(error)
    return render_template('user.html',form=loginform, heading='Login')


#Logout  
@authbp.route('/Logout')
@login_required
def logout():
    logout_user()
    flash('Logout Succesfully')
    return redirect(url_for('main.index'))

#Register
@authbp.route('/Register',methods=['GET','POST'])
def register():
    register = RegisterForm()
    if (register.validate_on_submit() == True):
            #get data from the form 
            username = register.name.data
            email = register.email.data
            password = register.password.data
            phone_num = register.phone.data
            address1 = register.address.data
            # Need database in models for 'User' 
            u1 = User.query.filter_by(name=username).first()
            if u1:
                flash('User name already exists, please login')
                return redirect(url_for('auth.login'))
            p1 = User.query.filter_by(phone=phone_num).first()
            if p1:
                flash('Phone number registered, Please try another phone number')
                return redirect(url_for('auth.register'))
            # don't store the password - create password hash
            pwd_hash = generate_password_hash(password)
            #create a new user model object
            new_user = User(name=username, emailid=email,password_hash=pwd_hash,phone=phone_num,address=address1)
 
            db.session.add(new_user)
            db.session.commit()
            #commit to the database and redirect to HTML page
            flash('Succesfully Register, please log in.')
            return redirect(url_for('auth.login'))
    #the else is called when there is a get message
    else:
        return render_template('user.html', form=register, heading='Register')





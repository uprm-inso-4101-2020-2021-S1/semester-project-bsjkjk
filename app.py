from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from datetime import datetime
import os

app = Flask(__name__)
#variable DEV used for testing: it uses a sqlite dabatase to test, else: it uses heroku postgresql's database
DEV = False

if DEV == False:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.secret_key = os.environ.get('SECRET_KEY')

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cfr.db'
    app.secret_key = 'somerandomsecretkey'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login = LoginManager(app)

## table used for storing fault reports ##
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fault_type = db.Column(db.String(10), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self, fault_type, content, username, email, date_created):
        self.fault_type = fault_type
        self.content = content
        self.username = username
        self.email = email
        self.date_created = date_created
        return '<Fault Report %r>' % self.id

## table used for storing account information ##
class Accounts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    account_username = db.Column(db.String(15), unique=True, nullable=False)
    account_email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)

    def __repr__(self, account_username, account_email, password):
        self.account_username = account_username
        self.account_email = account_email
        self.password = password
        return '<Account %r>' % self.id

##### Account and admin stuff ########################
@login.user_loader
def load_user(user_id):
    return Accounts.query.get(int(user_id))

class LoginForm(FlaskForm):
    """ Login Form """

    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    #pasword min and max might get changed to 8 and 80 respectively
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=15)])
    remember = BooleanField('remember me')

class SignUpForm(FlaskForm):
    """ SignUp Form """

    username = StringField('username_label',
        validators=[InputRequired(), Length(min=4, max=15, message="Username must be between 4 and 15 characters")])
    email = StringField('email_label', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password_label',
        validators=[InputRequired(), Length(min=6, max=15, message="Password must be between 6 and 15 characters")])
    confirm_pswd = PasswordField('confirm_pswd_label', validators=[InputRequired(), EqualTo('password', message="passwords must match")])
    user_agree = BooleanField('agreement')
    submit_button = SubmitField('Sign Up')

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('signIn'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(Accounts, db.session))

##########################################################

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        form = request.form
        for field in form:
            if form[field] == "":
                return redirect('/')
        report_username = request.form['username']
        report_email = request.form['email']
        report_type = request.form['fault_type']
        report_content = request.form['content']
        new_report = Report(username=report_username, email=report_email, fault_type=report_type, content=report_content)

        try:
            db.session.add(new_report)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding report.'
    else:
        query_reports = Report.query.order_by(Report.date_created).all()
        query_reports = reversed(query_reports)
        reports = []
        index = 0
        for report in query_reports:
            if index > 7:
                break
            reports.append(report)
            index += 1

        return render_template("index.html", reports=reports)


@app.route('/allReports')
def allReports():
        reports = Report.query.order_by(Report.date_created).all()
        reports = reversed(reports)
        return render_template("allReports.html", reports=reports)

###################Sign Up/Sign In routes (and LogOut)####################################
@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    reg_form = SignUpForm()

    if reg_form.validate_on_submit():
        form  = request.form
        for field in form:
            if form[field] == "":
                return redirect('/SignUp')
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_account = Accounts(account_username=username, account_email=email, password=password)
        try:
            db.session.add(new_account)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem creating new account.'
    else:
        return render_template("signup.html", form=reg_form)

@app.route('/signIn')
def signIn():
    #username = request.form['username']
    #user = Accounts.query.get_or_404(current_user)
    #login_user(user)
    return render_template("signIn.html")

@app.route('/logOut')
@login_required
def logOut():
    logout_user()
    return redirect('/signIn')
##############################################################################

@app.route('/contactAAA')
def contactAAA():
    return render_template("contactAAA.html")

@app.route('/contactAEE')
def contactAEE():
    return render_template("contactAEE.html")

@app.route('/contactDACO')
def contactDACO():
    return render_template("contactDACO.html")

@app.route('/delete/<int:id>')
def delete(id):
    report_to_delete = Report.query.get_or_404(id)
    try:
        db.session.delete(report_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    report = Report.query.get_or_404(id)

    if request.method == 'POST':
        report.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updatin your report.'
    else:
        return render_template('update.html', report=report)



if __name__ == "__main__":
    app.run() #debug=True, port = 5001

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://spfuntodxqvpaf:89bed639820cfd6b6a171efc9574fe88604059843315341a305f61d17e581e63@ec2-107-20-15-85.compute-1.amazonaws.com:5432/d8lljt8rmrco0d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



## table used for storing fault reports ##
class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    fault_type = db.Column(db.String(10), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    report_username = db.Column(db.String(15), unique=True, nullable=False)
    report_email = db.Column(db.String(15), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Fault Report %r>' % self.report_id

## table used for storing account information ##
class Accounts(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    account_username = db.Column(db.String(15), unique=True, nullable=False)
    account_email = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return '<Account %r>' % self.user_id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        form = request.form
        for field in form:
            if form[field] == "":
                return redirect('/')
        report_username = request.form['report_username']
        report_email = request.form['report_email']
        report_type = request.form['fault_type']
        report_content = request.form['content']
        new_report = Report(report_username=report_username, report_email=report_email, fault_type=report_type, content=report_content)

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

###################Sign Up/Sign In routes####################################
@app.route('/signUp')
def signUp():
    return render_template("signup.html")

@app.route('/signIn')
def signIn():
    return render_template("signIn.html")
##############################################################################

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

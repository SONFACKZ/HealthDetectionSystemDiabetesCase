from flask import Flask, flash, session, request, redirect, url_for, jsonify, render_template
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import numpy as np
import pandas as pd
import pickle

app = Flask(__name__, static_url_path='/static')

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#Database setting
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Z@ne091262'
app.config['MYSQL_DB'] = 'hci'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)





model = pickle.load(open('model.pkl', 'rb'))

dataset = pd.read_csv('diabetes.csv')

dataset_X = dataset.iloc[:,[1, 2, 5, 7]].values

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0,1))
dataset_scaled = sc.fit_transform(dataset_X)

@app.route('/')
@app.route("/home")
def home():
    return render_template("home.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        status = request.form['status']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (status, username, email, password) VALUES (%s, %s, %s, %s)",(status, username, email, hash_password,))
        mysql.connection.commit()
        session['username'] = username
        session['email'] = email
        return redirect(url_for("home"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE username =%s",(username,))
        user = cur.fetchone()
        cur.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user ['password'].encode('utf-8'):
                session['username'] = user['username']
                session['email'] = user['email']
                return render_template("home.html")
            else:
                flash('Error password or username  not match')
                return render_template("login.html")
        else:
            flash('Error password or username  not match')
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")
# def home():
#     return render_template("home.html")

# @app.route('/newpatient')
# def newpatient():
#     return render_template('newpatient.html')

@app.route('/newpatient', methods=['GET', 'POST'])
def newpatient():
    if request.method == 'GET':
        return render_template("newpatient.html")
    else:
        fullname = request.form['fullname']
        residence = request.form['residence']
        email = request.form['email']
        phone = request.form['phone']
        parentname = request.form['parentname']
        parentphone = request.form['parentphone']
        age = request.form['age']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients (fullname, residence, email, phone, parentname, parentphone, age) VALUES (%s, %s, %s, %s, %s, %s, %s)",(fullname, residence, email, phone, parentname, parentphone, age,))
        mysql.connection.commit()
        flash('New partient Registered successfuly')
        return redirect(url_for("newpatient"))


@app.route('/existpatient', methods=['GET', 'POST'])
def existpatient():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM patients")
    datas = cur.fetchall()#data frim database
    return render_template("existpatient.html", rows = datas)
    
@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM patients WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('existpatient'))


# @app.route('/update',methods=['POST','GET'])
# def update():

#     if request.method == 'POST':
#         id_data = request.form['id']
#         name = request.form['name']
#         email = request.form['email']
#         phone = request.form['phone']
#         cur = mysql.connection.cursor()
#         cur.execute("""
#                UPDATE students
#                SET name=%s, email=%s, phone=%s
#                WHERE id=%s
#             """, (name, email, phone, id_data))
#         flash("Data Updated Successfully")
#         mysql.connection.commit()
#         return redirect(url_for('Index'))


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/manage')
def manage():
    return render_template('manage.html')



@app.route('/predict')
def predict():
    # return render_template('predict.html')
    '''
    For rendering results on HTML GUI
    '''
    float_features = [float(x) for x in request.form.values()]
    final_features = [np.array(float_features)]
    prediction = model.predict( sc.transform(final_features) )

    if prediction == 1:
        pred = "You have Diabetes, please consult a Doctor."
    elif prediction == 0:
        # prob = positive_percent= model.predict_proba(X_test)[0][1]*100
        # sprob = str(prob)
        nothave = "The probablity for you to have diabete in the future is"
        pred = "You don't have Diabetes." + nothave
    output = pred

    return render_template('predict.html', prediction_text='{}'.format(output))

if __name__ == "__main__":

    app.run(debug=True)

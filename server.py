from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import mysql.connector
import datetime
import json
import ot
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message
from threading import Thread
import os

app = Flask(__name__)
app.secret_key = 'UniqueStudioCooperationedit'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = datetime.timedelta(seconds=1)
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# 获取环境变量中的账号和密码
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# app.config['MAIL_DEBUG'] = True
app.config['MAIL_SUPPRESS_SEND'] = False

mail = Mail(app)

con = mysql.connector.connect(
    user='root', password='MySQL#232', database='CooperationEdit', port=3305, use_unicode=True
)
cursor = con.cursor()


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


@app.route('/', methods=['GET'])
def editpage():
    return render_template('editpage.html')

# 用户登录


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cursor.execute(
            "select pw from userdetail where username = %s", (username, ))
        result = cursor.fetchall()
        print(result)
        if result == []:
            flash('用户名不存在')
            return render_template("login.html", **{'username': "" if (username == None) else username})
        elif not check_password_hash(result[0][0], password):
            flash('密码错误')
            return render_template("login.html", **{'username': "" if (username == None) else username})
        else:
            print(result[0][0])
            # session['login_user'] = result[0][0]
            return redirect(url_for('editpage'))


# 处理注册请求


@app.route('/register', methods=['POST', 'GET'])
def userregister():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        useremail = request.form.get('email')
        password = request.form.get('password1')
        hashed_pw = generate_password_hash(
            password, method='pbkdf2:sha1', salt_length=8)
        cursor.execute(
            "select * from userdetail where username = %s", (username,))
        if (cursor.fetchall() == []):
            cursor.execute('select max(id) from userdetail')
            id = cursor.fetchall()[0][0]
            cursor.execute("insert into userdetail (username, pw, email, rgtime, id) values (%s, %s, %s, %s, %s)",
                           (username, hashed_pw, useremail, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id+1))
            con.commit()
            print(username, useremail, password)
            return redirect(url_for('login'))
        else:
            flash('该用户名已被使用')
            return render_template('register.html', **{'username': "" if username == None else username})


# 重置密码


@app.route('/resetpw', methods=['POST', 'GET'])
def resetpw():
    if request.method == 'GET':
        return render_template('resetpw.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        cursor.execute(
            "select username, id from userdetail where email = %s", (email,))
        result = cursor.fetchall()
        username = result[0][0]
        id = result[0][1]
        if result == []:
            flash("您输入的邮箱不存在")
        else:
            print(os.environ.get('MAIL_USERNAME'),
                  os.environ.get('MAIL_PASSWORD'))
            msg = Message(subject="重置密码", sender=os.environ.get('MAIL_USERNAME'),
                          recipients=[email])
            msg.html = render_template('resetpw_email.html', **{
                                       'username': username, 'token': Serializer(app.secret_key, 300).dumps({'confirm': id})})
            thread = Thread(target=send_async_email, args=[app, msg])
            thread.start()
            return "<h1>密码重置邮件发送成功，五分钟内有效，请注意查收</h1>"
        # return render_template('resetpw_email.html', **{'username': username, 'token': Serializer(app.secret_key, 3600).dumps({'confirm': id})})


@app.route('/<username>/resetpw/<token>', methods=['GET', 'POST'])
def email_resetpw(username, token):
    if request.method == 'POST':
        s = Serializer(app.secret_key)
        cursor.execute(
            "select id from userdetail where username=%s", (username,))
        id = cursor.fetchall()[0][0]
        try:
            data = s.loads(token)
        except:
            return '略略略'
        if data.get('confirm') != id:
            return '略略略'
        else:
            newpw = request.form.get('newpw')
            hashed_newpw = generate_password_hash(
                newpw, method='pbkdf2:sha1', salt_length=8)
            cursor.execute(
                "update userdetail set pw = %s where username = %s", (hashed_newpw, username))
            con.commit()
            flash('密码修改成功')
            return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('setnewpw.html', **{'url': request.url})

    # 请求版本号


@app.route('/<username>/<docname>/requestversion', methods=['GET', 'POST'])
def rqversion(username, docname):
    # print('username = {}, docname = {}'.format(username, docname))
    cursor.execute(
        "select max(version) from docs where username = %s and docname = %s", (username, docname))
    result = cursor.fetchall()
    print(result)
    print(type(str(result[0][0])))
    return '0' if result[0][0] == None else str(result[0][0])

# 请求最新版本


@app.route('/<username>/<docname>/rqnewestdoc', methods=['GET', 'POST'])
def rqnewestdoc(username, docname):
    print(request.get_data().decode())
    print(type(request.get_data().decode()))

    # print(version)
    # print(type(version))
    cursor.execute(
        "select max(version) from docs where username = %s and docname = %s", (username, docname))
    version = cursor.fetchall()[0][0]
    print(version)
    print(int(request.get_data().decode()))
    print(version == int(request.get_data().decode()))
    if version > int(request.get_data().decode()):
        cursor.execute("select doc from docs where username = %s and docname = %s and version = (select max(version) from docs where username = %s and docname = %s)",
                       (username, docname, username, docname))
        return jsonify(cursor.fetchall()[0][0])
    else:
        return jsonify(None)

    # result = cursor.fetchall()
    # print(result[0][0])

    # print(type(result[0][0]))
    '''if result:
        if int(result[0][0]) > int(request.get_data().decode()):
            return jsonify(result[0][0])
        else:
            return jsonify('')
    else:
        return None'''
    # return None


@app.route('/<username>/<docname>/firstdoc')
def firstdoc(username, docname):
    cursor.execute("select doc from docs where username = %s and docname = %s and version = (select max(version) from docs where username = %s and docname = %s)",
                   (username, docname, username, docname))
    return jsonify(cursor.fetchall()[0][0])

# merge changeset


@app.route('/<username>/<docname>/merge', methods=['GET', 'POST'])
def merge(username, docname):
    changeset = json.loads(request.get_data().decode())
    # changeset = ot.Changeset(data['actions'], data['localversion'])
    cursor.execute(
        "select * from docs where username = %s and docname = %s and version = (select max(version) from docs where username = %s and docname = %s)", (username, docname, username, docname))
    result = cursor.fetchall()
    curent_version = int(result[0][2])
    doc = result[0][4]
    print(changeset['version'])
    print(type(changeset['version']))
    print(curent_version)
    print(type(curent_version))
    # print('changeset.version = ', str(changeset['version']))
    # print('curent_version = ', str(curent_version))
    if changeset['version'] == curent_version:
        print("现在版本相同")
        newdoc = ot.applychangeset(changeset['actions'], doc)
        cursor.execute("insert into docs (username, docname, version, changeset, doc, date) values (%s, %s, %s, %s, %s, %s)",
                       (username, docname, curent_version+1, str(changeset['actions']), newdoc, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        print(newdoc)
        return jsonify([])
    elif changeset['version'] < curent_version:
        cursor.execute(
            "select changeset , version from docs where username = %s and docname = %s order by version asc", (username, docname))
        server_changeset = []
        for data in cursor.fetchall()[changeset['version']:]:
            if data[0] != '':
                result_changeset = eval(data[0])
                for item in result_changeset:
                    server_changeset.append(item)
        # print(server_changeset)
        response_changeset, server_changeset = ot.ot(
            changeset['actions'], server_changeset)
        # server_changeset = ot.ot(server_changeset, changeset['actions'])
        newdoc = ot.applychangeset(server_changeset, doc)
        print(newdoc)
        # print(applychangeset(response_changeset, '789'))
        cursor.execute("insert into docs (username, docname, version, changeset, doc, date) values (%s, %s, %s, %s, %s, %s)",
                       (username, docname, curent_version+1, str(server_changeset), newdoc, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        return jsonify(response_changeset)
        # print(response_changeset)
        # print(server_changeset)


if __name__ == '__main__':

    app.run(debug=True)

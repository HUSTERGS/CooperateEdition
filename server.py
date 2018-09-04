from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import mysql.connector
import datetime
import json
import ot
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message
from flask_login import login_required, UserMixin, login_user, LoginManager, logout_user, current_user
from threading import Thread
import os
import hashlib
import identicon
import random
from glob import glob

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
app.config['JSON_AS_ASCII'] = False

mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
con = mysql.connector.connect(
    user='root', password='MySQL#232', database='CooperationEdit', port=3305, use_unicode=True
)
cursor = con.cursor()


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


class User(UserMixin):
    def __init__(self, userdetail):
        self.username = userdetail[0]
        self.pw = userdetail[1]
        self.email = userdetail[2]
        self.rgtime = userdetail[3]
        self.id = userdetail[4]


def gen_avatar_batch(code, size, dir):
    img = identicon.render_identicon(code, 16)
    img.save(dir + '%s_%s.png' % (code, size))

def gen_unique_num(date):
    datenum = date.replace("-",'').replace(':','').replace(' ','')
    randomNum=random.randint(0,100)
    if randomNum <= 10:
        randomNum = str(0) + str(randomNum)
    uniqueNum= datenum + str(randomNum)
    return uniqueNum


@login_manager.user_loader
def load_user(user_id):
    cursor.execute("select * from userdetail where id = %s", (user_id,))
    return User(cursor.fetchall()[0])


@app.route('/', methods=['GET'])
def editpage():
    return render_template('editpage.html')

# 用户登录


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('userdetail', username = current_user.username))
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
            cursor.execute(
                "select * from userdetail where username = %s", (username,))

            print(result[0][0])
            user = User(cursor.fetchall()[0])
            login_user(user)
            #session['username'] = username
            # session['login_user'] = result[0][0]
            print(user.rgtime)
            return redirect(url_for('userdetail', username = user.username))


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
            date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute("insert into userdetail (username, pw, email, rgtime, id) values (%s, %s, %s, %s, %s)",
                           (username, hashed_pw, useremail, date, id+1))
            cursor.execute("insert into userdocs (username, docs, lastedit, friends) values (%s, %s, %s, %s)", (username, str([]), '', str([])))
            con.commit()
            #服务端生成用户图片
            os.mkdir('./static/usericon/'+username)
            dirloc = "./static/usericon/"+username+'/'
            uniquenum = gen_unique_num(date)
            gen_avatar_batch(uniquenum, 16, dirloc)
            
            return redirect(url_for('login'))
        else:
            flash('该用户名已被使用')
            return render_template('register.html', **{'username': "" if username == None else username})




@app.route('/userdetail/<username>')
@login_required
def userdetail(username):
    dirloc = './static/usericon/' + username + '/' + '*.png'
    glob(dirloc)
    # + str(user.rgtime).replace("-",'').replace(':','').replace(' ','') + '_16.png'
    print(dirloc)
    print(glob(dirloc))
    current_user.icon_url = '.' + glob(dirloc)[0].replace('\\', '/')
    return render_template('userdetail.html', **{'user_icon_url': current_user.icon_url})
    
    
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
        if result == []:
            flash("您输入的邮箱不存在")
            return render_template('resetpw.html')
        else:
            username = result[0][0]
            id = result[0][1]
            print(os.environ.get('MAIL_USERNAME'),
                  os.environ.get('MAIL_PASSWORD'))
            msg = Message(subject="重置密码", sender=os.environ.get('MAIL_USERNAME'),
                          recipients=[email])
            msg.html = render_template('resetpw_email.html', **{
                                       'username': username, 'token': Serializer(app.secret_key, 300).dumps({'confirm': id})})
            thread = Thread(target=send_async_email, args=[app, msg])
            thread.start()
            flash("重置邮件已发送，五分钟内有效")
            return redirect(url_for('login'))
        # return render_template('resetpw_email.html', **{'username': username, 'token': Serializer(app.secret_key, 3600).dumps({'confirm': id})})

# 邮件中的重置密码链接
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
    #print(result)
    #print(type(str(result[0][0])))
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
    print(username, docname)
    cursor.execute("select doc from docs where username = %s and docname = %s and version = (select max(version) from docs where username = %s and docname = %s)",
                   (username, docname, username, docname))
    return jsonify(cursor.fetchall()[0][0])

# merge changeset


@app.route('/<username>/<docname>/merge', methods=['GET', 'POST'])
def merge(username, docname):
    changeset = json.loads(request.get_data().decode())
    print(changeset['actions'])
    print(username,docname)
    # changeset = ot.Changeset(data['actions'], data['localversion'])
    cursor.execute(
        "select * from docs where username = %s and docname = %s and version = (select max(version) from docs where username = %s and docname = %s)", (username, docname, username, docname))
    result = cursor.fetchall()
    curent_version = int(result[0][2])
    doc = result[0][4]
    #print(changeset['version'])
    #print(type(changeset['version']))
    #print(curent_version)
    #print(type(curent_version))
    # print('changeset.version = ', str(changeset['version']))
    # print('curent_version = ', str(curent_version))

    print(changeset['actions'])
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


@app.route('/userdoc/<username>/<target>')
@login_required
def rspuserdoc(username, target):
    if target == 'all-docs':
        cursor.execute(
            "select docs from userdocs where username = %s", (username,))
        docs = eval(cursor.fetchall()[0][0])
    elif target == 'mydocs':
        cursor.execute(
            "select docs from userdocs where username = %s", (username,))
        docs = eval(cursor.fetchall()[0][0])
    elif target == 'share-with-me':
        cursor.execute(
            "select docs from userdocs where username = %s", (username,))
        docs = eval(cursor.fetchall()[0][0])
    elif target == 'garbage':
        cursor.execute(
            "select docs from userdocs where username = %s", (username,))
        docs = eval(cursor.fetchall()[0][0])
    return jsonify(docs)


@app.route('/userdoc/<username>/new', methods=['GET', 'POST'])
@login_required
def newdoc(username):
    docname = '无标题文档'
    print(username)
    cursor.execute(
        "select docs from userdocs where username = %s", (username,))
    docs = eval(cursor.fetchall()[0][0])
    print(type(docs))
    # 如果名称重复
    num = 1
    newname = docname
    while newname in docs:
        newname = docname
        newname = newname + '(' + str(num) + ')'
        num += 1

    docs.append(newname)
    cursor.execute("update userdocs set docs = %s where username = %s",
                   (str(docs), username))
    cursor.execute("insert into docs (username, docname, version, changeset, doc, date) values (%s, %s, %s, %s, %s, %s)",
                       (username, newname, 0 , '[]' , '', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    con.commit()
    dirloc = './static/usericon/' + username + '/' + '*.png'
    return render_template('editpage.html', **{'username': username, 'docname': newname, 'user_icon_url': '../../' + glob(dirloc)[0].replace('\\', '/')})


@app.route('/logout')  # logout and pop out user data
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.context_processor  # handler
def my_context_processor():
    login_user = session.get('username', '')
    return {'login_user': login_user}


if __name__ == '__main__':

    app.run(debug=True)

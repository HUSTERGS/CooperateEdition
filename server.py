from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import datetime
import json

import ot

app = Flask(__name__)

con = mysql.connector.connect(
    user='root', password='MySQL#232', database='CooperationEdit', port=3305, use_unicode=True
)
cursor = con.cursor()


# table docs 顺序 username, docname, version, changeset, doc, date


@app.route('/', methods=['GET'])
def login():
    return render_template('editepage.html')


@app.route('/')
# 请求版本号
@app.route('/<username>/<docname>/requestversion', methods=['GET', 'POST'])
def rqversion(username, docname):
    #print('username = {}, docname = {}'.format(username, docname))
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

    #result = cursor.fetchall()
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
    #changeset = ot.Changeset(data['actions'], data['localversion'])
    cursor.execute(
        "select * from docs where username = %s and docname = %s and version = (select max(version) from docs where username = %s and docname = %s)", (username, docname, username, docname))
    result = cursor.fetchall()
    curent_version = int(result[0][2])
    doc = result[0][4]
    print(changeset['version'])
    print(type(changeset['version']))
    print(curent_version)
    print(type(curent_version))
    #print('changeset.version = ', str(changeset['version']))
    #print('curent_version = ', str(curent_version))
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
        #server_changeset = ot.ot(server_changeset, changeset['actions'])
        newdoc = ot.applychangeset(server_changeset, doc)
        print(newdoc)
        #print(applychangeset(response_changeset, '789'))
        cursor.execute("insert into docs (username, docname, version, changeset, doc, date) values (%s, %s, %s, %s, %s, %s)",
                       (username, docname, curent_version+1, str(server_changeset), newdoc, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        return jsonify(response_changeset)
        # print(response_changeset)
        # print(server_changeset)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import datetime
import json
app = Flask(__name__)

con = mysql.connector.connect(
    user='root', password='MySQL#232', database='CooperationEdit', port=3305, use_unicode=True
)
cursor = con.cursor()


class Step(object):
    def __init__(self, type, content, index):
        self.type = type
        self.content = content
        self.index = index


class Op(object):
    def __init__(self, changeset, version):
        self.changeset = changeset[:]
        self.version = version


def applychangeset(actions, doc):
    for action in actions:
        if action['type'] == 'insert':
            doc = doc[:action['index']] + \
                action['content'] + doc[action['index']:]
        elif action['type'] == 'delete':
            doc = doc[:action['index']-1] + doc[action['index']:]
    return doc


''' def follow(step1, step2):
    if step1 == None or step2 == None:
        return step2
    if step1['type'] == step2['type'] == 'insert':
        return Step('insert', step2['content'], step2['index'] if step1['index'] > step2['index'] else step2['index'] + 1)
    elif step1['type'] == 'insert' and step2['type'] == 'delete':
        return Step('delete', None, step2['index'] + 1 if step1['index'] < step2['index'] else step2['index'])
    elif step1['type'] == 'delete' and step2['type'] == 'insert':
        return Step('insert', step2['content'], step2['index'] if step1['index'] > step2['index'] else step2['index'] - 1)
    elif step1['type'] == step2['type'] == 'delete':
        if step1['index'] > step2['index']:
            return Step('delete', None, step2['index'])
        elif step2['index'] < step2['index']:
            return Step('delete', None, step2['index'] - 1)
        else:
            return None'''


def follow(step1, step2):
    if step1 == None or step2 == None:
        return step2
    if step1.type == step2.type == 'insert':
        return Step('insert', step2.content, step2.index if step1.index > step2.index else step2.index + 1)
    elif step1.type == 'insert' and step2.type == 'delete':
        return Step('delete', None, step2.index + 1 if step1.index < step2.index else step2.index)
    elif step1.type == 'delete' and step2.type == 'insert':
        return Step('insert', step2.content, step2.index if step1.index > step2.index else step2.index - 1)
    elif step1.type == step2.type == 'delete':
        if step1.index > step2.index:
            return Step('delete', None, step2.index)
        elif step2.index < step2.index:
            return Step('delete', None, step2.index - 1)
        else:
            return None

# table docs 顺序 username, docname, version, changeset, doc, date


@app.route('/', methods=['GET'])
def login():
    return render_template('editepage.html')


# 请求版本号
@app.route('/<username>/<docname>/requestversion', methods=['GET', 'POST'])
def rqversion(username, docname):
    print('username = {}, docname = {}'.format(username, docname))
    cursor.execute(
        "select * from docs where username = %s and docname = %s", (username, docname))
    result = cursor.fetchall()
    print(result)
    return '0' if result == [] else str(result[0][2])


@app.route('/<username>/<docname>/merge', methods=['GET', 'POST'])
def merge(username, docname):
    #str_changeset = request.get_data().decode()
    changeset = json.loads(request.get_data().decode())
    cursor.execute(
        "select * from docs where username = %s and docname = %s and version = (select max(version) from docs where username = %s and docname = %s)", (username, docname, username, docname))
    result = cursor.fetchall()
    curent_version = result[0][2]
    doc = result[0][4]
    print(changeset)
    if changeset.localversion == curent_version:
        newdoc = applychangeset(changeset.actions, doc)
        cursor.execute("insert into docs (username, docname, version, changeset, doc, date) values (%s, %s, %s, %s, %s, %s)",
                       (username, docname, curent_version+1, str(changeset), newdoc, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        print(newdoc)
    # elif changeset.localversion
    return '123'


if __name__ == '__main__':
    app.run(debug=True)

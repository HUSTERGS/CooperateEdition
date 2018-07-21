from flask import Flask, render_template, request, jsonify
from json import loads
app = Flask(__name__)

docversion = 0


class Step(object):
    def __init__(self, type, content, index):
        self.type = type
        self.content = content
        self.index = index


class Op(object):
    def __init__(self, changeset):
        self.changeset = changeset[:]


def applychangeset(op):
    pass


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


@app.route('/', methods=['GET'])
def login():
    return render_template('editepage.html')


@app.route('/merge', methods=['GET', 'POST'])
def edite():
    # print(request.get_data().decode())
    # return 'xs'
    temp = loads(request.get_data().decode())
    op = Op(temp['actions'])
    op.version = temp['localversion']
    if op.version == docversion:
        applychangeset(op)
    elif op.version < docversion:
        pass
    print(type(temp), type(temp['actions']))

    for step in temp['actions']:
        print(step['type'], step['content'], step['index'])
    return 'cds'


if __name__ == '__main__':
    app.run(debug=True)

# 收到的是基于某一个版本的changeset数组即ops
#op.version = number
# op.changeset = [step1, step2, step3...]
# step.type = 'insert' / 'delete'
# step.content = content
# step.index = number


class Step(object):
    def __init__(self, type, content, index):
        self.type = type
        self.content = content
        self.index = index


class Op(object):
    def __init__(self, changeset):
        self.changeset = changeset[:]


class CooperationDocument(object):
    def __init__(self, ops=[]):
        self.ops = ops[:]

    def follow(self, step1, step2):
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

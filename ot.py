# 收到的是基于某一个版本的changeset数组即ops
#op.version = number
# op.changeset = [actionA, actionB, step3...]
# step.type = 'insert' / 'delete'
# step.content = content
# step.index = number

from functools import reduce


def follow(actionA, actionB):
    if actionA == None or actionB == None:
        return actionB
    if actionA.type == actionB.type == 'insert':
        return Step('insert', actionB.content, actionB.index if actionA.index > actionB.index else actionB.index + 1)
    elif actionA.type == 'insert' and actionB.type == 'delete':
        return Step('delete', None, actionB.index + 1 if actionA.index < actionB.index else actionB.index)
    elif actionA.type == 'delete' and actionB.type == 'insert':
        return Step('insert', actionB.content, actionB.index if actionA.index > actionB.index else actionB.index - 1)
    elif actionA.type == actionB.type == 'delete':
        if actionA.index > actionB.index:
            return Step('delete', None, actionB.index)
        elif actionB.index < actionB.index:
            return Step('delete', None, actionB.index - 1)
        else:
            return None


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

    @staticmethod
    def ot(changesetA, changesetB):
        A_prime = []
        temp = changesetA[:]
        for action in changesetB.actions:
            temp.insert(0, action)
            result = reduce(lambda actionA, actionB: follow(
                actionB, actionA), temp)
            A_prime.append(result)
            temp = map(lambda action_in_B: follow(
                action_in_B, action), changesetA)
        return A_prime


class Action():
    def __init__(self, action):
        self.type = action['type']
        self.content = action['content']
        self.index = action['index']


class Changeset():
    def __init__(self, changeset, version):
        self.actions = changeset.actions[:]
        self.version = version

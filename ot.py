# 收到的是基于某一个版本的changeset数组即ops
#op.version = number
# op.changeset = [actionA, actionB, Action3...]
# Action.type = 'insert' / 'delete'
# Action.content = content
# Action.index = number

from functools import reduce


class Changeset():
    def __init__(self, actions, version):
        self.actions = actions[:]
        self.version = version


def Action(type, content, index):
    action = {}
    action['type'] = type
    action['content'] = content
    action['index'] = index
    return action


def follow(actionA, actionB):
    if actionA == None or actionB == None:
        print("NO")
    elif actionA['type'] == actionB['type'] == 'insert':
        if actionA['index'] > actionB['index']:
            pass
        else:
            actionB['index'] += 1
    elif actionA['type'] == 'insert' and actionB['type'] == 'delete':
        if actionA['index'] < actionB['index']:
            actionB['index'] += 1
        else:
            pass
    elif actionA['type'] == 'delete' and actionB['type'] == 'insert':
        if actionA['index'] > actionB['index']:
            pass
        else:
            actionB['index'] -= 1
    elif actionA['type'] == actionB['type'] == 'delete':
        if actionA['index'] > actionB['index']:
            pass
        elif actionB['index'] < actionB['index']:
            actionB['index'] -= 1
        else:
            actionB = None
    return actionB


def follow_wraper(actionA, actionB, temp):
    temp_actionA = actionA.copy() if actionA else None
    temp_actionB = actionB.copy() if actionB else None
    temp.append(follow(temp_actionB, temp_actionA))
    #print(actionA, actionB, follow(actionA, actionB))
    #print(actionB, actionA, follow(actionB, actionA))
    return follow(temp_actionA, temp_actionB)


def ot(changesetA, changesetB):
    A_prime = []
    temp = changesetA[:]
    for action in changesetB:
        temp_action = action.copy() if action else None
        temp2 = []
        temp.insert(0, temp_action)
        result = reduce(lambda actionA, actionB: follow_wraper(
            actionB, actionA, temp2), temp)
        A_prime.append(result)
        # temp = list(map(lambda action_in_B: follow(
        #    action_in_B, action), changesetA))
        temp = temp2
    B_prime = temp
    return A_prime, B_prime


def applychangeset(actions, doc):
    for action in actions:
        if action:
            if action['type'] == 'insert':
                doc = doc[:action['index']] + \
                    action['content'] + doc[action['index']:]
            elif action['type'] == 'delete':
                doc = doc[:action['index']-1] + doc[action['index']:]
    return doc

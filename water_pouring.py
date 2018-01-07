'''
Water pouring problem.
'''

import doctest

Fail = []


def pour_problem(X, Y, goal, start=(0, 0)):
    '''
    X and Y are the capacity of glasses; (x, y) is current fill levels and represents a state.
    The goal is a level that can be in either glass.
    Start at start state and follow successors until we reach the goal.
    Keep track of frotier and previously explored; fail when frontier.
    '''
    if goal in start:
        return [start]
    explored = set()  # set of states we have visited
    frontier = [[start]]  # ordered list of paths we have blazed
    while frontier:
        path = frontier.pop(0)
        (x, y) = path[-1]  # Last state in the first path of the frontier
        for (state, action) in successors(x, y, X, Y).items():
            if state not in explored:
                explored.add(state)
                path2 = path + [action, state]
                if goal in state:
                    return path2
                else:
                    frontier.append(path2)
    return Fail


def path_states(path):
    "Return a list of states in this path."
    return path[0::2]


def path_actions(path):
    "Return a list of actions in this path."
    return path[1::2]


def successors(x, y, X, Y):
    '''
    Return a dict of {state: action} pairs describing what can be reached
    from the (x, y) state, and how.
    '''
    assert x <= X and y <= Y  # (x, y) is glass levels; X and Y are glass size
    return {
        ((0, y + x) if y + x <= Y else (x - (Y - y), Y)): 'X->Y',
        ((x + y, 0) if x + y <= X else (X, y - (X - x))): 'X<-Y',
        (X, y): 'fill X',
        (x, Y): 'fill Y',
        (0, y): 'empty X',
        (x, 0): 'empty Y'
    }


def bridge_successors(state):
    """Return a dict of {state:action} pairs. A state is a (here, there, t) tuple,
    where here and there are frozensets of people (indicated by their times) and/or
    the 'light', and t is a number indicating the elapsed time. Action is represented
    as a tuple (person1, person2, arrow), where arrow is '->' for here to there and
    '<-' for there to here."""
    here, there, t = state
    light = 'light'
    if light in here:
        return dict(((here - frozenset([a, b, light]),
                      there | frozenset([a, b, light]), t + max(a, b)), (a, b,
                                                                         '->'))
                    for a in here
                    if a is not light for b in here if b is not light)
    else:
        return dict(((here | frozenset([a, b, light]),
                      there - frozenset([a, b, light]), t + max(a, b)), (a, b,
                                                                         '<-'))
                    for a in there
                    if a is not light for b in there if b is not light)


def bridge_successors2(state):
    """Return a dict of {state:action} pairs. A state is a
    (here, there) tuple, where here and there are frozensets
    of people (indicated by their travel times) and/or the light."""
    here, there = state
    light = 'light'
    if light in here:
        return dict(((here - frozenset([a, b, light]),
                      there | frozenset([a, b, light])), (a, b, '->'))
                    for a in here
                    if a is not light for b in here if b is not light)
    else:
        return dict(((here | frozenset([a, b, light]),
                      there - frozenset([a, b, light])), (a, b, '<-'))
                    for a in there
                    if a is not light for b in there if b is not light)


def bridge_problem(here):
    '''
    Find the fastest (least elapsed time) path to the goal in the bridge problem.
    '''
    here = frozenset(here) | frozenset(['light'])
    explored = set()  # set of states we have visited
    # State will be a (people-here, people-there, time-elapsed)
    # ordered list of path we have blazed
    frontier = [[(here, frozenset(), 0)]]
    if not here:
        return frontier[0]
    while frontier:
        path = frontier.pop(0)
        here, _, _ = last_state = path[-1]
        # Check for solution later when we pull best path
        if not here or here == set(['light']):
            return path
        for (state, action) in bridge_successors(last_state).items():
            if state not in explored:
                explored.add(state)
                here, _, _ = state
                path2 = path + [action, state]
                frontier.append(path2)
                frontier.sort(key=elapsed_time)
    return Fail


def elapsed_time(path):
    return path[-1][2]


def test_bridge():
    "tests."
    assert bridge_successors((frozenset([1, 'light']), frozenset([]), 3)) == {
        (frozenset([]), frozenset([1, 'light']), 4): (1, 1, '->')
    }

    assert bridge_successors((frozenset([]), frozenset([2, 'light']), 0)) == {
        (frozenset([2, 'light']), frozenset([]), 2): (2, 2, '<-')
    }

    print(path_actions(bridge_problem([1, 2, 5, 10])))

    here1 = frozenset([1, 'light'])
    there1 = frozenset([])

    here2 = frozenset([1, 2, 'light'])
    there2 = frozenset([3])

    here3 = frozenset([2])
    there3 = frozenset([1, 3, 'light'])

    assert bridge_successors2((here1, there1)) == {
        (frozenset([]), frozenset([1, 'light'])): (1, 1, '->')
    }
    assert bridge_successors2((here2, there2)) == {
        (frozenset([1]), frozenset(['light', 2, 3])): (2, 2, '->'),
        (frozenset([2]), frozenset([1, 3, 'light'])): (1, 1, '->'),
        (frozenset([]), frozenset([1, 2, 3, 'light'])): (2, 1, '->')
    }
    assert bridge_successors2((here3, there3)) == {
        (frozenset([1, 2, 3, 'light']), frozenset([])): (3, 1, '<-'),
        (frozenset([1, 2, 'light']), frozenset([3])): (1, 1, '<-'),
        (frozenset([2, 3, 'light']), frozenset([1])): (3, 3, '<-')
    }

    print('bridge tests pass')


class Test:
    '''
>>> successors(0, 0, 4, 9)
{(0, 9): 'fill Y', (0, 0): 'empty Y', (4, 0): 'fill X'}

>>> successors(3, 5, 4, 9)
{(4, 5): 'fill X', (4, 4): 'X<-Y', (3, 0): 'empty Y', (3, 9): 'fill Y', (0, 5): 'empty X', (0, 8): 'X->Y'}

>>> successors(3, 7, 4, 9)
{(4, 7): 'fill X', (4, 6): 'X<-Y', (3, 0): 'empty Y', (0, 7): 'empty X', (3, 9): 'fill Y', (1, 9): 'X->Y'}

>>> pour_problem(4, 9, 6)
[(0, 0), 'fill Y', (0, 9), 'X<-Y', (4, 5), 'empty X', (0, 5), 'X<-Y', (4, 1), 'empty X', (0, 1), 'X<-Y', (1, 0), 'fill Y', (1, 9), 'X<-Y', (4, 6)]

## what problem, with X, Y, and goal < 10, has the longest solution?
## Answer: pour_problem(7, 9, 8), with 14 steps.

>>> def num_actions(triplet): X, Y, goal = triplet; return len(pour_problem(X, Y, goal)) // 2

>>> def hardness(triplet): X, Y, goal = triplet; return num_actions((X, Y, goal)) - max(X, Y)

>>> max([(X, Y, goal) for X in range(1, 10) for Y in range(1, 10)
...                   for goal in range(1, max(X, Y))], key=num_actions)
(7, 9, 8)

>>> pour_problem(7, 9, 8)
[(0, 0), 'fill Y', (0, 9), 'X<-Y', (7, 2), 'empty X', (0, 2), 'X<-Y', (2, 0), 'fill Y', (2, 9), 'X<-Y', (7, 4), 'empty X', (0, 4), 'X<-Y', (4, 0), 'fill Y', (4, 9), 'X<-Y', (7, 6), 'empty X', (0, 6), 'X<-Y', (6, 0), 'fill Y', (6, 9), 'X<-Y', (7, 8)]
'''


class TestBridge:
    """
>>> elapsed_time(bridge_problem([1,2,5,10]))
17

## There are two equally good solutions
>>> S1 = [(2, 1, '->'), (1, 1, '<-'), (5, 10, '->'), (2, 2, '<-'), (2, 1, '->')]
>>> S2 = [(2, 1, '->'), (2, 2, '<-'), (5, 10, '->'), (1, 1, '<-'), (2, 1, '->')]
>>> path_actions(bridge_problem([1,2,5,10])) in (S1, S2)
True

## Try some other problems
>>> path_actions(bridge_problem([1,2,5,10,15,20]))
[(2, 1, '->'), (1, 1, '<-'), (10, 5, '->'), (2, 2, '<-'), (2, 1, '->'), (1, 1, '<-'), (15, 20, '->'), (2, 2, '<-'), (2, 1, '->')]

>>> path_actions(bridge_problem([1,2,4,8,16,32]))
[(2, 1, '->'), (1, 1, '<-'), (8, 4, '->'), (2, 2, '<-'), (2, 1, '->'), (1, 1, '<-'), (16, 32, '->'), (2, 2, '<-'), (2, 1, '->')]

>>> [elapsed_time(bridge_problem([1,2,4,8,16][:N])) for N in range(6)]
[0, 1, 2, 7, 15, 28]

>>> [elapsed_time(bridge_problem([1,1,2,3,5,8,13,21][:N])) for N in range(8)]
[0, 1, 1, 2, 6, 12, 19, 30]

"""


if __name__ == '__main__':
    # print(doctest.testmod())
    test_bridge()

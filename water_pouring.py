'''
Water pouring problem.
'''

import doctest

Fail = []


def shortest_path_search(start, successors, is_goal):
    """Find the shortest path from start state to a state
    such that is_goal(state) is true."""
    if is_goal(start):
        return [start]
    explored = set()
    frontier = [[start]]
    while frontier:
        path = frontier.pop(0)
        last_state = path[-1]
        if is_goal(last_state):
            return path
        explored.add(last_state)
        for state, action in successors(last_state).items():
            if state not in explored:
                path2 = path + [action, state]
                frontier.append(path2)
    return Fail


def lowest_cost_search(start, successors, is_goal, action_cost):
    """Return the lowest cost path, starting from start state,
    and considering successors(state) => {state:action,...},
    that ends in a state for which is_goal(state) is true,
    where the cost of a path is the sum of action costs,
    which are given by action_cost(action)."""
    if is_goal(start):
        return [start]
    explored = set()
    frontier = [[start]]
    while frontier:
        path = frontier.pop(0)
        last_state = final_state(path)
        if is_goal(last_state):
            return path
        explored.add(last_state)
        pcost = path_cost(path)
        for (state, action) in successors(last_state).items():
            if state not in explored:
                total_cost = pcost + action_cost(action)
                path2 = path + [(action, total_cost), state]
                add_to_frontier(frontier, path2)
    return Fail


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


def more_pour_problem(capacities, goal, start=None):
    """The first argument is a tuple of capacities (numbers) of glasses; the
    goal is a number which we must achieve in some glass.  start is a tuple
    of starting levels for each glass; if None, that means 0 for all.
    Start at start state and follow successors until we reach the goal.
    Keep track of frontier and previously explored; fail when no frontier.
    On success return a path: a [state, action, state2, ...] list, where an
    action is one of ('fill', i), ('empty', i), ('pour', i, j), where
    i and j are indices indicating the glass number."""

    def is_goal(state):
        return goal in state

    def replace(state, pos, value):
        result = list(state)
        result[pos] = value
        return type(state)(result)

    def successors(state):
        result = {}
        indices = range(len(state))
        for i in indices:
            result[replace(state, i, capacities[i])] = ('fill', i)
            result[replace(state, i, 0)] = ('empty', i)
            for j in indices:
                if i != j:
                    amount = min(state[i], capacities[j] - state[j])
                    new_state = replace(state, i, state[i] - amount)
                    new_state = replace(new_state, j, state[j] + amount)
                    result[new_state] = ('pour', i, j)

        return dict(result)

    if goal % 2 == 1 and all(map(lambda x: x % 2 == 0, capacities)):
        return Fail
    if all(map(lambda x: x < goal, capacities)):
        return Fail
    if start is None:
        start = (0, ) * len(capacities)
    return shortest_path_search(start, successors, is_goal)


def add_to_frontier(frontier, path):
    "Add path to frontier, replacing costlier path if there is one."
    # (This could be done more efficiently.)
    # Find if there is an old path to the final state of this path.
    old = None
    for i, p in enumerate(frontier):
        if final_state(p) == final_state(path):
            old = i
            break
    if old is not None and path_cost(frontier[old]) < path_cost(path):
        return  # Old path was better; do nothing
    elif old is not None:
        del frontier[old]  # Old path was worse; delete it
    ## Now add the new path and re-sort
    frontier.append(path)
    frontier.sort(key=path_cost)


def final_state(path):
    return path[-1]


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


def bridge_successors3(state):
    """Return a dict of {state:action} pairs.  State is (here, there, light)
    where here and there are frozen sets of people, light is 0 if the light is
    on the here side and 1 if it is on the there side.
    Action is a tuple (travelers, arrow) where arrow is '->' or '<-'"""

    def generate_successor(state, travelers):
        _, _, light = state
        start = state[light] - travelers
        dest = state[1 - light] | travelers
        if light:
            return (dest, start, 0), (travelers, '<-')
        else:
            return (start, dest, 1), (travelers, '->')

    _, _, light = state
    return dict(
        generate_successor(state, set([a, b]))
        for a in state[light] for b in state[light])


def bridge_problem(here):
    '''
    Find the fastest (least elapsed time) path to the goal in the bridge problem.
    '''

    def bridge_goal(state):
        here, _ = state
        return not here or len(here) == 1 and 'light' in here

    start = (frozenset(here) | frozenset(['light']), frozenset())
    return lowest_cost_search(start, bridge_successors2, bridge_goal,
                              bridge_cost)


def elapsed_time(path):
    return path_cost(path)


def path_cost(path):
    """The total cost of a path (which is stored in a tuple
    with the final action."""
    # path = (state, (action, total_cost), state, ... )
    if len(path) < 3:
        return 0
    else:
        _, total_cost = path[-2]
        return total_cost


def bridge_cost(action):
    """Returns the cost (a number) of an action in the
    bridge problem."""
    # An action is an (a, b, arrow) tuple; a and b are
    # times; arrow is a string.
    a, b, _ = action
    return max(a, b)


def missionaries_cannibals_problem(start=(3, 3, 1, 0, 0, 0), goal=None):
    '''
    Solve the missionaries and cannibals problem.
    State is 6 ints: (M1, C1, B1, M2, C2, B2) on the start (1) and other (2) sides.
    Find a path that goes from the initial state to the goal state (which if not specified,
    is the state with no people or boats on the start side.)
    '''
    if goal is None:
        goal = (0, 0, 0) + start[:3]

    def is_goal(state):
        return state == goal

    return shortest_path_search(start, missionaries_cannibals_successors,
                                is_goal)


def missionaries_cannibals_successors(state):
    """Find successors (including those that result in dining) to this
    state. But a state where the cannibals can dine has no successors."""
    M1, C1, B1, M2, C2, B2 = state
    if 0 < M1 < C1 or 0 < M2 < C2:
        return {}

    result = {}
    if B1:
        if M1 >= 1:
            result[(M1 - 1, C1, B2, M2 + 1, C2, B1)] = 'M->'
            if M1 >= 2:
                result[(M1 - 2, C1, B2, M2 + 2, C2, B1)] = 'MM->'
        if C1 >= 1:
            result[(M1, C1 - 1, B2, M2, C2 + 1, B1)] = 'C->'
            if C1 >= 2:
                result[(M1, C1 - 2, B2, M2, C2 + 2, B1)] = 'CC->'
        if M1 > 0 and C1 > 0:
            result[(M1 - 1, C1 - 1, B2, M2 + 1, C2 + 1, B1)] = 'MC->'
    else:
        if M2 >= 1:
            result[(M1 + 1, C1, B2, M2 - 1, C2, B1)] = '<-M'
            if M2 >= 2:
                result[(M1 + 2, C1, B2, M2 - 2, C2, B1)] = '<-MM'
        if C2 >= 1:
            result[(M1, C1 + 1, B2, M2, C2 - 1, B1)] = '<-C'
            if C2 >= 2:
                result[(M1, C1 + 2, B2, M2, C2 - 2, B1)] = '<-CC'
        if M2 > 0 and C2 > 0:
            result[(M1 + 1, C1 + 1, B2, M2 - 1, C2 - 1, B1)] = '<-MC'

    return result


def test_bridge():
    "tests."
    assert bridge_successors((frozenset([1, 'light']), frozenset([]), 3)) == {
        (frozenset([]), frozenset([1, 'light']), 4): (1, 1, '->')
    }

    assert bridge_successors((frozenset([]), frozenset([2, 'light']), 0)) == {
        (frozenset([2, 'light']), frozenset([]), 2): (2, 2, '<-')
    }

    print(path_actions(bridge_problem([1, 2, 5, 10])))
    here = [1, 2, 5, 10]
    assert bridge_problem(here) == [
        (frozenset([1, 2, 'light', 10, 5]), frozenset([])), (
            (2, 1, '->'), 2), (frozenset([10, 5]), frozenset([1, 2, 'light'])),
        ((2, 2, '<-'), 4), (frozenset(['light', 10, 2, 5]), frozenset([1])), (
            (5, 10,
             '->'), 14), (frozenset([2]), frozenset([1, 10, 5, 'light'])), (
                 (1, 1, '<-'), 15), (frozenset([1, 2, 'light']), frozenset(
                     [10, 5])), ((2, 1, '->'), 17), (frozenset([]), frozenset(
                         [1, 10, 2, 5, 'light']))
    ]

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

    assert path_cost(('fake_state1', ((2, 5, '->'), 5), 'fake_state2')) == 5
    assert path_cost(('fs1', ((2, 1, '->'), 2), 'fs2', ((3, 4, '<-'), 6),
                      'fs3')) == 6
    assert bridge_cost(
        (4, 2, '->'), ) == 4
    assert bridge_cost(
        (3, 10, '<-'), ) == 10

    assert bridge_successors3((frozenset([1]), frozenset([]), 0)) == {
        (frozenset([]), frozenset([1]), 1): (set([1]), '->')
    }

    assert bridge_successors3((frozenset([1, 2]), frozenset([]), 0)) == {
        (frozenset([1]), frozenset([2]), 1): (set([2]), '->'),
        (frozenset([]), frozenset([1, 2]), 1): (set([1, 2]), '->'),
        (frozenset([2]), frozenset([1]), 1): (set([1]), '->')
    }

    assert bridge_successors3((frozenset([2, 4]), frozenset([3, 5]), 1)) == {
        (frozenset([2, 4, 5]), frozenset([3]), 0): (set([5]), '<-'),
        (frozenset([2, 3, 4, 5]), frozenset([]), 0): (set([3, 5]), '<-'),
        (frozenset([2, 3, 4]), frozenset([5]), 0): (set([3]), '<-')
    }

    print('bridge tests pass')


def test_missionaries_cannibals():
    "Missionaries and cannibals problem tests."
    assert missionaries_cannibals_successors((2, 2, 1, 0, 0, 0)) == {
        (2, 1, 0, 0, 1, 1): 'C->',
        (1, 2, 0, 1, 0, 1): 'M->',
        (0, 2, 0, 2, 0, 1): 'MM->',
        (1, 1, 0, 1, 1, 1): 'MC->',
        (2, 0, 0, 0, 2, 1): 'CC->'
    }
    assert missionaries_cannibals_successors((1, 1, 0, 4, 3, 1)) == {
        (1, 2, 1, 4, 2, 0): '<-C',
        (2, 1, 1, 3, 3, 0): '<-M',
        (3, 1, 1, 2, 3, 0): '<-MM',
        (1, 3, 1, 4, 1, 0): '<-CC',
        (2, 2, 1, 3, 2, 0): '<-MC'
    }
    assert missionaries_cannibals_successors((1, 4, 1, 2, 2, 0)) == {}
    assert missionaries_cannibals_successors((0, 2, 1, 3, 1, 0)) == {
        (0, 1, 0, 3, 2, 1): 'C->',
        (0, 0, 0, 3, 3, 1): 'CC->'
    }
    print(missionaries_cannibals_problem())
    print('missionaries and cannibals problem tests pass')


def test_shortest_path_search():
    "shortest path search tests."

    def is_goal(state):
        if state == 8:
            return True
        else:
            return False

    def test_successors(state):
        result = {state + 1: '->', state - 1: '<-'}
        return result

    assert shortest_path_search(5, test_successors,
                                is_goal) == [5, '->', 6, '->', 7, '->', 8]
    print('shortest path search tests success')


def test_more_pour():
    "test pour problem."
    assert more_pour_problem((1, 2, 4, 8), 4) == [(0, 0, 0, 0), ('fill', 2),
                                                  (0, 0, 4, 0)]
    assert more_pour_problem((1, 2, 4), 3) == [(0, 0, 0), ('fill', 2), (
        0, 0, 4), ('pour', 2, 0), (1, 0, 3)]
    starbucks = (8, 12, 16, 20, 24)
    assert not any(more_pour_problem(starbucks, odd) for odd in (3, 5, 7, 9))
    assert all(more_pour_problem((1, 3, 9, 27), n) for n in range(28))
    assert more_pour_problem((1, 3, 9, 27), 28) == []
    print('test_more_pour passes')


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
>>> S1 = [((2, 1, '->'), 2), ((1, 1, '<-'), 3), ((5, 10, '->'), 13), ((2, 2, '<-'), 15), ((2, 1, '->'), 17)]
>>> S2 = [((2, 1, '->'), 2), ((2, 2, '<-'), 4), ((5, 10, '->'), 14), ((1, 1, '<-'), 15), ((2, 1, '->'), 17)]
>>> path_actions(bridge_problem([1,2,5,10])) in (S1, S2)
True

## Try some other problems
>>> elapsed_time(bridge_problem([1,2,5,10,15,20]))
42

>>> path_actions(bridge_problem([1,2,5,10,15,20]))
[((2, 1, '->'), 2), ((1, 1, '<-'), 3), ((10, 5, '->'), 13), ((2, 2, '<-'), 15), ((2, 1, '->'), 17), ((1, 1, '<-'), 18), ((15, 20, '->'), 38), ((2, 2, '<-'), 40), ((2, 1, '->'), 42)]

>>> elapsed_time(bridge_problem([1,2,4,8,16,32]))
52

>>> path_actions(bridge_problem([1,2,4,8,16,32]))
[((2, 1, '->'), 2), ((1, 1, '<-'), 3), ((8, 4, '->'), 11), ((2, 2, '<-'), 13), ((2, 1, '->'), 15), ((1, 1, '<-'), 16), ((16, 32, '->'), 48), ((2, 2, '<-'), 50), ((2, 1, '->'), 52)]

>>> [elapsed_time(bridge_problem([1,2,4,8,16][:N])) for N in range(6)]
[0, 1, 2, 7, 15, 28]

>>> [elapsed_time(bridge_problem([1,1,2,3,5,8,13,21][:N])) for N in range(8)]
[0, 1, 1, 2, 6, 12, 19, 30]

"""


if __name__ == '__main__':
    # print(doctest.testmod())
    test_bridge()
    test_missionaries_cannibals()
    test_shortest_path_search()
    test_more_pour()

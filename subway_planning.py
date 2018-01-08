'''
Subway planning.
'''
import collections
from water_pouring import shortest_path_search, path_states, path_actions

# Write a function, subway, that takes lines as input (read more about
# the **lines notation in the instructor comments box below) and returns
# a dictionary of the form {station:{neighbor:line, ...}, ... } 
#
# For example, when calling subway(boston), one of the entries in the 
# resulting dictionary should be 'foresthills': {'backbay': 'orange'}. 
# This means that foresthills only has one neighbor ('backbay') and 
# that neighbor is on the orange line. Other stations have more neighbors:
# 'state', for example, has 4 neighbors.
#
# Once you've defined your subway function, you can define a ride and 
# longest_ride function. ride(here, there, system) takes as input 
# a starting station (here), a destination station (there), and a subway
# system and returns the shortest path.
#
# longest_ride(system) returns the longest possible ride in a given 
# subway system. 


def subway(**lines):
    """Define a subway map. Input is subway(linename='station1 station2...'...).
    Convert that and return a dict of the form: {station:{neighbor:line,...},...}"""

    def overlapping_pairs(items):
        return (items[i:i + 2] for i in range(len(items) - 1))

    infos = collections.defaultdict(dict)
    for line, stations in lines.items():
        for a, b in overlapping_pairs(stations.split()):
            infos[a][b] = line
            infos[b][a] = line

    return infos


boston = subway(
    blue=
    'bowdoin government state aquarium maverick airport suffolk revere wonderland',
    orange=
    'oakgrove sullivan haymarket state downtown chinatown tufts backbay foresthills',
    green=
    'lechmere science north haymarket government park copley kenmore newton riverside',
    red=
    'alewife davis porter harvard central mit charles park downtown south umass mattapan'
)


def is_goal(dest):
    def _f(value):
        return value == dest

    return _f


def successors(system):
    def _f(value):
        return system[value]

    return _f


def ride(here, there, system=boston):
    "Return a path on the subway system from here to there."
    return shortest_path_search(here, successors(system), is_goal(there))


def longest_ride(system):
    """"Return the longest possible 'shortest path'
    ride between any two stops in the system."""
    stations = set(system.keys())
    return max(
        [ride(a, b) for a in stations for b in stations if a != b], key=len)


def test_ride():
    assert ride('mit', 'government') == [
        'mit', 'red', 'charles', 'red', 'park', 'green', 'government'
    ]
    assert ride('mattapan', 'foresthills') == [
        'mattapan', 'red', 'umass', 'red', 'south', 'red', 'downtown',
        'orange', 'chinatown', 'orange', 'tufts', 'orange', 'backbay',
        'orange', 'foresthills'
    ]
    assert ride('newton', 'alewife') == [
        'newton', 'green', 'kenmore', 'green', 'copley', 'green', 'park',
        'red', 'charles', 'red', 'mit', 'red', 'central', 'red', 'harvard',
        'red', 'porter', 'red', 'davis', 'red', 'alewife'
    ]
    assert len(path_states(longest_ride(boston))) == 16
    assert (path_states(longest_ride(boston)) == [
        'wonderland', 'revere', 'suffolk', 'airport', 'maverick', 'aquarium',
        'state', 'downtown', 'park', 'charles', 'mit', 'central', 'harvard',
        'porter', 'davis', 'alewife'
    ] or path_states(longest_ride(boston)) == [
        'alewife', 'davis', 'porter', 'harvard', 'central', 'mit', 'charles',
        'park', 'downtown', 'state', 'aquarium', 'maverick', 'airport',
        'suffolk', 'revere', 'wonderland'
    ] or path_states(longest_ride(boston)) == [
        'wonderland', 'revere', 'suffolk', 'airport', 'maverick', 'aquarium',
        'state', 'government', 'park', 'charles', 'mit', 'central', 'harvard',
        'porter', 'davis', 'alewife'
    ] or path_states(longest_ride(boston)) == [
        'alewife', 'davis', 'porter', 'harvard', 'central', 'mit', 'charles',
        'park', 'government', 'state', 'aquarium', 'maverick', 'airport',
        'suffolk', 'revere', 'wonderland'
    ])
    print('test_ride passes')


if __name__ == '__main__':
    test_ride()

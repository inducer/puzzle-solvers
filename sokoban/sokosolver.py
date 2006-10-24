import sys, operator, re
from heapq import heappop, heappush
from sets import Set

class INFINITY:
    pass

class tNoSolutionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)




def addTuples(t1, t2):
    return tuple([t1v + t2v for t1v, t2v in zip(t1, t2)])
def subtractTuples(t1, t2):
    return tuple([t1v - t2v for t1v, t2v in zip(t1, t2)])
def manhattanDistance(t1, t2):
    return sum([abs(t1v - t2v) for t1v, t2v in zip(t1, t2)])
def viTuple((x, y)):
    #return (y+1, x+1)
    return (x,y)

def findIterator(haystack, needle):
    pos = 0
    pos = haystack.find(needle, pos)
    while pos != -1:
        yield pos
        pos = haystack.find(needle, pos+1)

def findPositions(lines, char):
    for y, line in enumerate(lines):
        for x in findIterator(line, char):
            yield (x,y)




def aStar(initial_state, get_successor_states, estimate_remaining_cost, depth_limit = None):
    class tAStarNode:
        def __init__(self, state, parent, path_cost, estimated_path_cost, move_descriptor):
            self.State = state
            self.Parent = parent
            if parent is None:
                self.PathLength = 0
            else:
                self.PathLength = parent.PathLength+1
            self.PathCost = path_cost
            self.EstimatedPathCost = estimated_path_cost
            self.MoveDescriptor = move_descriptor
            
        def __cmp__(self, other):
            return cmp(self.EstimatedPathCost, other.EstimatedPathCost)

    init_remcost = estimate_remaining_cost(initial_state)
    if  init_remcost is INFINITY:
        raise tNoSolutionError, "no solution"

    queue = [tAStarNode(initial_state,
                        parent = None,
                        path_cost = 0, 
                        estimated_path_cost = init_remcost,
                        move_descriptor = None)]

    visited_states = Set([initial_state])

    while len(queue):
        top = heappop(queue)
        if depth_limit is not None and top.PathLength == depth_limit:
            continue

        visited_states.add(top.State)
        remcost = estimate_remaining_cost(top.State)

        if remcost == 0:
            result = []
            it = top
            previous_move_descr = None
            while it is not None:
                result.append((it.State, previous_move_descr))
                previous_move_descr = it.MoveDescriptor
                it = it.Parent
            result.reverse()
            return result

        top_pcost = top.PathCost
        for state, cost, descriptor in get_successor_states(top.State):
            if state in visited_states:
                continue

            remaining_cost = estimate_remaining_cost(state)
            if remaining_cost is INFINITY:
                continue

            heappush(queue, tAStarNode(state, top,
                                       path_cost = cost+top_pcost, 
                                       estimated_path_cost = cost+top_pcost+remaining_cost,
                                       move_descriptor = descriptor))

    raise tNoSolutionError, "no solution"




def iterativeDeepeningAStar(initial_state, get_successor_states, estimate_remaining_cost, initial = 10, step = 10):
    max_depth = initial
    while True:
        try:
            return aStar(initial_state, get_successor_states, 
                         estimate_remaining_cost, max_depth)
        except tNoSolutionError:
            max_depth += step




class tField:
    def copy(self, man = None, boxes = None):
        result = tField()
        result.Man = man or self.Man
        result.Boxes = boxes or self.Boxes
        result.Targets = self.Targets
        result.Walls = self.Walls
        return result

    def read(self, lines):
        men =  list(findPositions(lines, "@"))
        assert len(men) == 1
        self.Man = men[0]

        self.Boxes = list(findPositions(lines, "$"))
        self.Targets = list(findPositions(lines, "."))
        targets_with_boxes = list(findPositions(lines, "*"))
        self.Boxes += targets_with_boxes
        self.Targets += targets_with_boxes
        self.Walls = Set(findPositions(lines, "#"))
        assert len(self.Boxes) == len(self.Targets)

    def visualize(self):
        max_x = max_y = 0
        for (x,y) in self.Walls:
            max_x = max(x, max_x)
            max_y = max(y, max_y)
        x_size = max_x + 1
        y_size = max_y + 1
        
        vis = [[" "] * x_size for y in range(y_size)]
        for (x,y) in self.Walls:
            vis[y][x] = "#"
        for (x,y) in self.Targets:
            vis[y][x] = "."
        vis[self.Man[1]][self.Man[0]] = "@"
        for (x,y) in self.Boxes:
            vis[y][x] = "$"
        return "\n".join(["".join(line) for line in vis])

    def __eq__(self, other):
        return self.Man == other.Man and \
               self.Boxes == other.Boxes

    def __hash__(self):
        return hash(self.Man) ^ reduce(operator.xor, [hash(box) for box in self.Boxes])
    



def canManMoveTo(orig_field, dest_pos):
    if dest_pos in orig_field.Walls:
        return False

    def generateMoves(field):
        for direction in [(0,1),(1,0),(-1,0),(0,-1)]:
            new_man = addTuples(direction, field.Man)
            if new_man not in field.Walls and not new_man in field.Boxes:
                yield field.copy(new_man), 1, direction

    def estimateRemainingCost(field):
        return manhattanDistance(dest_pos, field.Man)

    try:
        aStar(orig_field, generateMoves, estimateRemainingCost)
        return True
    except tNoSolutionError:
        return False




def isWalled(field, spot):
    walled = 0
    for direction in [(0,1),(1,0),(0,-1),(-1,0),(0,1)]:
        if addTuples(spot, direction) in field.Walls:
            walled += 1
        else:
            walled = 0
        if walled == 2:
            return True
    return False

def solve(orig_field):
    def generateMoves(field):
        #print "EXPANDING" 
        #print field.visualize()
        for i, box in enumerate(field.Boxes):
            for direction in [(0,1),(1,0),(-1,0),(0,-1)]:
                new_box = addTuples(box, direction)
                if new_box not in field.Walls and not new_box in field.Boxes and \
                     canManMoveTo(field, subtractTuples(box, direction)) and \
                     not (isWalled(field, new_box) and not new_box in field.Targets):
                    new_boxes = field.Boxes[:i] + [new_box] + field.Boxes[i+1:]
                    yield field.copy(man = box, boxes = new_boxes), 1, (box, direction)

    def estimateRemainingCost(field):
        result = 0
        for box in field.Boxes:
            target_dists = [manhattanDistance(target, box) for target in field.Targets]
            result += min(target_dists)
        return result

    try:
        result = aStar(orig_field, generateMoves, estimateRemainingCost)
        for state, descriptor in result:
            print state.visualize()
            print descriptor
        return True
    except RuntimeError:
        return False




def main():
    lines = file(sys.argv[1], "r").readlines()
    if len(sys.argv) == 2:
        lines = file(sys.argv[1], "r").readlines()
    elif len(sys.argv) == 3:
        lines = file(sys.argv[1], "r").readlines()
        level_re = re.compile("^\\s*;\\s*%d\\s$" % int(sys.argv[2]))
        start = 0
        while not level_re.match(lines[start]):
            start += 1
            if start >= len(lines):
                raise RuntimeError, "level not found"
        stop = start+1
        while lines[stop].find(";") == -1:
            stop += 1
            if stop >= len(lines):
                break
        lines = lines[start+1:stop]
    else:
        print "USAGE: <level_file> [<level_number>]"
    field = tField()
    field.read(lines)
    #print canManMoveTo(field, (1, 2))
    solve(field)

if __name__ == "__main__":
    main()

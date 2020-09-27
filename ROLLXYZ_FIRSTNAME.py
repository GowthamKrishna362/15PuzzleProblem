#!/usr/bin/env python3
import time
import heapq


### Don't use fancy libraries. Evaluators won't install fancy libraries. You may use Numpy and Scipy if needed.
### Send an email to the instructor if you want to use more libraries.

#Global Variables
generatedPositions = dict() #Dictionary of positions generated so far. Used to avoid redundant generations.

states = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'A':10,'B':11,'C':12,'D':13,'E':14,'F':15  } #To convert alphabets to integral numbers



#Helper Functions (Minimal Helper functions for code level speed optimization)
def toTuple(tileList): #To create hashable board position
    tl= tileList
    result=(((tl[0][0], tl[0][1], tl[0][2], tl[0][3]),
          (tl[1][0], tl[1][1], tl[1][2], tl[1][3]),
          (tl[2][0], tl[2][1], tl[2][2], tl[2][3]),
         (tl[3][0], tl[3][1], tl[3][2], tl[3][3])))

    return result

def toList(tileTuple):   #To create editable board position
    tt= tileTuple
    result= [[tt[0][0], tt[0][1], tt[0][2], tt[0][3]],
             [tt[1][0], tt[1][1], tt[1][2], tt[1][3]],
             [tt[2][0], tt[2][1], tt[2][2], tt[2][3]],
             [tt[3][0], tt[3][1], tt[3][2], tt[3][3]]]
    return result


#End of Helper Functions

class BoardPosition:
    def __init__(self, tiles):
        if type(tiles)==type(list()):
            self.tiles = toTuple(tiles)
        else:
            self.tiles = tiles

            self.visited = False  #Stores if Board Position has been visited by the A* Search
            self.parent  = None   #Upon visit,stores the node from which this node has been derived
            self.f, self.g = -1,-1           #F score = G Score + Heuristic (-1 until calculated)
                                             #G score (-1 until calculated)

    def neighborsList(self):      #Returns list of neighbors of given Board Position
        neighbors = []
        for y_coord in range(4):                  #Finds index of zero tile
            for x_coord in range (4):
                if self.tiles[y_coord][x_coord]==0:
                    x0, y0 = x_coord , y_coord


        if x0 < 3: #Shifting Blank Tile Right
            rightshift = toList(self.tiles)
            rightshift[y0][x0 + 1], rightshift[y0][x0] = rightshift[y0][x0], rightshift[y0][x0 + 1]
            neighbors.append(createBoardPosition(rightshift))

        if y0 < 3: #Shifting Blank Tile Down
            downshift = toList(self.tiles)
            downshift[y0 + 1][x0], downshift[y0][x0] = downshift[y0][x0], downshift[y0 + 1][x0]
            neighbors.append(createBoardPosition(downshift))

        if x0 > 0:  #Shifting Blank Tile Left
            leftshift = toList(self.tiles)
            leftshift[y0][x0 - 1], leftshift[y0][x0] = leftshift[y0][x0], leftshift[y0][x0 - 1]
            neighbors.append(createBoardPosition(leftshift))

        if y0 > 0:  #Shifting Blank Tile Up
            upshift = toList(self.tiles)
            upshift[y0 - 1][x0], upshift[y0][x0] = upshift[y0][x0], upshift[y0 - 1][x0]
            neighbors.append(createBoardPosition(upshift))

        return neighbors


def manhattanDistance(fromState): #Manhattan Distance calculator.
        goal_x, goal_y = -1, -1
        result = 0
        for y_coord in range(4):
            for x_coord in range(4):
                element = fromState[y_coord][x_coord]
                if element == 0:
                    continue
                else:
                    goal_x, goal_y = element % 4, element // 4
                    result += abs(goal_x - x_coord) + abs(goal_y - y_coord)

        return result




def linearConflicts(fromState): #Calculates the number of column and row conflicts.


    colConflicts, rowConflicts = 0, 0  # Number of Column Conflicts,Number of Row Conflicts
    conflictsPerColumn = [0,0,0,0]
    conflictsPerRow = [0,0,0,0]
    correctColumn = [[False for i in range(4)] for j in
                     range(4)]  # Stores whether an element is in the right column, initialized to False.
    correctRow = [[False for i in range(4)] for j in
                  range(4)]  # Stores whether an element is in the right row, initialized to False.

    for y_coord in range(4):
        for x_coord in range(4):
            correctRow[y_coord][x_coord] = (y_coord == fromState[y_coord][x_coord] // 4)
            correctColumn[y_coord][x_coord] = (x_coord == fromState[y_coord][x_coord] % 4)

    for y_coord in range(4):
        for x_coord in range(4):
            firstElement = fromState[y_coord][x_coord]
            if correctRow[y_coord][x_coord] and firstElement != 0:
                for xCheck in range(x_coord + 1, 4):
                    secondElement = fromState[y_coord][xCheck]
                    if (correctRow[y_coord][xCheck]) and (secondElement < firstElement) and secondElement != 0:
                        conflictsPerRow[y_coord]+=1

    for x_coord in range(4):
        for y_coord in range(4):
            firstElement = fromState[y_coord][x_coord]
            if correctColumn[y_coord][x_coord] and firstElement != 0:
                for yCheck in range(y_coord + 1, 4):
                    secondElement = fromState[yCheck][x_coord]
                    if (correctColumn[yCheck][x_coord]) and (secondElement < firstElement) and secondElement != 0:
                        colConflicts += 1
                        conflictsPerColumn[x_coord]+=1

    for x in  conflictsPerColumn:
        if x<3:
            colConflicts+=x
        else:
            colConflicts+=3
    for x in conflictsPerRow:
        if x<3:
            rowConflicts+=x
        else:
            rowConflicts+=3
    totalConflicts = colConflicts + rowConflicts


    return totalConflicts


def totalHeuristic(fromState):
    return manhattanDistance(fromState) + 2*linearConflicts(fromState)


class PriorityQueue:
    def __init__(self, PositionList):
        self.length = 0
        self.PosHeap= []
        for Pos in PositionList:
            self.PosHeap.append((Pos.f,Pos.tiles))
            self.length+=1
        heapq.heapify(self.PosHeap)

    def push(self,newPosition):
        heapq.heappush(self.PosHeap,(newPosition.f,newPosition.tiles))
        self.length+=1

    def pop(self):
        if self.length<1:
            return None
        else:
            f,tiles= heapq.heappop(self.PosHeap)
            self.length-=1
            global generatedPositions
            poppedPosition = generatedPositions[tiles]
            if poppedPosition.visited:
                return self.pop()
            else:
                return poppedPosition
def makePath(goalNode):
    actionList=[]
    childNode = goalNode
    currentNode = goalNode.parent
    while(currentNode!=None):
        for y_coord in range(4):
            for x_coord in range(4):
                if childNode.tiles[y_coord][x_coord]==0:
                    xChild = x_coord
                    yChild = y_coord
        for y_coord in range(4):
            for x_coord in range(4):
                if currentNode.tiles[y_coord][x_coord] == 0:
                    xCurrent = x_coord
                    yCurrent = y_coord
        if xChild > xCurrent:
            actionList.append('Right')
        if xChild < xCurrent:
            actionList.append('Left')
        if yChild < yCurrent:
            actionList.append('Up')
        if yChild > yCurrent:
            actionList.append('Down')
        childNode =   currentNode
        currentNode= currentNode.parent
    actionList.reverse()
    return actionList

def createBoardPosition(tileList):
    global generatedPositions
    tileTuple=toTuple(tileList)

    if tileTuple in generatedPositions:
        return generatedPositions[tileTuple]
    else:
        genPos = BoardPosition(tileTuple)
        generatedPositions[tileTuple] = genPos
        return genPos


def FindMinimumPath(initialState,goalState):
    for y in range(4):
        for x in range(4):
            initialState[y][x] = states[initialState[y][x]]
            goalState[y][x]= states[goalState[y][x]]
    nodesGenerated = 0  # Number of Nodes
    start = createBoardPosition(initialState)
    goal  = createBoardPosition(goalState)
    start.g = 0
    start.f = totalHeuristic(initialState)
    frontierSet = PriorityQueue([start])

    while frontierSet.length>0:
        currentNode = frontierSet.pop()
        if currentNode == None:
            return None
        if currentNode == goal:
            minPath = makePath(currentNode)
            # for y in range(4):
            #     for x in range(4):
            #         print(goal.parent.tiles[y][x])x
            return minPath,nodesGenerated
        else:
            currentNode.visited= True
            for neighborNode in currentNode.neighborsList():
                gViaCurrent = currentNode.g + 1
                if  neighborNode.g == -1 or neighborNode.g > gViaCurrent:
                    neighborNode.g = gViaCurrent
                    neighborNode.f = neighborNode.g + totalHeuristic(neighborNode.tiles)
                    neighborNode.parent = currentNode
                    frontierSet.push(neighborNode)
                    nodesGenerated+=1






    # Sequence of actions in the optimal solution

    
    
    
    return minPath, nodesGenerated



#**************   DO NOT CHANGE ANY CODE BELOW THIS LINE *****************************


def ReadInitialState():
    with open("initial_state4.txt", "r") as file: #IMP: If you change the file name, then there will be an error when
                                                        #               evaluators test your program. You will lose 2 marks.
        initialState = [[x for x in line.split()] for i,line in enumerate(file) if i<4]
    return initialState

def ShowState(state,heading=''):
    print(heading)
    for row in state:
        print(*row, sep = " ")

def main():
    initialState = ReadInitialState()
    ShowState(initialState,'Initial state:')
    goalState = [['0','1','2','3'],['4','5','6','7'],['8','9','A','B'],['C','D','E','F']]
    ShowState(goalState,'Goal state:')
    
    start = time.time()
    minimumPath, nodesGenerated = FindMinimumPath(initialState,goalState)
    timeTaken = time.time() - start
    
    if len(minimumPath)==0:
        minimumPath = ['Up','Right','Down','Down','Left']
        print('Example output:')
    else:
        print('Output:')

    print('   Minimum path cost : {0}'.format(len(minimumPath)))
    print('   Actions in minimum path : {0}'.format(minimumPath))
    print('   Nodes generated : {0}'.format(nodesGenerated))
    print('   Time taken : {0} s'.format(round(timeTaken,4)))

if __name__=='__main__':
    main()

import time
from queue import PriorityQueue
import cProfile as cp

calcDistance = set(["greedy", "aStar"])



class State:
	def __init__(self, point, goals, parent, stepCost):
		self.point = point
		self.goals = goals
		self.parent = parent
		self.stepCost = stepCost
		self.hieur = 0

	def __str__(self):
		point = self.point
		goals = self.goals
		return "%(point)s : %(goals)s" % locals()

	def __lt__(self, other):
		# return self.hieur < other.hieur
		if self.hieur == other.hieur:
			return self.stepCost < other.stepCost
		else:
			return self.hieur < other.hieur
			

# class Point:
# 	def __init__(self, x, y):
# 		self.x = x
# 		self.y = y

# 	def __str__(self):
# 		return f"({self.x}, {self.y})"

startingKey = 'P'
wallKey = '%'
goalsKey = '.'
visitedKey = '!'

def readMapLayout(fileName):
	with open(fileName) as f:
		content = [x.strip() for x in f.readlines()]
		return content

#TODO: Maybe change this so that I can do this while reading the map
def getStartEndPositions(maze):
	startPos = (0,0)
	goals = []
	for lineNum in range(0, len(maze)):
		line = maze[lineNum]
		if startingKey in maze[lineNum]:
			startPos = (lineNum, maze[lineNum].index(startingKey))
		if goalsKey in maze[lineNum]:
			[goals.append((lineNum, x)) for x in findAll(goalsKey, maze[lineNum])]
	return (startPos, goals)

def findAll(term, string):
	index = string.find(term)
	indices = []
	while index != -1:
#		print(index)
		indices.append(index)
		index = string.find(term, index + 1) # Note this assumes that the maze is closed, otherwise out of bounds exception
	return indices

def printMaze(maze):
	for line in maze:
		print(''.join(line))

def printSol(maze, path, expanded):
	rebuiltMaze = [[maze[y][x] for x in range(len(maze[0]))] for y in range(len(maze))]
	# printMaze(rebuiltMaze)
	range1 = [chr(x) for x in range(48, 58)]
	[range1.append(chr(x)) for x in range(97, 123)]
	[range1.append(chr(x)) for x in range(65, 91)]
	rangeHeld = range1.copy()
	for state in reversed(path):
		point = state.point
		if rebuiltMaze[point[0]][point[1]] == goalsKey:
			rebuiltMaze[point[0]][point[1]] = range1.pop(0)
		elif state != path[-1] and rebuiltMaze[point[0]][point[1]] in rangeHeld:
			continue
		else:
			rebuiltMaze[point[0]][point[1]] = visitedKey
	# path cost: initial to goal state
	# Number of nodes expanded by alg
	solMaze = []
	for line in rebuiltMaze:
		solMaze.append(''.join(line).replace("!","."))
	printMaze(solMaze)
	pathLength = len(path)
	print("Path cost: %(pathLength)s, expanded nodes: %(expanded)s" % locals())

def buildPath(endPoint):
	path = []
	while endPoint:
		path.append(endPoint)
		endPoint = endPoint.parent
	return path

def getDistance(x1, y1, x2, y2):
	return (abs(x2-x1) + abs(y2-y1))

def getClosestEnd(start, ends):
	shortDist = getDistance(start[0], start[1], ends[0][0], ends[0][1])
	retVal = ends[0]
	for end in ends:
		nextDist = getDistance(start[0], start[1], end[0], end[1])
		if nextDist < shortDist:
			shortDist = nextDist
			retVal = end
	return retVal

def repeatedState(val, x, y, goals, visitedStates):
	if val == wallKey:
		return True
	elif str(goals) in visitedStates:
		return (x,y) in visitedStates[str(goals)]
	return False

class PsuedoState:
	def __init__(self, curPoint, ends, stepCost):
		self.curPoint = curPoint
		self.ends = ends
		self.stepCost = stepCost

	def __str__(self):
		x = self.curPoint[0]
		y = self.curPoint[1]
		ends = self.ends
		return "(%(x)s, %(y)s) : %(ends)s" % locals()

	def __lt__(self, other):
		return self.stepCost < other.stepCost

def buildMap(ends):
	endsMap = {}
	for end in ends:
		endsPQ = PriorityQueue()
		theseEnds = ends.copy()
		theseEnds.remove(end)
		firstState = PsuedoState(end, theseEnds, 0)

		endsPQ.put(firstState)
		visited = set()
		visited.add(str(firstState))
		endsMap[end] = getSmallestPathLength(endsPQ, visited)
	return endsMap

def getSmallestPathLength(endsPQ, visited):
	while endsPQ:
		curState = endsPQ.get()
		if curState.ends:
			for curEnd in curState.ends:
				nextEnds = curState.ends
				nextEnds.remove(curEnd)
				nextStepCost = curState.stepCost + getDistance(curState.curPoint[0], curState.curPoint[1], curEnd[0], curEnd[1])
				nextState = PsuedoState(curEnd, nextEnds, nextStepCost)
				if str(nextState) not in visited:
					endsPQ.put(nextState)
					visited.add(str(nextState))
		else:
			return curState.stepCost

def h2(searchType, curPos, endsBestCostMap, ends, curStepCost):
	minPath = -1
	if searchType == "aStar":
		key = str(ends)
		endsMap = endsBestCostMap[key]
		for end in ends:
			dist = getDistance(curPos[0], curPos[1], end[0], end[1]) + endsMap[end]

			if minPath > dist or minPath == -1:
				minPath = dist #* 2

		minPath += curStepCost #* 2

	elif searchType == "greedy":
		nextEnd = getClosestEnd((curPos[0], curPos[1]), ends)
		minPath = getDistance(curPos[0], curPos[1], nextEnd[0], nextEnd[1])

	return minPath

def search(maze, searchType):
	(startPosition, ends) = getStartEndPositions(maze)
	p0 = (startPosition[0], startPosition[1])
	initialState = State(p0, ends, None, 0)

	frontierNodes = PriorityQueue() if searchType != "dfs" else []
	frontierNodes.put(initialState) if searchType != "dfs" else frontierNodes.append(initialState)

	visitedStates = {}
	visitedStates[str(ends)] = set([p0])

	exposedNodes = 0

	#########
	# Stats #
	#########
	# timeExpandOrNot = 0
	# timePopping = 0
	# timeAppending = 0
	# timeNonRemoveHieur = 0
	# timeBuildingMap = 0
	# timeBuildingStates = 0
	# timeCheckingIfEndGoal = 0
	# timeChangingEnds = 0
	# timeRemovingGoals = 0

	# buildMapTime = time.clock()
	initialMap = buildMap(ends)
	# timeBuildingMap += time.clock() - buildMapTime
	endsBestCostMap = {}
	endsBestCostMap[str(ends)] = initialMap

	exploredPoints = [p0]
	rebuiltMaze = [[maze[y][x] for x in range(len(maze[0]))] for y in range(len(maze))]

	while frontierNodes:
		exposedNodes += 1

			# tp = time.clock()
		curState = frontierNodes.get() if searchType != "dfs" else frontierNodes.pop()

		# timePopping += time.clock() - tp
		(x, y) = curState.point

		nextPoints = [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]
		# if (x,y) == (2,15) or (x,y) == (4,15):
		# 	path = buildPath(curState)
		# 	printSol(maze, path, exposedNodes)
		# 	print(f"{x},{y}: hier: {curState.hieur}")
		# exploredPoints.append(curState.point)
		# if exposedNodes % 1000 == 0:
		# 	a = 0
		# 	for point in exploredPoints:
		# 		# print(point)
		# 		rebuiltMaze[point[0]][point[1]] = visitedKey
		# 		a += 1
		# 		if a > 75:
		# 			printMaze(rebuiltMaze)
		# 			time.sleep(.25)

		for tuplePoint in nextPoints:
			x1 = tuplePoint[0]
			y1 = tuplePoint[1]

			# repeatTime = time.clock()
			repeated = repeatedState(maze[x1][y1], x1, y1, curState.goals, visitedStates)
			# timeExpandOrNot += time.clock() - repeatTime

			if not repeated:
				nextPoint = (x1, y1)
				
				nextEnds = curState.goals
				# stState = time.clock()
				nextState = State(nextPoint, nextEnds, curState, curState.stepCost + 1)
				# timeBuildingStates += time.clock() - stState

				# exploredPoints.append(nextPoint)

				# stEndGoal = time.clock()
				isEndGoal = (x1,y1) in nextEnds
				# timeCheckingIfEndGoal += time.clock() - stEndGoal
				if isEndGoal:

					# stRG = time.clock()
					removedEnds = nextEnds.copy()
					removedEnds.remove((x1,y1))
					# timeRemovingGoals += time.clock() - stRG

						# print(f"found end: {x1}, {y1}, remainEnds: {removedEnds}")

					# stState = time.clock()
					nextState.goals = removedEnds
					# timeChangingEnds += time.clock() - stState

					if removedEnds:
						if str(removedEnds) not in endsBestCostMap:
							# buildMapTime = time.clock()
							nextEndsMap = buildMap(removedEnds)
							endsBestCostMap[str(removedEnds)] = nextEndsMap
							# timeBuildingMap += time.clock() - buildMapTime
					else:
						# print(f" timeRepeat: {timeExpandOrNot} \n timePopping: {timePopping}\n timeAppending: {timeAppending}\n nonRemovedHiur: {timeNonRemoveHieur}\n buildMap: {timeBuildingMap}")
							
						# print(f" buildState: {timeBuildingStates}\n timeCheckingIfEndGoal: {timeCheckingIfEndGoal}\n timeChangingEnds: {timeChangingEnds}\n timeRemovingGoals {timeRemovingGoals}")
						return (nextState, exposedNodes)

				# stHieur = time.clock()
				nextState.hieur = h2(searchType, nextState.point, endsBestCostMap, nextState.goals, nextState.stepCost)
				# timeNonRemoveHieur += time.clock() - stHieur

				# stFN = time.clock()
				frontierNodes.put(nextState) if searchType != "dfs" else frontierNodes.append(nextState)
				# timeAppending += time.clock() - stFN
				goalsKey = str(nextState.goals)
				if goalsKey in visitedStates:
					visitedStates[goalsKey].add(nextState.point)
				else:
					visitedStates[goalsKey] = set([nextState.point])
				# path = buildPath(nextState)
				# printSol(maze, path, exposedNodes)

	return(initialState, exposedNodes)
				

def runSearch(maze, searchType):
	(winningState, numExposed) = search(maze, searchType)
	path = buildPath(winningState)
	printSol(maze, path, numExposed)

if __name__ == "__main__":
	mazeNames = [
	# "bigMaze.txt",
	# "mediumMaze.txt" ,
	# "openMaze.txt" ,
	# "tinySearch.txt" ,
	# "smallSearch.txt" ,
	"mediumSearch.txt"
	]
	searches = [
	# "dfs",
	# "bfs",
	# "greedy",
	"aStar"
	]
	# Change visitedStates to be a hashmap from endgoals to map, then when checking just check if for that end goal if it's in the visited states set

	for mazeName in mazeNames:
		maze = readMapLayout(mazeName)
		(start, ends) = getStartEndPositions(maze)
		# printMaze(maze)
		print(mazeName)
		for searchType in searches:
			print(searchType)
			# start = time.clock()
			runSearch(maze, searchType)
			# cp.run("runSearch(maze, searchType)")
			# (winningState, numExposed) = search(maze, searchType)
			# end = time.clock()
			# print(f"time {end - start}")
			

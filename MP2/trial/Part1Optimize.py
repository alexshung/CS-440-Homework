from queue import PriorityQueue
import cProfile as cp
import time
import random as r

class Variable(object):
	"""docstring for Variable"""
	def __init__(self, point, values, pickedValue = '_', heur = 0):
		#r.random()
		super(Variable, self).__init__()
		self.point = point
		self.values = values
		self.pickedValue = pickedValue
		self.heur = heur

	def __str__(self):
		return f"{self.point}, values: {self.values}, picked: {self.pickedValue}"

	def __lt__(self, other):
		if self.heur == other.heur:
			return self.point[0] + self.point[1] < other.point[0] + other.point[1]
		return self.heur < other.heur
		
class State(object): # This is the assignment
	"""docstring for State"""
	def __init__(self, assignedVars, unassignedVars, varsMap):
		super(State, self).__init__()
		self.assignedVars = assignedVars
		self.unassignedVars = unassignedVars
		self.varsMap = varsMap

	# def __str__(self):
	# 	assigned = ""
	# 	unassigned = ""
	# 	for var in self.assignedVars:
	# 		assigned += str(var)
	# 	for var in self.unassignedVars:
	# 		unassigned += str(var)
	# 	return f"{assigned}, {unassigned}"
		

def readInput(fileName):
	with open(fileName) as f:
		content = [x.strip() for x in f.readlines()]
		content = [[content[y][x] for x in range(len(content[0]))] for y in range(len(content))]
		return content

def buildInitialState(puzzle):
	domain = set()
	assignedVars = {}
	unassignedVars = PriorityQueue()
	varsMap = {}
	test = 0
	for x in range(0, len(puzzle)):
		line = puzzle[x]
		for y in range(0, len(line)):
			char = puzzle[x][y]
			test += 1
			if char != '_':
				domain.add(char)
				varA = Variable((x,y), None, char, test)
				assignedVars[(x,y)] = varA
				# varsMap[varA.point] = varA
			else:
				varA = Variable((x,y), None, '_', test)
				unassignedVars.put(varA)
				varsMap[varA.point] = varA
	return (State(assignedVars, unassignedVars, varsMap), domain)

def printSol(state, puzzle, totalTime, explored):
	for var in state.assignedVars.values():
		(x,y) = var.point
		puzzle[x][y] = var.pickedValue
	printMap(puzzle)
	print(f"Took {totalTime}s and attempted assignment {explored}")
	return puzzle

def printDebug(state, puzzle):
	# for var in state.assignedVars.values():
		# (x,y) = var.point
	for x in range(len(puzzle)):
		for y in range(len(puzzle[x])):
			if (x, y) in state.assignedVars:
				puzzle[x][y] = state.assignedVars[(x,y)].pickedValue
			else:
				puzzle[x][y] = '_'
	printMap(puzzle)

def printMap(maze):
	for line in maze:
		print(''.join(line))

def isStateComplete(state, domain, length, width):
	if state.unassignedVars.empty():
		for x in range(length):
			for y in range(width):
				if (x,y) not in state.assignedVars:
					var = state.varsMap[(x,y)]
					var.values = domain
					state.unassignedVars.put(state.varsMap[(x,y)])
					print(f"added {state.varsMap[(x,y)]}, {state.unassignedVars.empty()}")
		return state.unassignedVars.empty()
	else:
		return False

def makeNextPoints(x,y):
	return [(x+1,y), (x,y+1), (x-1,y), (x, y-1)]

def isConsistent(state, point, color, ends, puzzleLength, puzzleWidth, domain):
	(x,y) = point
	# Would only see this from canAssign, and can assign an edge piece so return true
	# if x < 0 or y < 0 or x == puzzleWidth or y == puzzleLength:
	# 	return True
	nextPoints = makeNextPoints(x,y)
	numSame = 0
	numAssignedNeigh = 0
	for nextPoint in nextPoints:
		(x1, y1) = nextPoint
		if x1 < 0 or y1 < 0 or x1 == puzzleWidth or y1 == puzzleLength:
			numAssignedNeigh += 1
		elif nextPoint in state.assignedVars:
			numAssignedNeigh += 1

			var = state.assignedVars[nextPoint]
			values = var.values if var.values != None else domain
			if var.pickedValue != "_":
				if var.pickedValue == color:
					numSame += 1
			elif color in var.values and len(var.values) == 1:
				numSame += 1

	if numSame > 2:
		# print(f"numSame: {numSame} point: {point} color {color}")
		return False
	# Early termination case
	elif numAssignedNeigh == 3:
		# print(f"point: {point} color {color} numAssignedNeigh: {numAssignedNeigh}, {numSame}")
		return numSame > 0 if point not in ends else True
	elif numAssignedNeigh == 4:
		# print(f"point: {point} color {color} numAssignedNeigh: {numAssignedNeigh}, {numSame}")
		return numSame == 2 if point not in ends else numSame == 1
	else:
		return True

def canAssign(state, var, color, ends, puzzleLength, puzzleWidth, domain):
	(x,y) = var.point
	points = [var.point] + makeNextPoints(x,y)
	for point in points:
		spaceColor = state.assignedVars[point].pickedValue if point in state.assignedVars else color
		if point in state.assignedVars or point == var.point:
			pointConsistent = isConsistent(state, point, spaceColor, ends, puzzleLength, puzzleWidth, domain)
			if not pointConsistent:
				# print(f"{point} was determiend to be inconsistent")
				return False
	return True

def cspRandom(state, domain, ends, puzzleLength, puzzleWidth, puzzle, acc):
	
	if isStateComplete(state, domain, puzzleLength, puzzleWidth):
		return (state, acc)
	var = state.unassignedVars.get()
	for color in domain:
		var.pickedValue = color
		state.assignedVars[var.point] = var
		# print("\n")
		# printDebug(state, puzzle)
		# time.sleep(1)
		acc += 1
		if canAssign(state, var, color, ends, puzzleLength, puzzleWidth, domain):

			(result, acc) = cspRandom(state, domain, ends, puzzleLength, puzzleWidth, puzzle, acc)
			if result != None:
				return (result, acc)
		state.assignedVars.pop(var.point)
		var.pickedValue = '_'
	state.unassignedVars.put(var)
	return (None, acc)

def buildSolName(puzzle):
	return f"sol{puzzle}"

def cspSmart(state, domain, ends, puzzleLength, puzzleWidth, puzzle, acc):
	if isStateComplete(state, domain, puzzleLength, puzzleWidth):
		return (state, acc)

	# if updateSingleValue(state, domain, var, ends, puzzleLength, puzzleWidth):
	origValues = state.varsMap.copy()

	if updateAllValues(state, domain, ends, puzzleLength, puzzleWidth):

		var = state.unassignedVars.get()
		varDomain = var.values
		# print(f"point {var.point}:{varDomain}")
		for color in varDomain:
			var.pickedValue = color
			state.assignedVars[var.point] = var


			printDebug(state, puzzle)
			print("\n")
			time.sleep(0.5)

			acc += 1
			(result, acc) = cspSmart(state, domain, ends, puzzleLength, puzzleWidth, puzzle, acc)
			if result != None:
				# print("finished")
				return (result, acc)
			state.assignedVars.pop(var.point)
			var.pickedValue = '_'
		var.values = domain
		state.unassignedVars.put(var)
	for varPoint in state.varsMap:
		var = state.varsMap[varPoint]
		var.values = origValues[varPoint].values
		var.heur = origValues[varPoint].heur
	return (None, acc)

def updateSingleValue(state, domain, var, ends, puzzleLength, puzzleWidth):
	varsHolder = [var]
	while varsHolder:
		nextVar = varsHolder.pop()
		origValue = nextVar.values
		varDomain = nextVar.values if nextVar.values != None else domain
		possibleValues = set()
		for color in varDomain:
			nextVar.pickedValue = color
			state.assignedVars[nextVar.point] = nextVar
			if canAssign(state, nextVar, color, ends, puzzleLength, puzzleWidth, domain):
				possibleValues.add(color)

				# print(f"{color} was valid for {nextVar.point}")
			# else:
				# print(f"{color} was not valid for {nextVar.point}")
			state.assignedVars.pop(nextVar.point)
			nextVar.pickedValue = '_'
		if not possibleValues:
			print(f"terminated early. No values for {nextVar.point}")
			return False
		if possibleValues != origValue:
			point = nextVar.point
			varsHolder + makeNextPoints(point[0], point[1])
		nextVar.values = possibleValues
		nextVar.heur = len(possibleValues)
		print(f"{nextVar.point}: {nextVar.values}")
	return True


def updateAllValues(state, domain, ends, puzzleLength, puzzleWidth):
	pq = PriorityQueue()
	poppedValues = set()
	retVal = True
	while not state.unassignedVars.empty():
		var = state.unassignedVars.get()

		# print(f"updatePop: {var}")
		
		poppedValues.add(var)
		# TODO: Change this to PQ, and then use some other class to define a heuristic to identify least constraining value
		possibleValues = set()
		varDomain = var.values if var.values != None else domain
		for color in varDomain:
			var.pickedValue = color
			state.assignedVars[var.point] = var
			if canAssign(state, var, color, ends, puzzleLength, puzzleWidth, domain):
				possibleValues.add(color)
			# 	print(f"{color} was valid for {var.point}")
			# else:
			# 	print(f"{color} was not valid for {var.point}")
			state.assignedVars.pop(var.point)
			var.pickedValue = '_'
		if not possibleValues:
			# print(f"terminated early. No values for {var}")

			for val in poppedValues:
				state.unassignedVars.put(val)
				print(f"Adding {val} back")
			retVal = False
			return retVal
		var.values = possibleValues
		var.heur = len(possibleValues)
		# print(f"updatePop: {var}")
		pq.put(var)
	state.unassignedVars = pq
	return retVal

# When building the initial state
# Initialize the variables with values that are possible
	# Set the heuristic to the variables be the # of values remaining
# Need to update legal values
# Figure out how to do least constrained value?

if __name__ == "__main__":
	fileNames = [
	# 'input55.txt',
	'input77.txt',
	# 'input88.txt',
	# 'input991.txt',
	# 'input10101.txt',
	# 'input10102.txt'
	]
	sols = []
	for puzzle in fileNames:
		print(puzzle)
		puzzle = readInput(puzzle)

		(initState, domain) = buildInitialState(puzzle)
		ends = initState.assignedVars.copy()
		puzzleLength = len(puzzle)
		puzzleWidth = len(puzzle[0])
		startTime = time.clock()

		# (finalState, acc) = cspRandom(initState, domain, ends, len(puzzle[0]),len(puzzle), puzzle, 0)
		# updateAllValues(initState, domain, ends, puzzleLength, puzzleWidth)
		(finalState, acc) = cspSmart(initState, domain, ends, len(puzzle), len(puzzle[0]), puzzle, 0)
		# print(finalState.varsMap[(3,1)])
		# print(finalState.varsMap[(6, 5)])
		totalTime = time.clock() - startTime
		sols.append(printSol(initState, puzzle, totalTime, acc))

	# Check solutions
	for x in range(0, len(fileNames)):
		fileName = fileNames[x]
		sol = readInput(buildSolName(fileName))
		assert(sol == sols[x])


# 8 x 8 board with the first two lines set up
# Pieces can either move forward, or diagonal either way
# Implement two strats: minimax search and alpha-beta search
# Implement two eval functions: offensive and defensive. Use these when the max depth of the tree is reached
# Try setting depth to be 3

# if False:
# 	Implement minimax search for a search tree depth of 3.
# 	Implement alpha-beta search for a search tree of depth more than that of minimax.
# 	Implement Defensive Heuristic 1 and Offensive Heuristic 1.
# 		Defensive: 2*(number_of_own_pieces_remaining) + random()
# 		Offensive: 2*(30 - number_of_opponent_pieces_remaining) + random()
# 	Design and implement an Offensive Heuristic 2 with the idea of beating Defensive Heuristic 1.
# 	Design and implement an Defensive Heuristic 2 with the idea of beating Offensive Heuristic 1.

import random as r
import time
import copy as cp
import cProfile
from Heuristics import defensiveHeuristic2, defensiveHeuristic1, offensiveHeuristic1, offensiveHeuristic2

# Colors:
bp = "B"
wp = "W"
boardSize = 8
maxScore = 100000

# def defensiveHeuristic1(board, color, d, isBoardWon, t):
# 	numPieces = len(board.black) if color == bp else len(board.white)
# 	return 2 * numPieces  + r.random()

def printPieces(pieces):
	st = ""
	for piece in pieces:
		st += piece.__str__() + " "
	return st

class Board():
	"""docstring for Board"""
	def buildPieceMap(self):
		pieceMap = {}
		for piece in self.black:
			pieceMap[(piece.x, piece.y)] = piece
		for piece in self.white:
			pieceMap[(piece.x, piece.y)] = piece
		self.pieceMap = pieceMap
		self.bestMove = []

	def __init__(self, black, white):
		self.black = black
		self.white = white
		self.buildPieceMap()

	def pop(self, piece):
		color = piece.color
		if color == wp:
			self.white.remove(piece)
		else:
			self.black.remove(piece)
		self.pieceMap.pop((piece.x, piece.y))

	def add(self, piece):
		color = piece.color
		if color == wp:
			self.white.add(piece)
		else:
			self.black.add(piece)
		if (piece.x, piece.y) in self.pieceMap:
			print(f"AS: Collision -> {self.pieceMap[(piece.x, piece.y)]} : {piece}")
		self.pieceMap[(piece.x, piece.y)] = piece

	def hasPiece(self, coord):
		return coord in self.pieceMap

	# def deepcopy(self):
	# 	return Board(self.black.deepcopy(), self.white.deepcopy())

	def makeMove(self, movePos, piece):
		self.pieceMap.pop((piece.x, piece.y))
		piece.x = movePos[0]
		piece.y = movePos[1]
		
		takenPiece = None
		if movePos in self.pieceMap:
			takenPiece = self.pieceMap[movePos]
			# print(f"Really taken? taken: {takenPiece}, by: {piece}")
			self.black.remove(takenPiece) if takenPiece.color == bp else self.white.remove(takenPiece)
		self.pieceMap[movePos] = piece
		return takenPiece

class Piece():
	"""docstring for Piece"""
	def __init__(self, color, x, y):
		self.color = color
		self.x = x
		self.y = y
	
	def copy(self):
		return Piece(self.color, self.x, self.y)

	def __str__(self):
		return f"({self.x}, {self.y}): {self.color}"
# class Move():
# 	def __init__(self, x, y, type):
# 		self.x = x
# 		self.y = y
def minimaxSearch():
	pass

def printBoard(board):
	arrayBoard = [['_' for x in range(boardSize)] for y in range(boardSize)]
	for piece in board.pieceMap.values():
		arrayBoard[piece.y][piece.x] = piece.color
	
	for line in arrayBoard:
		print(''.join(line))
	print()

# Do I want a board that keeps white and black pieces? Seems to make the most sense
def buildInitialBoard():
	blackPieces = set()
	whitePieces = set()
	for x in range(boardSize):
		for y in range(2):
			blackPieces.add(Piece(bp, x, y))
			whitePieces.add(Piece(wp, x, boardSize - y - 1))
	return Board(blackPieces, whitePieces)

# Return the coords that the piece can move to
# Forward, diag right, diag left
def makeMoves(piece):
	moves = []
	newY = piece.y + 1 if piece.color == bp else piece.y - 1

	moves.append((piece.x + 1, newY))
	moves.append((piece.x - 1, newY))
	moves.append((piece.x, newY))
	return moves

def isValid(move, piece, board, depth):
	if move[0] >= boardSize or move[0] < 0 or move[1] >= boardSize or move[1] < 0:
		return False
	# moved up, only valid if there isn't a piece there
	if move[0] == piece.x:
		return not board.hasPiece(move)
	# moved diag. Only valid if there isn't a piece there or if the piece is of a different color
	else:
		return not board.hasPiece(move) or board.pieceMap[move].color != piece.color
# Victory is either no pieces, or there exists a piece on the other side of the board
def boardWon(board):
	winningState = len(board.white) == 0 or len(board.black) == 0
	if winningState:
		return winningState
	for piece in board.pieceMap.values():
		if piece.y == boardSize - 1 and piece.color == bp:
			return True
		elif piece.y == 0 and piece.color == wp:
			return True
	return winningState

def playGame(board, color, depth, playerColor, depthLimit, heur = defensiveHeuristic1, isAlphaBeta = False, parentScore = None):
	isMax = color == playerColor

	bestBoard = None
	myPieces = board.white if color == wp else board.black

	# TODO: Make board won score part of the heuristic
	isBoardWon = boardWon(board)
	if depth > depthLimit - 1 or (isAlphaBeta and isBoardWon):
		score = heur(board, playerColor, depth, isBoardWon, isMax)
		return (score, None, 1)
	
	# TODO: We need to change this to handle parent score to do alpha beta pruning
	bestScore = None
	bestMove = None
	shortCircuit = False
	totalExpanded = 0
	if depth == 0:
		printPieces(myPieces)
	for piece in myPieces:

		if isAlphaBeta:
			if shortCircuit:
		 		break
		# if depth == 0:
		# 	print(f"Depth 0: {piece}")
		board.pop(piece)
		movedPiece = piece.copy()
		board.add(movedPiece)

		# Make list of moves, going up, diag right, diag left
		allMoves = makeMoves(piece)
		bestPieceScore = None
		bestPieceMove = None
		for move in allMoves:
			# if depth == 0:
			# 	print(f"{move} : {isValid(move, piece, board, depth)}")
			# If it's a valid move, make that move and continue down until depth is ht
			if isValid(move, piece, board, depth):
				takenPiece = board.makeMove(move, movedPiece)

				nextColor = bp if color == wp else wp
				# TODO: Potential speed increase by returning if the board is won after making a move
				(boardScore, nothing, numNodesExpanded) = playGame(board, nextColor, depth + 1, playerColor, depthLimit, heur, isAlphaBeta, bestPieceScore)
				
				# TODO: Don't count leaves as nodes somehow
				totalExpanded += numNodesExpanded
				
				if not boardScore:
					boardScore = maxScore if isMax else 0

				# if boardWon(board):
				# 	print(f" {depth}, {bestPieceScore}, {boardScore}")
				isBetter = True if not bestPieceScore else boardScore > bestPieceScore if isMax else boardScore < bestPieceScore
				# if depth == 1:
				# 	print(f"{isBetter} : {bestPieceScore} : {boardScore} : {piece} : {move} : {playerColor}")
				# If the cut off point was better than anything we've seen, save that move for this piece
				# TODO: Eval if we need bestPieceScore
				if isBetter:
					bestPieceScore = boardScore
					bestPieceMove = (move, piece)

				board.pop(movedPiece)
				movedPiece.x = piece.x
				movedPiece.y = piece.y
				board.add(movedPiece)
				if takenPiece:
					board.add(takenPiece)

				isShortCircuit = False if not parentScore else bestPieceScore > parentScore if isMax else bestPieceScore < parentScore
				if isAlphaBeta:
					if (boardWon(board) and isMax) or isShortCircuit:
						shortCircuit = True
						break

		isBetterPiece = True if not bestScore else False if not bestPieceScore else bestPieceScore > bestScore if isMax else bestPieceScore < bestScore
		if isBetterPiece:
			bestScore = bestPieceScore
			bestMove = bestPieceMove
				
		# Here because the last move of the moved piece might not be valid, so it won't be added back on
		board.pop(movedPiece)
		board.add(piece)
	# if depth != 2:
	# 	print(f"{depth} Best score: {bestScore}")
	return (bestScore, bestMove, totalExpanded)

class Player():
	def __init__(self, depthLimit, isAlphaBeta, heur):
		self.depthLimit = depthLimit
		self.isAlphaBeta = isAlphaBeta
		self.heur = heur

	def __str__(self):
		return self.__name__()

	def __name__(self):
		alpha = "AlphaBeta" if self.isAlphaBeta else "Minimax"
		return f"{alpha} - {self.heur.__name__}"
def runGame(p1, p2):
	board = buildInitialBoard()
	printBoard(board)
	isWhite = True

	# Stores the number of game tree nodes expanded and the amount of time taken
	statsTracker = {}
	statsTracker[True] = [0, 0]
	statsTracker[False] = [0, 0]
	moves = 0
	while not boardWon(board):
		startTime = time.clock()
		(score, bestMove, nodesExpanded) = playGame(board, wp, 0, wp, p1.depthLimit, p1.heur, p1.isAlphaBeta) if isWhite else playGame(board, bp, 0, bp, p2.depthLimit, p2.heur, p2.isAlphaBeta)
		(accNodesExpanded, timeTaken) = statsTracker[isWhite]
		statsTracker[isWhite] = (accNodesExpanded + nodesExpanded, timeTaken + time.clock() - startTime)

		# print(f"About to make a real move: {bestMove[0]} : {bestMove[1]}")
		
		board.makeMove(bestMove[0], bestMove[1])
		# print()
		printBoard(board)
		# time.sleep(.25)
		isWhite = not isWhite

		moves += 1
	winner = p2 if isWhite else p1
	numMovesWhite = moves / 2
	numMovesBlack = moves / 2
	if isWhite:
		numMovesBlack += 1
	else:
		numMovesWhite += 1
	whiteNodeCount = statsTracker[True][0]
	blackNodeCount = statsTracker[False][0]
	whiteTime = statsTracker[True][1]
	blackTime = statsTracker[False][1]

	print("Final Board:")
	printBoard(board)
	print(f"winning player: {winner}")
	print(f"W = {p1}: # of game tree nodes -> {whiteNodeCount}, avg nodes per move -> {round(whiteNodeCount / numMovesWhite)}, avg amount of time -> {round(whiteTime / numMovesWhite, 3)}, # of pieces captured -> {16 - len(board.black)}")
	print(f"B = {p2}: # of game tree nodes -> {blackNodeCount}, avg nodes per move -> {round(blackNodeCount / numMovesBlack)}, avg amount of time -> {round(blackTime / numMovesBlack, 3)}, # of pieces captured -> {16 - len(board.white)}")
	print(f"total moves: {moves}")
	return winner

def runMinimaxSearch(heur1, heur2):
	depthLimit = 3
	p1 = Player(depthLimit, False, heur1)
	p2 = Player(depthLimit, False, heur2)
	runGame(p1, p2)

def runAlphaDefensive():
	depthLimit = 3
	p1 = Player(depthLimit, False, defensiveHeuristic1)
	p2 = Player(depthLimit, False, defensiveHeuristic1)
	runGame(p1, p2)

def runAlphaBeta():
	depth = 3
	offensive = Player(depth, True, offensiveHeuristic1)
	defensive = Player(depth, True, defensiveHeuristic1)
	runGame(offensive, defensive)

#####################
### Required Runs ###
#####################
def runAlpahVsMinimax():
	# depthAlpha = 5
	depthMin = 3
	alpha = Player(depthAlpha, True, offensiveHeuristic1)
	minMax = Player(depthMin, False, offensiveHeuristic1)
	return runGame(alpha, minMax)

def runOffensive2VsDefensive1():
	depth = 3
	offensive2 = Player(depth, True, offensiveHeuristic2)
	defensive1 = Player(depth, True, defensiveHeuristic1)
	return runGame(offensive2, defensive1)

def runDef2VsOff1():
	depth = 3
	def2 = Player(depth, True, defensiveHeuristic2)
	off1 = Player(depth, True, offensiveHeuristic1)
	return runGame(def2, off1)

def runOff2VsOff1():
	depth = 3
	off2 = Player(depth, True, offensiveHeuristic2)
	off1 = Player(depth, True, offensiveHeuristic1)
	return runGame(off2, off1)

def runDef2VsDef1():
	depth = 3
	def2 = Player(depth, True, defensiveHeuristic2)
	def1 = Player(depth, True, defensiveHeuristic1)
	return runGame(def2, def1)

def runOff2VsDef2():
	depth = 3
	off2 = Player(depth, True, offensiveHeuristic2)
	def2 = Player(depth, True, defensiveHeuristic2)
	return runGame(off2, def2)

def runxTimes(funct, x):
	victoryMap = {}
	for y in range(0, x):
		winner = funct()
		if winner.__name__() in victoryMap:
			victoryMap[winner.__name__()] += 1
		else:
			victoryMap[winner.__name__()] = 1
	for p in victoryMap:
		print(f"{p} won {victoryMap[p]}")

def main():
	
	# runAlphaDefensive()
	# runMinimaxSearch(defensiveHeuristic1, defensiveHeuristic1)
	# runAlphaBeta()

	# Required runs
	
	# runAlpahVsMinimax()
	runOffensive2VsDefensive1()
	# runDef2VsOff1()
	# runOff2VsOff1()
	# runDef2VsDef1()
	# runOff2VsDef2()

	# Run in bulk
	# runxTimes(runOffensive2VsDefensive1, 10)
	# runxTimes(runDef2VsOff1, 10)
	# runxTimes(runOff2VsOff1, 10)

if __name__ == '__main__':
	cProfile.run('main()')
	# main()






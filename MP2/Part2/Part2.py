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
# Colors:
bp = "B"
wp = "W"
boardSize = 8
depthLimit = 3

def defensiveHeuristic1(board, color):
	numPieces = len(board.black) if color == bp else len(board.white)
	return 2 * numPieces + r.random()

def offensiveHeuristic1(board, color):
	numPiecesLeft = len(board.black) if color == wp else len(board.white)
	return 2 * (30 - numPiecesLeft) + r.random()

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
	moves = set()
	newY = piece.y + 1 if piece.color == bp else piece.y - 1
	# Could I make this into an enum?
	moves.add((piece.x, newY))
	moves.add((piece.x + 1, newY))
	moves.add((piece.x - 1, newY))
	return moves

def isValid(move, piece, board):
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

# def betterBoard(curBestBoard, evalBoard, color, heur = defensiveHeuristic1):
# 	return heur(curBestBoard, color) > heur(evalBoard, color)

def playGame(board, color, depth, heur = defensiveHeuristic1):
	isMax = color == wp

	bestBoard = board
	myPieces = board.white if isMax else board.black
	# Stop after the 6th move, meaning each player has moved 3 times. 
	# TODO: Re-evaluate if this should just be 3
	if depth > depthLimit - 1 or boardWon(board):
		# print(f"returning cause of depth {depth} or {boardWon(board)}")
		return board

	# For all of my pieces
	# numPieces = 0
	
	# print(f"{depth}: {st}")
	
	bestScore = 0

	for piece in myPieces:
		# print(f"{depth}: {piece}")
		board.pop(piece)
		movedPiece = piece.copy()
		board.add(movedPiece)

		# Make list of moves, going up, diag right, diag left
		allMoves = makeMoves(piece)
		for move in allMoves:
			# If it's a valid move, make that move and continue down until depth is ht
			if isValid(move, piece, board):
				# print(piece)
				takenPiece = board.makeMove(move, movedPiece)
				
				# printBoard(board)
				# time.sleep(.5)

				finalBoard = playGame(board, bp, depth + 1, heur) if isMax else playGame(board, wp, depth + 1, heur)
				
				# If the cut off point was better than anything we've seen, save that move for this piece
				# Question: Why not save that move across all pieces? 
				# TODO: Will need to track what the actual move was on which piece which resulted in this
				boardScore = heur(finalBoard, piece.color)
				if boardScore > bestScore:
					# print(f"Found better board: {depth}")
					bestScore = boardScore
					bestBoard = cp.deepcopy(finalBoard)
					bestBoard.bestMove = (move, piece)
					# printBoard(bestBoard)
				board.pop(movedPiece)
				movedPiece.x = piece.x
				movedPiece.y = piece.y
				board.add(movedPiece)
				if takenPiece:
					board.add(takenPiece)

		board.pop(movedPiece)
		board.add(piece)
	return bestBoard

def main():
	board = buildInitialBoard()
	printBoard(board)
	isWhite = True
	while not boardWon(board):
		nextBoard = playGame(board, wp, 0, defensiveHeuristic1) if isWhite else playGame(board, bp, 0, offensiveHeuristic1)
		board.makeMove(nextBoard.bestMove[0], nextBoard.bestMove[1])
		print()
		printBoard(board)
		isWhite = not isWhite

if __name__ == '__main__':
	cProfile.run('main()')






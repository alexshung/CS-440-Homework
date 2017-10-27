import random as r

# Colors:
bp = "B"
wp = "W"
boardSize = 8
maxScore = 100000


def defensiveHeuristic1(board, color, *args):
	numPieces = len(board.black) if color == bp else len(board.white)
	return 2 * numPieces  + r.random()


def offensiveHeuristic1(board, color, *args):
	numPiecesLeft = len(board.black) if color == wp else len(board.white)
	return 2 * (30 - numPiecesLeft) + r.random()

def defensiveHeuristic2(board, color, depth, isBoardWon, isMax):
	score = None
	if isBoardWon:
		score = maxScore - depth
		if isMax:
			score = score * -1
		score = -1 * maxScore + depth if isMax else maxScore - depth
	else:
		numPieces = len(board.black) if color == bp else len(board.white)
		basicHeur = 2 * numPieces
		positionScore = getFarthestPiece(board, color)
		oppColor = wp if color == bp else bp
		opponentScore = defensiveHeuristic1(board, oppColor)
		score = basicHeur + r.random() - depth + positionScore - opponentScore
	return score

def offensiveHeuristic2(board, color, depth, isBoardWon, isMax):
	score = None
	if isBoardWon:
		score = maxScore - depth
		if isMax:
			score = score * -1
		score = -1 * maxScore + depth if isMax else maxScore - depth
	else:
		numPiecesLeft = len(board.black) if color == wp else len(board.white)
		basicHeur = 2 * (30 - numPiecesLeft)
		positionScore = getFarthestPiece(board, color)

		oppColor = wp if color == bp else bp
		opponentScore = offensiveHeuristic1(board, oppColor)
		oppPositionScore = getFarthestPiece(board, oppColor)
		score = basicHeur + r.random() - depth + positionScore - opponentScore #- oppPositionScore
	return score

# This returns the farthest y coordinate of the piece
# For black that will be the greatest y, for white it will be the least
def getFarthestPiece(board, color):
	isMax = True if color == bp else False
	myPieces = board.black if color == bp else board.white
	farthest = None
	for piece in myPieces:
		curPos = piece.y #* 2 + piece.x
		isBetter = True if not farthest else curPos > farthest if isMax else curPos < farthest
		if isBetter:
			farthest = curPos
	return farthest
import random as r
import math
import time
import concurrent.futures as cf

minXVelocity = 0.3
paddleHeight = 0.2
paddleAtTop = 1
paddleAtBottom = 1 - paddleHeight
# These correspond to [nothing, down, up]
allowedPaddleMoves = [0, 0.04, -0.04]

xRange = 0.015
yRange = 0.03
# Rewards: +1 if you hit the wall, -1 when you lose, and 0 otherwise
class State(object):
	def __init__(self, ball_x, ball_y, vel_x, vel_y, paddle_y):
		super(State, self).__init__()
		self.ball_x = ball_x
		self.ball_y = ball_y
		self.vel_x = vel_x
		self.vel_y = vel_y
		# Represents the height of the paddle
		self.paddle_y = paddle_y

	def incrementBall(self):
		self.ball_x += self.vel_x
		self.ball_y += self.vel_y

	def dealWithBounce(self):
		# Bouncing off the top
		if self.ball_y < 0:
			self.ball_y = -self.ball_y
			self.vel_y = -self.vel_y
		# Bouncing off the bottom
		elif self.ball_y > 1:
			self.ball_y = 2 - self.ball_y
			self.vel_y = -self.vel_y

		# Bouncing off wall / left side of screen
		if self.ball_x < 0:
			self.ball_x = -self.ball_x
			self.vel_x = -self.vel_x

		# Bouncing off the paddle
		if self.ball_x > 1 and self.ball_y > self.paddle_y and self.ball_y < self.paddle_y + paddleHeight:
			self.ball_x = 2 * 1 - self.ball_x
			self.vel_x = -max(0.03, self.vel_x + r.uniform(-xRange, xRange))
			self.vel_y = -self.vel_y + r.uniform(-yRange, yRange)

		# Correct velocity if above 1
		if self.vel_x < -1:
			self.vel_x = -1
		elif self.vel_x > 1:
			self.vel_x = 1
		if self.vel_y < -1:
			self.vel_y = -1
		elif self.vel_y > 1:
			self.vel_y = 1

	def movePaddle(self, paddleMove):
		self.paddle_y += paddleMove
		if self.paddle_y < 0:
			self.paddle_y = 0
		elif self.paddle_y + paddleHeight > 1:
			self.paddle_y = 1 - paddleHeight

	def makeMove(self, paddleMove):
		self.movePaddle(paddleMove)
		self.incrementBall()
		reward = 0
		if self.ball_x > 1:
			reward = 1
		self.dealWithBounce()
		if self.ball_x > 1:
			reward = -1
		return reward

	def printSelf(self):
		gridSize = 12
		paddlePos = 12
		(discPos, discXVel, discYVel, discPaddle) = buildDiscreteState(self, gridSize, paddlePos)
		dState = (discPos, discXVel, discYVel, discPaddle)
		paddleStart = self.paddle_y * 100 / gridSize
		paddleEnd = (self.paddle_y + paddleHeight) * 100 / gridSize
		for y in range(gridSize):
			board = ""
			for x in range(gridSize + 1):
				char = " "
				if (x, y) == discPos:
					char = "."
				if x == gridSize - 1 and y >= paddleStart and y <= paddleEnd:
					char = "]"
				if x == gridSize:
					char = "|"
				board += char
			print(f"{board}\n")
		print(f"Discrete State: {dState}")
		print(f"State: {self.ball_x}, {self.ball_y}, {self.vel_x}, {self.vel_y}, paddle: {self.paddle_y}")
		print("----------------------------")

def discreteXVelocity(xVel):
	return 1 if xVel >= 0 else -1

def discreteYVelocity(yVel):
	return 1 if yVel > 0.015 else -1 if yVel < -0.015 else 0

def buildDiscreteState(state, gridSize, paddlePossibility):
# Pretend it's 12x12 grid, same state if ball lies within same cell in table
	discPos = (math.floor(state.ball_x * 100 / gridSize), math.floor(state.ball_y * 100 / gridSize))
# Discretize the X-vel of ball into + or -
	discXVel = discreteXVelocity(state.vel_x)
# Discretize the Y-vel of ball into +, 0, or -. 0 If 0.015< vel < 0.015
	discYVel = discreteYVelocity(state.vel_y)
# Paddle location = floor(12 * paddle_y / (1- paddle_height)) if paddle_y = 1 - paddle_height, paddle_y = 11
	discPaddle = math.floor(paddlePossibility * state.paddle_y / (1 - paddleHeight)) if state.paddle_y < 1 - paddleHeight else paddlePossibility - 1
	return (discPos, discXVel, discYVel, discPaddle)

def getPaddleMove(bestNextMove, t):
	explorationChance = 1 - 1000 / (1000 + t/100)
	if r.random() < explorationChance:
		return allowedPaddleMoves[r.randint(0, 2)]
	return bestNextMove

def updateQFunction(reward, key, qFunction, t, bestNextState):
	gamma = 0.8
	avgReward = 0
	times = 0
	if key in qFunction:
		(avgReward, times) = qFunction[key]
	alpha = 1000 / (1000 + times)
	qFunction[key] = (avgReward + alpha * (reward + gamma * bestNextState - avgReward), times + 1)

def getBestNextMove(discreteState, qFunction):
	bestReward = None
	bestMove = None
	(discPos, discXVel, discYVel, discPaddle) = discreteState
	r.shuffle(allowedPaddleMoves)
	for move in allowedPaddleMoves:
		key = (discPos, discXVel, discYVel, discPaddle + move, move)
		nextReward = 0 if key not in qFunction else qFunction[key][0]
		if bestReward == None or bestReward < nextReward:
			bestReward = nextReward
			bestMove = move
	return (bestMove, bestReward)

def runSingleGame(qFunction, t):
	bestNextMove = allowedPaddleMoves[0]
	bounced = 0
	c = 0
	state = State(0.5, 0.5, 0.03, 0.01, 0.5 - paddleHeight / 2)

	while(state.ball_x < 1):
		paddleMove = getPaddleMove(bestNextMove, t)
		if c <= 1:
			paddleMove = 0.04
			c += 1
		elif bounced == 0:
			paddleMove = 0

		reward = state.makeMove(paddleMove)

		discreteState = buildDiscreteState(state, 12, 12)

		# time.sleep(0.1)
		# state.printSelf()
		if reward == 1:
			bounced += 1
		(bestNextMove, bestReward) = getBestNextMove(discreteState, qFunction)
		(discPos, discXVel, discYVel, discPaddle) = discreteState
		key = (discPos, discXVel, discYVel, discPaddle, paddleMove)
		updateQFunction(reward, key, qFunction, t, bestReward)

		# if reward != 0:
		# 	print(reward)
		# 	for key in qFunction:
		# 		print(f"{key}:{qFunction[key]}")
		t += 1
	# print(buildDiscreteState(state, 12, 12))
	# print(f"{state.ball_x}, {state.ball_y} : {state.paddle_y}, {bounced}")
	# print(bounced)
	return bounced

def runGame(gameNum):
	t = 0
	qFunction = {}
	numBounces = list()
	
	for i in range(gameNum):
		numBounces.append(runSingleGame(qFunction, t))
	print(numBounces)
	for key in qFunction:
		print(f"{key}:{qFunction[key]}")

if __name__ == '__main__':
	runGame(100)

		
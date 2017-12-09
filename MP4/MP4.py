import numpy as np
from collections import Counter, defaultdict
from math import log
from sklearn.metrics import confusion_matrix
import json

class Number():
	"""docstring for Number"""
	def __init__(self, data, label):
		self.data = data
		self.label = label
		self.classifiedLabel = None

class Perceptron():
	def __init__(self, weights, label):
		self.weights = weights
		self.label = label

	def __str__(self):
		return f"{self.label}:{self.weights}"

class PerceptronEncoder(json.JSONEncoder):
	def default(self, obj):
		# if not isinstance(obj, Perceptron):
		# 	return super(PerceptronEncoder, self).default(obj)
		return obj.__dict__

def convertToNums(x):
	return [0 if y == ' ' else 1 for y in x]

def convertSoundToNums(x):
	return [1 if y == ' ' else 0 for y in x]
def readNumbers(fileName):
	with open(fileName) as f:
		content = [convertToNums(x.replace("\n", "")) for x in f.readlines()]
		return content

def basicReader(fileName):
	with open(fileName) as f:
		return [x for x in f.readlines()]

def readNumbersSegmented(fileName, reader = readNumbers, rowLength = 28, skip = 0):
	block = reader(fileName)
	testNumbers = list()
	lineNum = 0

	singleNum = list()
	skipped = 0
	for line in block:
		if skipped <= 1:
			if lineNum % rowLength == 0 and lineNum > 0 and singleNum:
				singleNum = np.array(singleNum)
				testNumbers.append(singleNum.flatten())
				singleNum = list()
				skipped = skip
			if line:
				lineNum += 1
				singleNum.append(line)
		else:
			skipped -= 1

	testNumbers.append(np.array(singleNum).flatten())
	return testNumbers


def readLabels(fileName):
	with open(fileName) as f:
		return [x.strip() for x in f.readlines()]
def buildNumbers(dataDir, labelDir):
	data = readNumbersSegmented(dataDir)
	labels = readLabels(labelDir)
	numbers = []
	for i in range(len(data)):
		numbers.append(Number(data[i], labels[i]))
	return (numbers, set(labels))

def trainPerceptrons(numbers, trainingLabels, epochs, bias, learningRate, savedPerceptronFile, isWeightRand, intermediateCheck = True, randomized = False):
	perceptrons = list()
	# initialize the perceptrons
	for label in trainingLabels:
		weightLenght = len(trainingData[0].data)
		weights = np.zeros(weightLenght) if not isWeightRand else np.random.rand(weightLenght)
		perceptrons.append(Perceptron(weights, label))

	curEpoch = 0
	holdOut = numbers[4000:]
	training = numbers #[:4000]
	while(curEpoch < epochs):
		if randomized:
			np.random.shuffle(training)
		for number in training:
			for perceptron in perceptrons:
				weights = perceptron.weights
				expectedLabel = perceptron.label
				# Classify with current weights
				data = number.data
				y = 1 if number.label == expectedLabel else -1
				classifiedLabel = np.sign(weights.dot(data) + bias)
				# If classified incorrectly update weights
				if y != classifiedLabel:
					weights = weights + learningRate(curEpoch) * (y - classifiedLabel) * data
				perceptron.weights = weights
		if intermediateCheck:
		 # and curEpoch != 0 and curEpoch % 20 == 0:
			(cm, correctPercent) = testPerceptrons(holdOut, perceptrons)
			fileName = f"epoch.data.{savedPerceptronFile}.csv"
			with open(fileName, "a") as f:
				f.write(f"{curEpoch},{correctPercent}\n")
		curEpoch += 1
	return perceptrons

def evaluation(results, testLabels):
	
	confusionMatrix = confusion_matrix(testLabels, results)

	resultsMap = {}
	correctHeur = 0
	for i in range(len(confusionMatrix)):
		totalClassified = 0
		row = confusionMatrix[i]
		correct = 0
		for j in range(len(row)):
			totalClassified += row[j]
			if i == j:
				correct = row[j]
		resultsMap[i] = (correct / totalClassified) * 100
		correctHeur += correct

	for key in resultsMap:
		print(f"Class {key}: {resultsMap[key]}% correct")
	return (confusionMatrix, correctHeur / len(results) * 100)

def testPerceptrons(testData, perceptrons):
	expectedLabels = list()
	classifiedLabels = list()
	for number in testData:
		bestGuess = None
		bestClass = None
		for perceptron in perceptrons:
			guess = np.array(perceptron.weights).dot(number.data)
			if not bestGuess or guess > bestGuess:
				bestGuess = guess
				bestClass = perceptron.label
		expectedLabels.append(number.label)
		classifiedLabels.append(bestClass)
	return evaluation(classifiedLabels, expectedLabels)

def savePerceptrons(perceptrons, fileName):
	with open(fileName, "w") as f:
		for p in perceptrons:
			p.weights = p.weights.tolist()
			f.write(f"{json.dumps(p, cls=PerceptronEncoder)}\n")

def readPerceptrons(fileName):
	perceptrons = list()
	with open(fileName) as f:
		for p in f.readlines():
			perceptron = json.loads(p.strip())
			perceptrons.append(Perceptron(perceptron["weights"], perceptron["label"]))
	return perceptrons

def basicLearningRate(t):
	return 1000 / (1000 + t)

def penalizedLearningRate(t):
	return 1000 / ((1000 + t) * 3)

def lenientLearningRate(t):
	return 1000 / ((1000 + t) / 2)

def findBestConfiguration(trainingData, trainingLabels, testData):
	################################
	## Things to mess around with ##
	################################
	epochs = 20 # 10
	learningRates = [basicLearningRate, penalizedLearningRate, lenientLearningRate]
	biasList = [0, 1]

	best = None
	bestStatic = None
	retVal = None
	# First find best staticc - bias and learning rate function
	isWeightRand = False
	randomized = False
	savedPerceptronFile = None
	holdOut = trainingData[4000:]
	numbers = trainingData[:4000]
	for bias in biasList:
		for learningRate in learningRates:
			identifier = f"perceptrons.{epochs}.{bias}.{randomized}.{learningRate.__name__}.isWeightRand.{isWeightRand}.txt"
			print(identifier)
			savedPerceptronFile = identifier
			perceptrons = trainPerceptrons(numbers, trainingLabels, epochs, bias, learningRate, savedPerceptronFile, isWeightRand, False)
			savePerceptrons(perceptrons, savedPerceptronFile)
			# perceptrons = readPerceptrons(savedPerceptronFile)
			print("Training information")
			(confusionMatrix, correct) = testPerceptrons(holdOut, perceptrons)
			print(f"Correctly classified overall: {correct}%")
			if not best or correct > best:
				best = correct
				bestConfig = identifier
				bestStatic = [bias, learningRate]

	(bias, learningRate) = bestStatic
	# bias = 1
	# learningRate = penalizedLearningRate
	# best is going to be the best with isWeightRand false

	# Run the random algo like 100 times for randomizing the weight
	weightTotal = 0
	savedPerceptronFile = ""
	testRuns = 10
	for i in range(testRuns):
		perceptrons = trainPerceptrons(numbers, trainingLabels, epochs, bias, learningRate, savedPerceptronFile, True, False)
		weightTotal += testPerceptrons(holdOut, perceptrons)[1]
	print(f"Randomized Weight: Average is {weightTotal / testRuns} compared to static {best}")

	randTotal = 0
	for i in range(testRuns):
		perceptrons = trainPerceptrons(numbers, trainingLabels, epochs, bias, learningRate, savedPerceptronFile, False, False, True)
		randTotal += testPerceptrons(holdOut, perceptrons)[1]
	print(f"Randomized Data: Average is {randTotal / testRuns} compared to static {best}")
	retVal = [bias, weightTotal / testRuns > best, learningRate, randTotal / testRuns > best]
	return retVal

if __name__ == "__main__":
	dirPath = "../MP3/digitdata/"

	smallTrainingFileName = dirPath + "trainingimage2"
	trainingDataDir = dirPath + "trainingimages"
	trainingLabelsDir = dirPath + "traininglabels"

	testDataDir = dirPath + "testimages"
	testLabelsDir = dirPath + "testlabels"
	
	# Try randomizing the training data before passing it into training
	(trainingData, trainingLabels) = buildNumbers(trainingDataDir, trainingLabelsDir)
	(testData, g) = buildNumbers(testDataDir, testLabelsDir)
	# bias, randomized, learningRate, isWeightRand = findBestConfiguration(trainingData, trainingLabels, testData)
	# print(f"bias: {bias}, randomized data: {randomized}, learningRate: {learningRate.__name__}, weightRand: {isWeightRand}")
	bias = 1
	randomized = False
	learningRate = penalizedLearningRate
	isWeightRand = False
	epochs = 10 #10 # Identified by looking through table provided

	savedPerceptronFile = f"best.{epochs}.txt"
	if randomized:
		np.random.shuffle(trainingData)
	perceptrons = trainPerceptrons(trainingData, trainingLabels, epochs, bias, learningRate, savedPerceptronFile, isWeightRand, True, randomized)
	# savePerceptrons(perceptrons, savedPerceptronFile)
	# perceptrons = readPerceptrons(savedPerceptronFile)

	print("Best Testing information")
	testCM, testCorrect = testPerceptrons(testData, perceptrons)
	print(testCM)
	print(f"Correctly classified overall: {testCorrect}%")




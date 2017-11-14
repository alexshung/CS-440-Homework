import numpy as np
from collections import Counter, defaultdict
from math import log
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt


def convertToNums(x):
	return [0 if y == ' ' else 1 for y in x]
def readNumbers(fileName):
	with open(fileName) as f:
		content = [convertToNums(x.replace("\n", "")) for x in f.readlines()]
		return content

def basicReader(fileName):
	with open(fileName) as f:
		return [x for x in f.readlines()]

def readTestNumbers(fileName, reader = readNumbers):
	block = reader(fileName)
	testNumbers = list()
	lineNum = 0

	singleNum = list()
	for line in block:
		if lineNum % 28 == 0 and lineNum > 0:
			testNumbers.append(singleNum)
			singleNum = list()
		lineNum += 1
		singleNum.append(line)

	testNumbers.append(singleNum)

	return testNumbers

def readLabels(fileName):
	with open(fileName) as f:
		return [x.strip() for x in f.readlines()]

# Does the smoothing based on some value k
def initClassToFeatures(k):
	classToFeatures = {}
	for x in range(10):
		classToFeatures[str(x)] = [[k for x in range(28)] for y in range(28)]
	return classToFeatures

def buildClassToFeaturesMap(classToFeatures, inputNumbers, labels):
	lineCounter = 0
	number = list()
	for x in inputNumbers:
		if lineCounter % 28 == 0 and lineCounter > 0:
			labelIndex = int(lineCounter / 28) - 1
			label = labels[labelIndex]
			if label in classToFeatures:
				classToFeatures[label] = classToFeatures[label] + np.matrix(number)
			else:
				classToFeatures[label] = np.matrix(number)
			number = list()
		lineCounter += 1
		number.append(x)

	labelIndex = int(lineCounter / 28) - 1
	label = labels[labelIndex]
	if label in classToFeatures:
		classToFeatures[label] = classToFeatures[label] + np.matrix(number)
	else:
		classToFeatures[label] = np.matrix(number)

# Deals with the trianing data and building the prior probability
def training(imageFilePath, labelFilePath, smoothingConstant):
	labels = readLabels(labelFilePath)
	classCounter = Counter(labels)
	inputNumbers = readNumbers(imageFilePath)
	classPriors = {}

	# Build the class priors
	numPoints = len(labels)
	for key in classCounter.keys():
		classPriors[key] = classCounter[key] / numPoints

	# Build the inverse probability
	# TODO: Experiment with different values of k (say, from 0.1 to 10) and find the one that gives the highest classification accuracy.
	classToFeatures = initClassToFeatures(smoothingConstant)
	buildClassToFeaturesMap(classToFeatures, inputNumbers, labels)

	# Normalize based on the number of samples
	# + 2 for the smoothing
	for key in classToFeatures:
		classToFeatures[key] = classToFeatures[key] / (classCounter[key] + 2)

	return (classToFeatures, classPriors)

def testing(imageFilePath, classToFeatures, classPriors):
	result = list()

	testNumbers = readTestNumbers(imageFilePath)

	bestWorstClassTracker = {}
	indexNum = 0
	for number in testNumbers:
		bestClass = None
		bestClassProb = None

		for clazz in range(10):
			key = str(clazz)
			classResultForNumber = log(classPriors[key])
			for x in range(len(number)):
				for y in range(len(number[x])):
					probOfOne = classToFeatures[key].item((x, y))
					classResultForNumber += log(probOfOne) if number[x][y] == 1 else log(1 - probOfOne)
			
			if not bestClassProb or classResultForNumber > bestClassProb:
				bestClass = clazz
				bestClassProb = classResultForNumber
		if bestClass in bestWorstClassTracker:
			(tBestProb, best, tWorstProb, worst) = bestWorstClassTracker[bestClass]
			
			# Check to see if better class
			if tBestProb < bestClassProb:
				tBestProb = bestClassProb
				best = indexNum
			# Check to see if worse class
			if tWorstProb > bestClassProb:
				tWorstProb = bestClassProb
				worst = indexNum

			bestWorstClassTracker[bestClass] = (tBestProb, best, tWorstProb, worst)
		else:
			bestWorstClassTracker[bestClass] = (bestClassProb, indexNum, bestClassProb, indexNum)

		indexNum += 1
		result.append(bestClass)
	return (result, bestWorstClassTracker)

def evaluation(results, testLabelFilePath):
	testLabels = [int(x) for x in readLabels(testLabelFilePath)]
	confusionMatrix = confusion_matrix(testLabels, results, labels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

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
	print(confusionMatrix)
	return (confusionMatrix, correctHeur)

def printBestWorstForClass(imageFilePath, bestWorstClassTracker):
	numbers = readTestNumbers(imageFilePath, basicReader)
	for key in bestWorstClassTracker:
		(z, best, d, worst) = bestWorstClassTracker[key]
		print(f"For Class {key}")
		print(f"Best")
		for line in numbers[best]:
			print(''.join(str(line)))

		print(f"Worst")
		for line in numbers[worst]:
			print(''.join(str(line)))

def findBestSmoothingConstant(imageFilePath, labelFilePath):
	bestHeur = None
	bestK = None
	for k in np.arange(0.1, 2.0, 0.2):
		(classToFeatures, classPriors) = training(imageFilePath, labelFilePath, k)

		# Figure out best constant on test result. Should technically be a hold out set instead, but oh well
		(testResults, bestWorstClassTracker) = testing(imageFilePath, classToFeatures, classPriors)

		(c_matrix, correctHeur) = evaluation(testResults, labelFilePath)
		print(f"{k}: correct {correctHeur}")
		if not bestK or bestHeur < correctHeur:
			bestK = k
			bestHeur = correctHeur

	return bestK

def oddsRatioMaker(classToFeatures):
	# Makes ratio for 4 most incorrectly classified pairs
	# 7 as 9: 14 times
	# 4 as 9: 18 times
	# 8 as 3: 14 times
	# 5 as 3: 12 times
	pairs = [(7, 9), (4, 9), (8, 3), (5, 3)]
	i = 1
	for pair in pairs:
		x = str(pair[0])
		y = str(pair[1])
		
		fig = plt.figure(i)
		i += 1

		mx = np.log(classToFeatures[x])
		my = np.log(classToFeatures[y])
		oddsRatio = mx - my

		figx = fig.add_subplot(1, 3, 1)
		figx.imshow(mx, aspect='auto', cmap = 'RdYlBu', interpolation='nearest')
		figx.set_title(f"{x}")

		figy = fig.add_subplot(1, 3, 2)
		figy.imshow(my, aspect='auto', cmap = 'RdYlBu', interpolation='nearest')
		figy.set_title(f"{y}")
		
		figxy = fig.add_subplot(1, 3, 3)
		img = figxy.imshow(oddsRatio, aspect='auto', cmap = 'RdYlBu', interpolation='nearest')
		figxy.set_title(f"{x} over {y}")

		fig.colorbar(img)
	plt.show()


if __name__ == "__main__":
	dirPath = "digitdata/"

	smallTrainingFileName = dirPath + "trainingimage2"
	fullTrainingFileName = dirPath + "trainingimages"
	labelFilePath = dirPath + "traininglabels"

	fullTestFileName = dirPath + "testimages"
	labelTestFilePath = dirPath + "testlabels"

	# bestK = findBestSmoothingConstant(fullTrainingFileName, labelFilePath) => discovered .1 is the best
	# print(bestK)

	(classToFeatures, classPriors) = training(fullTrainingFileName, labelFilePath, .1)

	(testResults, bestWorstClassTracker) = testing(fullTestFileName, classToFeatures, classPriors)

	(c_matrix, correctHeur) = evaluation(testResults, labelTestFilePath)

	# oddsRatioMaker(classToFeatures)
	# print(correctHeur)
	printBestWorstForClass(fullTestFileName, bestWorstClassTracker)


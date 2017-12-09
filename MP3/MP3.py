import numpy as np
from collections import Counter, defaultdict
from math import log
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt


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

def readTestNumbers(fileName, reader = readNumbers, rowLength = 28, skip = 0):
	block = reader(fileName)
	testNumbers = list()
	lineNum = 0

	singleNum = list()
	skipped = 0
	for line in block:
		if skipped <= 1:
			if lineNum % rowLength == 0 and lineNum > 0 and singleNum:
				testNumbers.append(singleNum)
				singleNum = list()
				skipped = skip
			# if skipped <= 1:
			if line:
				lineNum += 1
				singleNum.append(line)
		else:
			skipped -= 1

	testNumbers.append(singleNum)
	return testNumbers


def readLabels(fileName):
	with open(fileName) as f:
		return [x.strip() for x in f.readlines()]

# Does the smoothing based on some value k
def initClassToFeatures(k, classes, lengthDoc, widthDoc):
	classToFeatures = {}
	for x in classes:
		classToFeatures[str(x)] = [[k for x in range(widthDoc)] for y in range(lengthDoc)]
	return classToFeatures

def buildClassToFeaturesMap(classToFeatures, inputNumbers, labels, rowLength, skip):
	lineCounter = 0
	number = list()
	skipped = 0
	a = 0
	for x in inputNumbers:
		if skipped <= 1:
			if lineCounter % rowLength == 0 and lineCounter > 0 and number:
				labelIndex = int(lineCounter / rowLength) - 1
				label = labels[labelIndex]
				if label in classToFeatures:
					classToFeatures[label] = classToFeatures[label] + np.matrix(number)
				else:
					classToFeatures[label] = np.matrix(number)
				number = list()
				skipped = skip
			if skipped <= 1:
				number.append(x)
				lineCounter += 1
		else:
			skipped -= 1
		a += 1		

	labelIndex = int(lineCounter / rowLength) - 1
	label = labels[labelIndex]
	if label in classToFeatures and number:
		classToFeatures[label] = classToFeatures[label] + np.matrix(number)

# Deals with the trianing data and building the prior probability
def training(inputs, labels, smoothingConstant, lengthDoc, widthDoc, skip):
	classCounter = Counter(labels)
	classPriors = {}

	# Build the class priors
	numPoints = len(labels)
	for key in classCounter.keys():
		classPriors[key] = classCounter[key] / numPoints

	# Build the inverse probability
	classToFeatures = initClassToFeatures(smoothingConstant, classCounter.keys(), lengthDoc, widthDoc)
	buildClassToFeaturesMap(classToFeatures, inputs, labels, lengthDoc, skip)

	# Normalize based on the number of samples
	# + 2 for the smoothing
	for key in classToFeatures:
		classToFeatures[key] = classToFeatures[key] / (classCounter[key] + 2)

	return (classToFeatures, classPriors)

def testing(testNumbers, classToFeatures, classPriors):
	result = list()
	bestWorstClassTracker = {}
	indexNum = 0
	for number in testNumbers:
		bestClass = None
		bestClassProb = None

		for clazz in classToFeatures:
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

def findBestSmoothingConstant(inputNumbers, labels, testNumbers, docLength = 28, docWidth = 28, skip = 0):
	bestHeur = None
	bestK = None
	for k in np.arange(0.1, 2.0, 0.2):
		(classToFeatures, classPriors) = training(inputNumbers, labels, k, docLength, docWidth, skip)

		# Figure out best constant on test result. Should technically be a hold out set instead, but oh well
		(testResults, bestWorstClassTracker) = testing(testNumbers, classToFeatures, classPriors)

		(c_matrix, correctHeur) = evaluation(testResults, labels)
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

###############
### PART 2 ####
###############
def voiceReader(fileName):
	with open(fileName) as f:
		data = [convertSoundToNums(x.replace("\n", "")) for x in f.readlines()]
		return data

def buildVoiceInputData(noFileName, yesFileName):
	noData = voiceReader(noFileName)
	yesData = voiceReader(yesFileName)
	return (noData, yesData)

def buildVoiceTestData(noFileName, yesFileName):
	noData = readTestNumbers(noFileName, voiceReader, 25, 3)
	yesData = readTestNumbers(yesFileName, voiceReader, 25, 3)
	return (noData, yesData)

def runModel(inputs, labels, testInputs, testLabels, smoothingConstant, docLength = 28, docWidth = 28, skip = 0):
	(classToFeatures, classPriors) = training(inputs, labels, smoothingConstant, docLength, docWidth, skip)

	(testResults, bestWorstClassTracker) = testing(testInputs, classToFeatures, classPriors)

	(c_matrix, correctHeur) = evaluation(testResults, testLabels)

	return (classToFeatures, correctHeur, bestWorstClassTracker)

def runPart1():
	dirPath = "digitdata/"

	smallTrainingFileName = dirPath + "trainingimage2"
	fullTrainingFileName = dirPath + "trainingimages"
	labelFilePath = dirPath + "traininglabels"

	fullTestFileName = dirPath + "testimages"
	labelTestFilePath = dirPath + "testlabels"

	inputNumbers = readNumbers(fullTrainingFileName)
	labels = readLabels(labelFilePath)
	testNumbers = readTestNumbers(fullTestFileName)
	testLabels = readLabels(labelTestFilePath)

	# testInputNumbers = readTestNumbers(fullTrainingFileName)
	# bestK = findBestSmoothingConstant(inputNumbers, labels, testInputNumbers) # => discovered .1 is the best
	# print(bestK)

	(classToFeatures, correctHeur, bestWorstClassTracker) = runModel(inputNumbers, labels, testNumbers, testLabels, 0.1)

	# oddsRatioMaker(classToFeatures)
	print(correctHeur/len(testNumbers))
	# printBestWorstForClass(fullTestFileName, bestWorstClassTracker)

def runPart2():
	dirPath = "yesno/"
	trainingNoDataPath = dirPath + "no_train.txt"
	trainingYesDataPath = dirPath + "yes_train.txt"

	testNoDataPath = dirPath + "no_test.txt"
	testYesDataPath = dirPath + "yes_test.txt"

	(noData, yesData) = buildVoiceInputData(trainingNoDataPath, trainingYesDataPath)
	
	trainingNoLabel = ["no" for x in range(int(len(noData) / 28))] # These are input files of length 28 for some reason
	trainingYesLabel = ["yes" for x in range(int(len(yesData) / 28))]
	
	(noTestData, yesTestData) = buildVoiceTestData(testNoDataPath, testYesDataPath)

	testNoLabel = ["no" for x in range(len(noTestData))]
	testYesLabel = ["yes" for x in range(len(yesTestData))]

	totalTrainingData = noData + yesData
	totalTrainingLabel = trainingNoLabel + trainingYesLabel
	totalTestData = noTestData + yesTestData
	totalTestLabel = testNoLabel + testYesLabel

	(noTrainTestData, yesTrainTestData) = buildVoiceTestData(trainingNoDataPath, trainingYesDataPath)
	testTrainingData = noTrainTestData + yesTrainTestData
	# bestK = findBestSmoothingConstant(totalTrainingData, totalTrainingLabel, testTrainingData) # => discovered .1 is the best
	# print(bestK)
	runModel(totalTrainingData, totalTrainingLabel, totalTestData, totalTestLabel, 1, 25, 10, 3)

if __name__ == "__main__":
###############
#### PART 1 ###
###############
	runPart1()

###############
#### PART 2 ###
###############
#	runPart2()
	



	




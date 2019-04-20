#!/usr/bin/env python3

class Episode(object):

	def __init__(self, name, partOne, partTwo):
		self.name = name
		self.partOne = partOne
		self.partTwo = partTwo
		self.played = False

	def setPlayed(self, played):
		self.played = played

	def isPartTwo(self):
		return self.partTwo

	def isPartOne(self):
		return self.partOne

	def __str__(self):
		return "{name: '" + str(self.name) + "', partOne: " + str(self.partOne) + ", partTwo: " + str(self.partTwo) + ", played: " + str(self.played) + "}"

	def __repr__(self):
		return self.__str__()

	def isPlayed(self):
		return self.played

	def getName(self):
		return self.name

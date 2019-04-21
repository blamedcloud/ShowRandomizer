#!/usr/bin/env python3
import os
import random
from episode import Episode
from history import ShowHistory, episodeStr2IntPair

def getSeasonDirFromNum(seasonNum):
	return "Season " + str(seasonNum)

class Season(object):

	def __init__(self, showDir, seasonNum, weight, partOneEp = -1):
		self.seasonNum = seasonNum
		self.weight = weight
		self.seasonDir = getSeasonDirFromNum(self.seasonNum)
		self.seasonPath = os.path.join(showDir, self.seasonDir)
		self.episodes = {}

		episodeNames = os.listdir(self.seasonPath)
		for episode in episodeNames:
			if episode != 'Thumbs.db':
				seasonEpisodeStr = self.seasonDir + ', ' + episode
				seasonEpisodePair = episodeStr2IntPair(seasonEpisodeStr)
				epNum = seasonEpisodePair[1]
				self.episodes[epNum] = Episode(episode, epNum == partOneEp, epNum == (partOneEp+1))

	def setPlayed(self, history, reset = False):
		assert isinstance(history, ShowHistory)
		if reset:
			self.resetPlayed()
		for pair in history:
			if pair[0] == self.seasonNum:
				self.episodes[pair[1]].setPlayed(True)

	def resetPlayed(self):
		for num, ep in self.episodes.items():
			ep.setPlayed(False)

	def getSeasonNum(self):
		return self.seasonNum

	def __str__(self):
		return "seasonNum=" + str(self.seasonNum) + "; weight=" + str(self.weight) + "; " + str(self.episodes)

	def __repr__(self):
		return self.__str__()

	def hasNonPlayedEpisode(self):
		for num, ep in self.episodes.items():
			if not ep.isPlayed():
				return True
		return False

	def hasValidEpisode(self):
		for num, ep in self.episodes.items():
			if (not ep.isPlayed()) and (not ep.isPartTwo()):
				return True
		return False

	def countValidEpisodes(self, countPlayed = False):
		valid = 0
		for num, ep in self.episodes.items():
			if countPlayed:
				if not ep.isPartTwo():
					valid += 1
			else:
				if not ep.isPlayed() and not ep.isPartTwo():
					valid += 1
		return valid

	def getValidEpisodeNums(self, countPlayed = False):
		valid = []
		for num, ep in self.episodes.items():
			if countPlayed:
				if not ep.isPartTwo():
					valid.append(num)
			else:
				if not ep.isPlayed() and not ep.isPartTwo():
					valid.append(num)
		return valid

	def getFirstEpisodeInfo(self):
		smallest = min(self.episodes.keys())
		return self.getEpisodeInfo(smallest)

	def getEpisodeObj(self, epNum):
		return self.episodes[epNum]

	def getEpisodeInfo(self, epNum):
		epName = self.episodes[epNum].getName()
		episodePath = os.path.join(self.seasonPath, epName)
		seasonEpisodeStr = self.seasonDir + ', ' + epName
		return (episodePath, seasonEpisodeStr)

	def getRandomValidEpisodeInfo(self):
		validEpNums = self.getValidEpisodeNums()
		assert len(validEpNums) > 0
		epNum = random.choice(validEpNums)
		return self.getEpisodeInfo(epNum)

	def getEffectiveWeight(self):
		if self.hasValidEpisode():
			return self.weight
		else:
			return 0

	def hasEpisodeByNum(self, num):
		return num in self.episodes

	def __len__(self):
		return len(self.episodes)


#!/usr/bin/env python3
import os
import random
import subprocess
from season import Season
from history import ShowHistory

class Show(object):

	def __init__(self, showDir):
		self.seasons = {}
		self.dir = showDir
		self.history = None
		self.episodeCount = 0
		self._newSeason = False

	def __len__(self):
		return len(self.seasons)

	def addSeason(self, seasonNum, weight, partOneEp = -1):
		assert isinstance(weight, int)
		if weight < 1:
			print("WARNING: weights must be integers 1 or larger, setting to 1!")
			weight = 1
		self.seasons[seasonNum] = Season(self.dir, seasonNum, weight, partOneEp)
		self._newSeason = True

	def setPlayHistory(self, history):
		assert isinstance(history, ShowHistory)
		if history.getRecentNum() >= self.getEpisodeCount():
			# if there are no duplicates in the history,
			# then you've played every episode.
			# So, remove the oldest one from the history.
			print("WARNING: History too long, setting smaller recentNum!")
			history.changeRecentNum(self.getEpisodeCount()-1)
			print("History recentNum set to: " + str(history.getRecentNum()))
		self.history = history
		self._updatePlayed()

	def getHistory(self):
		return self.history

	def __str__(self):
		return "dir: " + str(self.dir) + "; Seasons: " + str(self.seasons)

	def __repr__(self):
		return self.__str__()

	def _updatePlayed(self):
		for num, season in self.seasons.items():
			season.setPlayed(self.history, True)

	def _countEpisodes(self):
		total = 0
		for seasonNum in self.seasons:
			total += len(self.seasons[seasonNum])
		self.episodeCount = total

	def getEpisodeCount(self):
		if self.episodeCount == 0 or self._newSeason:
			self._countEpisodes()
			self._newSeason = False
		return self.episodeCount

	def getRandomSeason(self):
		choices = []
		for num, season in self.seasons.items():
			choices += [num]*season.getEffectiveWeight()
		if len(choices) == 0:
			print("There are no valid seasons, maybe use less history?")
			raise ValueError
		return random.choice(choices)

	def getFirstSeason(self):
		smallest = min(self.seasons.keys())
		return self.seasons[smallest]

	def getRandomEpisodeInfo(self):
		seasonNum = self.getRandomSeason()
		return self.seasons[seasonNum].getRandomValidEpisodeInfo()

	def playRandomEpisode(self, vlcExe, printEp = False):
		epInfo = self.getRandomEpisodeInfo()
		self.playEpisode(vlcExe, epInfo, printEp)

	def playRandomOrPartTwo(self, vlcExe, printEp = False):
		assert self.history is not None
		playNext = False
		if len(self.history) > 0:
			mostRecent = self.history.getMostRecent()
			seasonNum = mostRecent[0]
			episodeNum = mostRecent[1]
			if self.seasons[seasonNum].getEpisodeObj(episodeNum).isPartOne():
				playNext = True
		if playNext:
			self.playNextEpisode(vlcExe, printEp)
		else:
			self.playRandomEpisode(vlcExe, printEp)

	def playEpisode(self, vlcExe, epInfo, printEp = False):
		episodePath = epInfo[0]
		seasonEpisodeStr = epInfo[1]
		if printEp:
			print(seasonEpisodeStr)
		if self.history is not None:
			self.history.recordEpisode(seasonEpisodeStr)
			self.history.update()
			self._updatePlayed()
		subprocess.run([vlcExe, episodePath, "--fullscreen"])

	def playNextEpisode(self, vlcExe, printEp = False):
		assert self.history is not None
		if len(self.history) > 0:
			mostRecent = self.history.getMostRecent()
			seasonNum = mostRecent[0]
			episodeNum = mostRecent[1]
			thisSeason = self.seasons[seasonNum]
			epInfo = None
			if thisSeason.hasEpisodeByNum(episodeNum+1):
				epInfo = thisSeason.getEpisodeInfo(episodeNum+1)
			else:
				if (seasonNum+1) in self.seasons:
					nextSeason = self.seasons[seasonNum+1]
					epInfo = nextSeason.getFirstEpisodeInfo()
				else:
					epInfo = self.getFirstSeason().getFirstEpisodeInfo()
		else:
			epInfo = self.getFirstSeason().getFirstEpisodeInfo()
		self.playEpisode(vlcExe, epInfo, printEp)



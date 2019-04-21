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

	def __len__(self):
		return len(self.seasons)

	def addSeason(self, seasonNum, weight, partOneEp = -1):
		self.seasons[seasonNum] = Season(self.dir, seasonNum, weight, partOneEp)

	def setPlayHistory(self, history):
		assert isinstance(history, ShowHistory)
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

	def getRandomSeason(self):
		choices = []
		for num, season in self.seasons.items():
			choices += [num]*season.getEffectiveWeight()
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



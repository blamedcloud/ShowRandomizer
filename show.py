import os
import random
import subprocess

def episodeStr2IntPair(seasonEpisodeStr):
	commaSep = seasonEpisodeStr.split(',')
	seasonStr = commaSep[0].strip(' ')
	episodeStr = commaSep[1].strip(' ')
	seasonNum = int(seasonStr.split(' ')[1])
	episodeNum = int(episodeStr.split(' ')[0])
	return (seasonNum, episodeNum)

def getSeasonDirFromNum(seasonNum):
	return "Season " + str(seasonNum)
	
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
		
	def getValidEpisodeNums(self):
		valid = []
		for num, ep in self.episodes.items():
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
		mostRecent = self.history.getMostRecent()
		print(mostRecent)
		seasonNum = mostRecent[0]
		episodeNum = mostRecent[1]
		if self.seasons[seasonNum].getEpisodeObj(episodeNum).isPartOne():
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
		self.playEpisode(vlcExe, epInfo, printEp)


class ShowHistory(object):

	def __init__(self, historyFile, recentNum):
		self.recentNum = recentNum
		self.historyFile = historyFile
		self.recentlyWatched = []
		self.update()
		
	def update(self):
		history = []
		with open(self.historyFile, 'r') as FILE:
			for line in FILE:
				history.append(line)
		self.recentlyWatched = [episodeStr2IntPair(ep) for ep in history[-1 * self.recentNum:]]
	
	def getMostRecent(self):
		return self.recentlyWatched[-1]
	
	def __str__(self):
		return str(self.recentlyWatched)
	
	def changeRecentNum(self, newRecentNum):
		self.recentNum = newRecentNum
		self.update()
	
	def __iter__(self):
		return iter(self.recentlyWatched)
	
	def recordEpisode(self, seasonEpisodeStr):
		with open(self.historyFile, 'a') as FILE:
			FILE.write(seasonEpisodeStr + '\n')


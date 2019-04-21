#!/usr/bin/env python3

def episodeStr2IntPair(seasonEpisodeStr):
	commaSep = seasonEpisodeStr.split(',')
	seasonStr = commaSep[0].strip(' ')
	episodeStr = commaSep[1].strip(' ')
	seasonNum = int(seasonStr.split(' ')[1])
	episodeNum = int(episodeStr.split(' ')[0])
	return (seasonNum, episodeNum)

class ShowHistory(object):

	def __init__(self, historyFile, recentNum):
		self.recentNum = recentNum
		self.historyFile = historyFile
		self.recentlyWatched = []
		self.update()

	def update(self):
		history = []
		self.recentlyWatched = []
		with open(self.historyFile, 'r') as FILE:
			for line in FILE:
				history.append(line)
		if len(history) > 0:
			if self.recentNum > 0:
				self.recentlyWatched = [episodeStr2IntPair(ep) for ep in history[-1 * self.recentNum:]]
			elif self.recentNum == -1:
				self.recentlyWatched = [episodeStr2IntPair(ep) for ep in history]

	def getMostRecent(self):
		return self.recentlyWatched[-1]

	def __len__(self):
		return len(self.recentlyWatched)

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



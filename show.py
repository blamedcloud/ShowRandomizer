#!/usr/bin/env python3
import os
import random
import subprocess
from season import Season
from history import ShowHistory

class Show(object):

    def __init__(self, showDir, vlcExe = None):
        self.seasons = {}
        self.dir = showDir
        self.history = None
        self.totalEpisodeCount = 0
        self.validEpisodeCount = 0
        self._newSeason = False
        self.vlcExe = vlcExe

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
        if history.getRecentNum() >= self.getValidEpisodeCount():
            # if there are no duplicates in the history,
            # then you've played every episode.
            # So, remove the oldest one from the history.
            print("WARNING: History too long, setting smaller recentNum!")
            history.changeRecentNum(self.getValidEpisodeCount()-1)
            print("History recentNum set to: " + str(history.getRecentNum()))
        self.history = history
        self._updatePlayed()

    def getHistory(self):
        return self.history

    def setVlcExe(self, vlcExe):
        if vlcExe is not None:
            self.vlcExe = vlcExe

    def hasVlcExe(self):
        return self.vlcExe is not None

    def hasSeasonByNum(self, seasonNum):
        return seasonNum in self.seasons

    def __str__(self):
        return "dir: " + str(self.dir) + "; Seasons: " + str(self.seasons)

    def __repr__(self):
        return self.__str__()

    def _updatePlayed(self):
        for num, season in self.seasons.items():
            season.setPlayed(self.history, True)

    def _countEpisodes(self):
        total = 0
        valid = 0
        for seasonNum in self.seasons:
            total += len(self.seasons[seasonNum])
            valid += self.seasons[seasonNum].countValidEpisodes(True)
        self.totalEpisodeCount = total
        self.validEpisodeCount = valid
        self._newSeason = False

    def getTotalEpisodeCount(self):
        if self.totalEpisodeCount <= 0 or self._newSeason:
            self._countEpisodes()
        return self.totalEpisodeCount

    def getValidEpisodeCount(self):
        if self.validEpisodeCount <= 0 or self._newSeason:
            self._countEpisodes()
        return self.validEpisodeCount

    def setSeasonsWeightingSimple(self, isSimple):
        for num, season in self.seasons.items():
            season.setWeightingSimple(isSimple)

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

    def playRandomEpisode(self, printEp = False, vlcExe = None):
        self.setVlcExe(vlcExe)
        epInfo = self.getRandomEpisodeInfo()
        self._playEpisode(epInfo, printEp)

    def playRandomOrPartTwo(self, printEp = False, vlcExe = None):
        self.setVlcExe(vlcExe)
        playNext = False
        if self.history is not None and len(self.history) > 0:
            mostRecent = self.history.getMostRecent()
            seasonNum = mostRecent[0]
            episodeNum = mostRecent[1]
            if self.seasons[seasonNum].getEpisodeObj(episodeNum).isPartOne():
                playNext = True
        if playNext:
            self.playNextEpisode(printEp)
        else:
            self.playRandomEpisode(printEp)

    def playNextEpisode(self, printEp = False, vlcExe = None):
        self.setVlcExe(vlcExe)
        epInfo = None
        if self.history is not None and len(self.history) > 0:
            mostRecent = self.history.getMostRecent()
            seasonNum = mostRecent[0]
            episodeNum = mostRecent[1]
            thisSeason = self.seasons[seasonNum]
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
        self._playEpisode(epInfo, printEp)

    def replayLastEpisode(self, printEp = False, vlcExe = None):
        self.setVlcExe(vlcExe)
        if self.history is not None and len(self.history) > 0:
            mostRecent = self.history.getMostRecent()
            seasonNum = mostRecent[0]
            episodeNum = mostRecent[1]
            self.playEpisode(seasonNum, episodeNum, printEp)
        else:
            epInfo = self.getFirstSeason().getFirstEpisodeInfo()
            self._playEpisode(epInfo, printEp)

    def playEpisode(self, seasonNum, epNum, printEp = False, vlcExe = None):
        assert self.hasSeasonByNum(seasonNum)
        assert self.seasons[seasonNum].hasEpisodeByNum(epNum)
        self.setVlcExe(vlcExe)
        epInfo = self.seasons[seasonNum].getEpisodeInfo(epNum)
        self._playEpisode(epInfo, printEp)

    def _playEpisode(self, epInfo, printEp = False, vlcExe = None):
        self.setVlcExe(vlcExe)
        episodePath = epInfo[0]
        seasonEpisodeStr = epInfo[1]
        if printEp:
            print(seasonEpisodeStr)
        if self.history is not None:
            self.history.recordEpisode(seasonEpisodeStr)
            self.history.update()
            self._updatePlayed()
        subprocess.run([self.vlcExe, episodePath, "--fullscreen"])



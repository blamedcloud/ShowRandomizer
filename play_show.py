#!/usr/bin/env python3
from timed_input import user_input
from show import Show
import re

DEFAULT_TIMEOUT = 5

# returns true if the user typed anything (and pressed enter) before the timeout
def quit(timeout = DEFAULT_TIMEOUT):
    answer = user_input("Press enter to stop playback:", timeout)
    return answer is not None

# input_args is meant to be sys.argv from a command-line
# so we never care about the first entry
#
# in order to use this, show must have a valid vlcExe
# either passed in the constructor or in show.setVlcExe
#
# also, you'll want your vlc to exit after playing the
# episode. See vlc_setup.txt for more info.
def play(show, input_args, showEpisode = False, timeout = DEFAULT_TIMEOUT):
    assert isinstance(show, Show)
    assert show.hasVlcExe()
    args = input_args[1:]

    continueRE = re.compile('--?c(ont|ontinue)?', re.IGNORECASE)
    nextRE = re.compile('--?n(ext)?', re.IGNORECASE)
    replayRE = re.compile('--?r(eplay)?', re.IGNORECASE)
    sequentialRE = re.compile('--?s(eq|equential)?', re.IGNORECASE)

    continuePlaying = False
    for arg in args:
        if continueRE.fullmatch(arg):
            continuePlaying = True
            args.remove(arg)
            break

    firstPlay = None
    loopPlay = None

    # firstPlay and loopPlay usually don't have to be lambda's
    # but I kept it that way to drive home that they are always
    # a function that takes one bool as an argument
    if len(args) == 1:
        if nextRE.fullmatch(args[0]):
            firstPlay = lambda printEp: show.playNextEpisode(printEp)
            loopPlay = lambda printEp: show.playNextEpisode(printEp)
        elif replayRE.fullmatch(args[0]):
            firstPlay = lambda printEp: show.replayLastEpisode(printEp)
            loopPlay = lambda printEp: show.playNextEpisode(printEp)
        elif sequentialRE.fullmatch(args[0]):
            firstPlay = lambda printEp: show.playRandomOrPartTwo(printEp)
            loopPlay = lambda printEp: show.playNextEpisode(printEp)
    elif len(args) == 2:
        try:
            seasonNum = int(args[0])
            epNum = int(args[1])
            firstPlay = lambda printEp: show.playEpisode(seasonNum, epNum, printEp)
            loopPlay = lambda printEp: show.playNextEpisode(printEp)
        except ValueError:
            print("Expected (seasonNumber, episodeNumber) as the two arguments")
    elif len(args) == 0:
        firstPlay = lambda printEp: show.playRandomOrPartTwo(printEp)
        loopPlay = lambda printEp: show.playRandomOrPartTwo(printEp)

    if firstPlay is None or loopPlay is None:
        print("Invalid arguments")
    else:
        firstPlay(showEpisode)
        while continuePlaying:
            if quit(timeout):
                break
            loopPlay(showEpisode)


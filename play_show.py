#!/usr/bin/env python3
from timed_input import user_input
from show import Show
import re

DEFAULT_TIMEOUT = 5

# returns true if the user typed anything (and pressed enter) before the timeout
def quit(timeout = DEFAULT_TIMEOUT):
    answer = user_input("Press enter to stop playback:", timeout)
    if answer is not None:
        return True
    else:
        return False

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
    args = input_args[1:]

    continueRE = re.compile('--?c(ont|ontinue)?', re.IGNORECASE)
    nextRE = re.compile('--?n(ext)?', re.IGNORECASE)

    continuePlaying = False
    for arg in args:
        if continueRE.fullmatch(arg):
            continuePlaying = True
            args.remove(arg)
            break

    firstPlay = None
    loopPlay = None

    if len(args) == 1:
        if nextRE.fullmatch(args[0]):
            firstPlay = lambda x: show.playNextEpisode(x)
            loopPlay = lambda x: show.playNextEpisode(x)
    elif len(args) == 2:
        try:
            seasonNum = int(args[0])
            epNum = int(args[1])
            firstPlay = lambda x: show.playEpisode(seasonNum, epNum, x)
            loopPlay = lambda x: show.playNextEpisode(x)
        except ValueError:
            print("Expected (seasonNumber, episodeNumber) as the two arguments")
    elif len(args) == 0:
        firstPlay = lambda x: show.playRandomOrPartTwo(x)
        loopPlay = lambda x: show.playRandomOrPartTwo(x)

    if firstPlay is None or loopPlay is None:
        print("Invalid arguments")
    else:
        firstPlay(showEpisode)
        while continuePlaying:
            if quit(timeout):
                break
            loopPlay(showEpisode)

#!/usr/bin/env python3

def user_input_unix(prompt = "type something in time:", timeout = 5):

    def interrupted(signum, frame):
        raise RuntimeError
    signal.signal(signal.SIGALRM, interrupted)

    def my_input():
        try:
            print(prompt)
            answer = input()
            return answer
        except:
            return None

    signal.alarm(timeout)
    answer = my_input()
    signal.alarm(0)
    return answer

def user_input_win(prompt = "type something in time:", timeout = 5):
    INTERVAL = 0.05

    SP = ' '
    CR = '\r'
    LF = '\n'
    CRLF = CR + LF

    class TimeoutOccurred(Exception):
        pass

    def echo(string):
        sys.stdout.write(string)
        sys.stdout.flush()

    def win_input_timeout(prompt, timeout):
        echo(prompt)
        begin = time.monotonic()
        end = begin  + timeout
        line = ''

        while time.monotonic() < end:
            if msvcrt.kbhit():
                c = msvcrt.getwche()
                if c in (CR, LF):
                    echo(CRLF)
                    return line
                if c == '\003':
                    raise KeyboardInterrupt
                if c == '\b':
                    line = line[:-1]
                    cover = SP * len(prompt + line + SP)
                    echo(''.join([CR,cover,CR,prompt,line]))
                else:
                    line += c
            time.sleep(INTERVAL)

        echo(CRLF)
        raise TimeoutOccurred

    # main:
    answer = None
    try:
        answer = win_input_timeout(prompt, timeout)
    except TimeoutOccurred:
        pass
    return answer

try:
    import msvcrt

except ImportError:
    import signal

    user_input = user_input_unix

else:
    import sys
    import time

    user_input = user_input_win


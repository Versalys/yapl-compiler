class _Getch:
    """
    From github: https://stackoverflow.com/questions/510357/how-to-read-a-single-character-from-the-user
    Gets a single character from standard input.  Does not echo to the screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios

        try:  # If this isn't a "real" file, just read the first byte
            fd = sys.stdin.fileno()
        except:
            ch = sys.stdin.read(1)
            return ch
        
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        try:  # If this isn't a "real" file, just read the first byte
            fd = sys.stdin.fileno()
        except:
            ch = sys.stdin.read(1)
            return ch

        import msvcrt
        return msvcrt.getch()


getch = _Getch()

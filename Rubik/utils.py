import time

def get_char():
    # figure out which function to use once, and store it in _func
    if "_func" not in get_char.__dict__:
        try:
            # for Windows-based systems
            import msvcrt # If successful, we are on Windows
            print("On Windows hit enter after every key")
            # getch doesn't work in IDEs, if on the cmd line can use msvcrt.getch
            get_char._func = input

        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty, sys, termios # raises ImportError if unsupported

            def _ttyRead():
                fd = sys.stdin.fileno()
                oldSettings = termios.tcgetattr(fd)

                try:
                    tty.setraw(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

                return answer

            get_char._func = _ttyRead

    return get_char._func()


def curr_time_s():
    return time.time()


# whether the buttons or keyboard should be used as input
def use_buttons():
    return True


def in_test():
    return False

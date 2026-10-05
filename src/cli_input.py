import sys
import getpass

def getpass_asterisk(prompt="  API key: "):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    try:
        import msvcrt
    except ImportError:
        return getpass.getpass("")

    pw = ""
    while True:
        char = msvcrt.getch()
        if char in (b'\r', b'\n'):
            sys.stdout.write('\n')
            break
        elif char == b'\x08': # Backspace
            if len(pw) > 0:
                pw = pw[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif char == b'\x03': # Ctrl+C
            raise KeyboardInterrupt
        elif char in (b'\x00', b'\xe0'):
            msvcrt.getch() # discard
        else:
            try:
                char_decoded = char.decode('utf-8')
                if char_decoded.isprintable():
                    pw += char_decoded
                    sys.stdout.write('*')
                    sys.stdout.flush()
            except UnicodeDecodeError:
                pass
    return pw

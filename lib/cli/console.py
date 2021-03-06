#!/usr/bin/python3

# pylint: disable=broad-except, invalid-name

"""
Handles console related stuff
"""

import os
import re
import sys
import time
import traceback
from ipaddress import ip_address

from prompt_toolkit import ANSI
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import prompt

from . import colors


def print_banner(ver, exp_cnt):
    """
    print banner along with some info
    """
    banner = colors.CYAN + colors.BOLD + r'''
 ███▄ ▄███▓▓█████  ▄████▄
▓██▒▀█▀ ██▒▓█   ▀ ▒██▀ ▀█
▓██    ▓██░▒███   ▒▓█    ▄
▒██    ▒██ ▒▓█  ▄ ▒▓▓▄ ▄██▒
▒██▒   ░██▒░▒████▒▒ ▓███▀ ░
░ ▒░   ░  ░░░ ▒░ ░░ ░▒ ▒  ░
░  ░      ░ ░ ░  ░  ░  ▒
░      ░      ░   ░
       ░      ░  ░░ ░
                  ░
'''+f'''

    version: {ver}

    {exp_cnt} exploits
''' + colors.END + colors.GREEN + f'''

    by jm33_m0
    https://github.com/jm33-m0/mec
    type h or help for help\n''' + colors.END

    print(banner)


# util functions

def print_status(msg, proc):
    '''
    print animated status info,
    until proc exits
    '''
    msg += '\r'
    msg_list = list(msg)

    def loop():
        print(colors.CYAN + msg + colors.END, end='')
        i = 0

        for c in msg:
            sys.stdout.flush()
            msg_list[i] = c.upper()
            sys.stdout.write(colors.CYAN+''.join(msg_list)+colors.END)

            if re.match(r"[a-z]", c):
                time.sleep(.3)
            msg_list[i] = c
            sys.stdout.write(colors.CYAN+''.join(msg_list)+colors.END)
            i += 1

    try:
        while True:
            if not proc.is_alive():
                break
            loop()
    except KeyboardInterrupt:
        return
    except BaseException:
        pass
    finally:
        sys.stdout.flush()
        print()


def print_error(msg):
    '''
    print error msg in red
    '''
    print(colors.END)
    print(colors.RED + msg + colors.END)


def print_warning(msg):
    '''
    print warning msg in yellow
    '''
    print(colors.END)
    print(colors.YELLOW, msg, colors.END)


def print_success(msg):
    '''
    print success msg in green
    '''
    print(colors.END)
    print(colors.GREEN + colors.BOLD, msg, colors.END)


def debug_except():
    '''
    display traceback info
    '''
    tcbk = traceback.format_exc()
    print_error("[-] Unhandled exception:\n"+tcbk)
    sys.exit(1)


def input_check(prompt_info, allow_blank=True,
                check_type=None, ip_check=False, choices=None):
    '''
    checks user input, always returns str
    check_type: checks type and return as str
    ip_check: check if input is ip
    '''
    # add some completions
    command_list = ["app:", "port:", "ip:", "cidr:", "country:", "city:",
                    "subdivisions:", "device:", "ver:",
                    "weblogic", "tomcat", "jenkins", "joomla", "jboss",
                    "exchange", "iis", "nginx", "apache"]
    command_list += os.listdir("./")
    choice_completer = WordCompleter(command_list)

    if choices is not None:
        choice_completer = WordCompleter(choices)

    while True:

        try:
            input_ps = ANSI(colors.BLUE + prompt_info + colors.END)
            user_input = prompt(
                message=input_ps,
                complete_in_thread=True,
                complete_while_typing=True,
                completer=choice_completer).strip().lower()

            if not allow_blank and user_input == '':
                continue

            if choices is not None:
                if user_input not in choices:
                    print_error("[-] Invalid input")

                    continue

                if check_type is None:
                    return user_input

                return str(check_type(user_input))

            if check_type is not None and choices is None:
                return str(check_type(user_input))

            if ip_check:
                try:
                    ip_address(user_input)
                except ValueError:
                    print_error("[-] Not an IP address")

                    continue

            return user_input

        except (EOFError, KeyboardInterrupt, SystemExit):
            continue

        # pylint: disable=broad-except
        except BaseException as err:
            print_error(f"[-] Error: {err}")

            break


def yes_no(quest):
    '''
    ask a yes_no question
    '''

    res = input_check(prompt_info=quest+" (y/N) ",
                      choices=["y", "n", ""])

    if res == "y":
        return True

    return False


def tail(filepath):
    '''
    tail -f to peek the stdout of your exploit
    '''
    last_lines = ""

    try:
        filed = open(filepath)
        last_lines = ''.join(filed.readlines()[-20:])
        filed.close()
    except IndexError:
        pass
    except BaseException:
        debug_except()

    return last_lines

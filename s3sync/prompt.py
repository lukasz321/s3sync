import sys
from termios import tcflush, TCIFLUSH
from typing import List

RED = "\033[91m\033[1m"
CYAN = "\033[96m\033[1m"
GRAY = "\033[0m\033[1m"
ENDC = "\033[0m\033[0m"


class Prompt:
    """
    Class helping user interact with termianl.
    Ask for input, ask for acknowledgement, prompt yes or no, etc.

    Heavily influenced by click module.
    See __main__ at the bottom of this file for examples.
    """

    @staticmethod
    def choose(prompt: str, options: List) -> str:
        """
        Ask user for input. Input is limited to the options provided
        in the list (`options` argument). User must choose one of the options.

        Note that options are case sensitive.
        """

        if prompt[-1:] not in [":", "?", "."]:
            prompt = prompt + ":"

        while True:
            print(CYAN + prompt + ENDC)
            print(f"Valid options are: {options}")
            user_input = input(">> ")

            if not user_input:
                continue

            if user_input.lower() in [o.lower() for o in options]:
                return user_input

            print(f'"{user_input}" is not a valid option!')

    @staticmethod
    def confirm(prompt: str):
        """
        Prompt user to hit ENTER.
        """

        if prompt[-1:] not in [":", "?", "."]:
            prompt = prompt + ":"

        tcflush(sys.stdin, TCIFLUSH)
        print(CYAN + prompt + ENDC)
        input(f">> [ENTER] ")

    @staticmethod
    def acknowledge(prompt: str):
        Prompt.confirm(prompt)

    @staticmethod
    def input(prompt: str, flush: bool = False) -> str:
        """
        Ask user for input. Note that no input is accepted, so return may be "".
        """

        if flush:
            tcflush(sys.stdin, TCIFLUSH)

        print(CYAN + prompt + ENDC)
        user_input = input(">> ")
        return user_input

    @staticmethod
    def yes_no(prompt: str) -> bool:
        """
        Ask operator to choose "y" or "n" to prompt.
        """

        if prompt.endswith(":") or prompt.endswith("."):
            prompt = prompt[:-1]

        while True:
            print(CYAN + prompt + ENDC)
            user_input = input(">> [Y/n]: ")

            if user_input.lower() == "y":
                return True
            elif user_input.lower() == "n":
                return False

            print(f'"{user_input}" is not a valid input! Enter "y" or "n".\n')


if __name__ == "__main__":
    true_or_false = Prompt.yes_no("Works?")
    user_input = Prompt.input("How old are you?")
    true_or_false = Prompt.confirm("Press ENTER if you accept the terms")
    Prompt.confirm("Do you confirm?")
    user_choice = Prompt.choose(
        "Choose [A] if you like apples or [P] if you like pears", options=["a", "p"]
    )

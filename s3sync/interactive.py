import argparse
import pathlib
from typing import List

from .prompt import Prompt, RED, ENDC, CYAN
from .const import *
from .utils import systemd_service_is_active, restart_systemd_service


class MasterFile:
    def __init__(self):
        self.contents: List[pathlib.Path] = []

        try:
            with open(WATCHLIST_PATH, "r") as f:
                self.contents: List = [
                    pathlib.Path(l.replace("\n", "")) for l in f.readlines()
                ]
        except FileNotFoundError:
            WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(WATCHLIST_PATH, "w+") as f:
                pass

    def list(self):
        for idx, filepath in enumerate(self.contents):
            s = f" {idx + 1}".ljust(6)
            s += f"{filepath.exists()}".ljust(8)
            s += str(filepath)
            print(s)

    def remove_path(self, path: pathlib.Path):
        self.contents = [c for c in self.contents if c != path]
        self.save()

    def remove_index(self, idx: int):
        del self.contents[idx]
        self.save()

    def save(self):
        with open(WATCHLIST_PATH, "w") as f:
            f.write("\n".join([str(path) for path in self.contents]))

        restart_systemd_service("s3sync")

    def add(self, filepath: str):
        path = pathlib.Path(filepath)

        if not path.exists():
            print(RED + "\nThis file does not exist!\n" + ENDC)
            return
        elif path.resolve() in self.contents:
            print(RED + "\nThis path already exists in watchlist!\n" + ENDC)
            return

        self.contents.append(path.resolve())
        self.save()
        print("Done!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-a",
        "--add",
        action="store_true",
        help="",
    )

    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="",
    )

    args = parser.parse_args()

    if systemd_service_is_active("s3sync"):
        print(CYAN + "s3sync.service is active!\n" + ENDC)
    else:
        print("**************************************************************")
        print(
            RED
            + "ATTN: s3sync.service is not active. Run `s3sync-start` to fix."
            + ENDC
        )
        print("**************************************************************\n")

    masterfile = MasterFile()

    try:
        while True:
            masterfile.list()

            choice = Prompt.choose(
                "\nWhat would you like to do?", options=["r", "remove", "a", "add"]
            )

            if choice in ("remove", "r"):
                user_input = Prompt.input("Enter # or filepath to remove:")

                if user_input.isnumeric():
                    if int(user_input) > len(masterfile.contents):
                        print(RED + "\nNot a valid index!\n" + ENDC)
                        continue

                    masterfile.remove_index(int(user_input) - 1)
                elif pathlib.Path(user_input) in masterfile.contents:
                    masterfile.remove_path(pathlib.Path(user_input))
                else:
                    print(RED + "Not a valid input!" + ENDC)

            elif choice in ("add", "a"):
                fpath = Prompt.input("\nPaste filepath:")
                if not fpath:
                    continue

                masterfile.add(fpath)
    except KeyboardInterrupt:
        pass

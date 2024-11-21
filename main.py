import os
# Import ascii art
from art.ascii_art import print_ascii_art

# Import commands
from commands.exit import exit_program
from commands.clear import clear_screen
from commands.help import show_help
from commands.discover import discover

def show_prompt():
    print("BlackArmy> ", end="")

def parse_arguments(command):
    return command.split()

def main():
    commands = {
        "help": show_help,
        "clear": clear_screen,
        "exit": exit_program
    }

    print_ascii_art()

    while True:
        show_prompt()
        command = input()
        args = parse_arguments(command)

        if not args:
            continue

        if args[0] == "discover" and len(args) >= 4:
            domain = args[1]
            wordlist = args[3]
            discover(domain, wordlist)
        elif args[0] in commands:
            commands[args[0]]()
            if args[0] == "exit":
                break
        elif command:
            os.system(command)

if __name__ == "__main__":
    main()

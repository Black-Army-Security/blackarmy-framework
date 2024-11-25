import os
# Import ascii art
from art.ascii_art import print_ascii_art
# Import commands
from commands.exit import exit_program
from commands.clear import clear_screen
from commands.help import show_help
from commands.discover import discover
from commands.webdiscover import webdiscover

def show_prompt():
    print("BlackArmy> ", end="")

def parse_arguments(command):
    return command.split()

def main():
    # Mapping commands to functions
    commands = {
        "help": show_help,
        "clear": clear_screen,
        "exit": exit_program
    }

    print_ascii_art()

    while True:
        show_prompt()
        command = input().strip()
        args = parse_arguments(command)

        if not args:
            continue

        # Handle 'discover' command
        if args[0] == "discover":
            if len(args) == 4 and args[2] == "-w":
                domain = args[1]
                wordlist = args[3]
                discover(domain, wordlist)
            else:
                print("Incorrect command. Usage: discover domain.com -w /path/to/wordlist.txt")

        # Handle 'webdiscover' command
        elif args[0] == "webdiscover":
            if len(args) == 4 and args[2] == "-w":
                target_url = args[1]
                wordlist = args[3]
                webdiscover(target_url, wordlist)
            else:
                print("Incorrect command. Usage: webdiscover target_url.com -w /path/to/wordlist.txt")

        # Handle other commands
        elif args[0] in commands:
            commands[args[0]]()
            if args[0] == "exit":
                break

        # Handle unknown commands
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()

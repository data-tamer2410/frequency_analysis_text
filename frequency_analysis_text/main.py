"""This project is a program designed for analyzing text files."""
from frequency_analysis_text.functionality import AnalysisText, ProgramState, EmptyFileError, \
    InvalidFileFormatError
import sys


def show_info_commands(for_gui=False):
    if for_gui:
        return ("Smart mode: Toggle smart mode for advanced text analysis.\n"
                "Root mode: Toggle root mode for root word analysis.\n"
                "To pickle: Save the current text analysis to a pickle file.\n"
                "Remove: Remove selected words from the text.\n"
                "Case sens: Toggle case sensitivity in text analysis.\n"
                "Restart: Restart the text analysis with the original text.\n"
                "To json: Save the current text analysis to a JSON file.\n"
                "Result: Update the text display with the current analysis results.\n"
                "Load File: Load a new text file into the application.\n"
                "Undo: Undo the last text modification.\n"
                "Redo: Redo the last undone text modification.")
    return (
        "1. '!help' to show information about commands;\n"
        "2. '!enter_file' for enter new file;\n"
        "3. '!list_words' to show all unique words;\n"
        "4. '!case_sens' to show the status case sensitive;\n"
        "5. '!case_sens_on' to turn on case sensitive;\n"
        "6. '!case_sens_off' to turn off case sensitive;\n"
        "7. '!smart_mode' to show the status smart mode;\n"
        "8. '!smart_mode_on' to enable smart mode;\n"
        "9. '!smart_mode_off' to disable smart mode;\n"
        "10. '!restart_text' to restart the text;\n"
        "11. '!text' to show the current text;\n"
        "12. '!result' to show analysis results;\n"
        "13. '!remove_words' to remove words from the text;\n"
        "14. '!replace_words' to replace words in the text;\n"
        "15. '!save_to_json' to save the text analysis to a JSON file;\n"
        "16. '!save_to_pickle' to save the text analysis to a Pickle file;\n"
        "17. '!root_mode' to show the status root mode;\n"
        "18. '!root_mode_on' to enable root mode;\n"
        "19. '!root_mode_off' to disable root mode;\n"
        "20. '!close' to close the program.\n"
    )


def parse_input(user_input: str):
    """Processes the user input string."""
    user_input = user_input.strip()
    if not user_input.startswith('!'):
        return user_input, []
    command, *args = user_input.split()
    args = ' '.join(args)
    return command, args


def user_command_handler(user_input: str, obj_text: AnalysisText, state: ProgramState):
    """Handles user commands."""
    command, args = parse_input(user_input)
    command_args_dict = {
        '!replace_words': obj_text.remove_or_replace_last_words
    }
    command_dict = {
        '!root_mode_on': obj_text.root_mode_on,
        '!root_mode_off': obj_text.root_mode_off,
        '!root_mode': obj_text.show_root_mode,
        '!case_sens_on': obj_text.case_sens_on,
        '!case_sens_off': obj_text.case_sens_off,
        '!case_sens': obj_text.show_case_sens,
        '!smart_mode_on': obj_text.smart_mode_on,
        '!smart_mode_off': obj_text.smart_mode_off,
        '!smart_mode': obj_text.show_smart_mode,
        '!enter_file': state.new_file,
        '!restart_text': obj_text.restart_user_text,
        '!text': obj_text.show_user_text,
        '!result': obj_text.show_result,
        '!remove_words': obj_text.remove_or_replace_last_words,
        '!save_to_json': obj_text.save_file_to_json,
        '!save_to_pickle': obj_text.save_file_to_pickle,
        '!list_words': obj_text.show_list_words,
        '!help': show_info_commands,
        '!close': sys.exit
    }

    if command in command_dict:
        print(command_dict[command]())
    elif command in command_args_dict:
        print(command_args_dict[command](args))
    elif command.startswith('!'):
        print(f'Incorrect command.\n\n{show_info_commands()}')
    else:
        print(obj_text.search_word(command)[0])


def main():
    """The main script for user interaction."""
    state = ProgramState()
    obj_text = None
    while True:
        if state.enter_new_file:
            try:
                user_path = input('Enter path to file:').strip()
                obj_text = AnalysisText(user_path)
                obj_text.load_file()
                print(obj_text)
                state.enter_new_file = False
            except (PermissionError, FileNotFoundError):
                print('File not found or access denied.')
                continue
            except IOError as e:
                print(f'An I/O error occurred: {e}.')
                continue
            except (EmptyFileError, InvalidFileFormatError) as e:
                print(e)
                continue
            except (AttributeError, KeyError):
                print('The file is corrupted.')
                continue

        user_input = input('Enter word for search or command:')
        user_command_handler(user_input, obj_text, state)


if __name__ == '__main__':
    main()

from functionality import AnalysisText, ProgramState, EmptyFileError
import sys


def show_info_commands():
    return ("1. '__enter_file__' for enter new file;\n"
            "2. '__save_file__' to save file;\n"
            "3. '__close_program__' to close program;\n"
            "4. '__list_words__' to show all unique words;\n"
            "5. '__case_sens__' to show the status case sensitive;\n"
            "6. '__case_sens_on__' to on case sensitive;\n"
            "7. '__case_sens_off__' to off case sensitive;\n"
            "8. '__help__' to show information about commands;\n"
            "9. '__smart_mode__' to show the status smart mode;\n"
            "10. '__smart_mode_on__' to on the ability to search for words not only as individual words;\n"
            "11. '__smart_mode_off__' to off the ability to search for words not only as individual words.")


def user_command_handler(command: str, obj_text: AnalysisText, state: ProgramState):
    command_dict = {
        '__save_file__': obj_text.save_text,
        '__list_words__': obj_text.show_list_words,
        '__help__': show_info_commands,
        '__close_program__': sys.exit

    }

    if command == '__enter_file__':
        state.enter_new_file = True
    elif command == '__smart_mode_off__':
        obj_text.smart_mode = False
        print(f'Smart mode off.')
    elif command == '__smart_mode_on__':
        obj_text.smart_mode = True
        print(f'Smart mode on{", case sensitive off." if obj_text.case_sensitive else "."}')
        obj_text.case_sensitive = False
    elif command == '__smart_mode__':
        print(f'Smart mode: {"on." if obj_text.smart_mode else "off."}')
    elif command == '__case_sens_on__':
        obj_text.case_sensitive = True
        print(f'Case sensitive on{", smart mode off." if obj_text.smart_mode else "."}')
        obj_text.smart_mode = False
    elif command == '__case_sens_off__':
        obj_text.case_sensitive = False
        print('Case sensitive off.')
    elif command == '__case_sens__':
        print(f'Case sensitive: {"on." if obj_text.case_sensitive else "off."}')
    elif command in command_dict:
        print(command_dict[command]())
    elif not command:
        print('Print word or command.')
    else:
        print(obj_text.search_word(command))


def parse_input(user_input: str):
    return user_input.strip()


def main():
    state = ProgramState()
    obj_text = None
    while True:
        if state.enter_new_file:
            try:
                user_path = parse_input(input('Enter path to file:'))
                obj_text = AnalysisText(user_path)
                obj_text.load_text()
                obj_text.analyze_text()
                print(obj_text)
                state.enter_new_file = False
            except (PermissionError, FileNotFoundError):
                print('File not found or access denied.')
                continue
            except IOError as e:
                print(f'An I/O error occurred: {e}')
                continue
            except EmptyFileError as e:
                print(e)
                continue

        command = parse_input(input('Enter word for search or command:'))
        user_command_handler(command, obj_text, state)


if __name__ == '__main__':
    main()

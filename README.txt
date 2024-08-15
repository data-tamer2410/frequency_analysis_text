1. Enter path to file: (1. Path to file.)



2. Enter word for search: (1. Word for search,
                           2. '__enter_file__' to enter new file,
                           3. '__save_file__' to save file,
                           4. '__close_program__' to close program,
                           5. '__list_words__' to show all unique words,
                           6. '__case_sens__' to show the status case sensitive,
                           7. '__case_sens_on__' to on case sensitive,
                           8. '__case_sens_off__' to off case sensitive,
                           9. '__help__' to show information about commands,
                           10. '__smart_mode__' to show the status smart mode,
                           11. '__smart_mode_on__' to on the ability to search for words not only as individual words',
                           12. '__smart_mode_off__' to off the ability to search for words not only as individual words.')

Ukrainian / Українською

Опис проекту:
Цей проект є програмою для аналізу текстових файлів. Вона дозволяє завантажувати текстові файли, аналізувати частоту слів та чисел, а також здійснювати пошук по тексту з урахуванням чутливості до регістру та спеціального "розумного" режиму. Програма також підтримує збереження результатів аналізу в окремі файли.

Основні компоненти:

class EmptyFileError
Виняток, який виникає, коли файл не містить слів або чисел.

class ProgramState:
Зберігає стан програми, визначаючи, чи потрібно завантажувати новий файл.

class AnalysisText:
Клас, що представляє аналіз тексту.

Методи:
__init__(self, path): Ініціалізація з шляхом до файлу.
load_text(self): Завантаження тексту з файлу.
analyze_text(self): Аналіз тексту для визначення частоти слів і чисел.
save_text(self): Збереження результатів аналізу у файл.
search_word(self, word): Пошук слова в тексті з використанням кешу.
show_list_words(self): Показати список унікальних слів.
__str__(self): Формування рядка з результатами аналізу.

main.py:
Основний скрипт для взаємодії з користувачем.

Функції:
show_info_commands(): Показати інформацію про команди.
user_command_handler(command, obj_text, state): Обробка команд користувача.
parse_input(user_input): Обробка введеного користувачем рядка.
main(): Головний цикл програми.

Використання(всі доступні команди написані на початку цього файлу):
Запустіть скрипт main.py.
Введіть шлях до файлу, який ви хочете проаналізувати.
Після аналізу ви можете виконувати такі дії:
Вводити слова для пошуку.
Використовувати спеціальні команди для керування режимами (чутливість до регістру, "розумний" режим).
Зберігати результати аналізу у файл.
Отримати список усіх унікальних слів.




English

Project Description:
This project is a program designed for analyzing text files. It allows loading text files, analyzing word and number frequencies, and searching the text with case sensitivity and a special "smart" mode. The program also supports saving the analysis results to separate files.

Main Components:

class EmptyFileError:
An exception raised when the file does not contain words or numbers.

class ProgramState:
Stores the state of the program, determining whether a new file needs to be loaded.

class AnalysisText:
A class representing text analysis.

Methods:
__init__(self, path): Initializes with the path to the file.
load_text(self): Loads the text from the file.
analyze_text(self): Analyzes the text to determine word and number frequencies.
save_text(self): Saves the analysis results to a file.
search_word(self, word): Searches for a word in the text using cache.
show_list_words(self): Shows a list of unique words.
__str__(self): Generates a string with the analysis results.

main.py:
The main script for user interaction.

Functions:
show_info_commands(): Shows information about available commands.
user_command_handler(command, obj_text, state): Handles user commands.
parse_input(user_input): Processes the user input string.
main(): The main program loop.

Usage(all available commands are written at the beginning of this file):
Run the main.py script.
Enter the path to the file you want to analyze.
After analysis, you can perform the following actions:
Enter words for searching.
Use special commands to control modes (case sensitivity, "smart" mode).
Save the analysis results to a file.
Get a list of all unique words.

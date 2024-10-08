"""
This module is designed for text analysis from various file formats
(.txt, .json, .pkl, .pickle), including searching, replacing words,
and saving and loading data.
"""

import pickle
from pathlib import Path
from collections import Counter
import copy
import datetime
import re
import json
import pymorphy2
from nltk.stem import SnowballStemmer
import langid


class InvalidFileFormatError(Exception):
    """
    An exception raised when attempting to load a file with an unsupported format.
    """

    def __init__(self):
        super().__init__("Invalid file format.")


class EmptyFileError(Exception):
    """An exception raised when the file does not contain words or numbers."""

    def __init__(self):
        super().__init__("The file does not contain words or numbers.")


class ProgramState:
    """Stores the state of the program, determining whether a new file needs to be loaded."""

    def __init__(self):
        self.enter_new_file = True

    def new_file(self):
        """
        Returns a string of # characters indicating the need to load a new file.
        """
        self.enter_new_file = True
        return "#" * 50


class AnalysisText:
    """A class representing text analysis."""

    def __init__(self, path):
        """Initializes with the path to the file."""
        self.path = Path(path)
        self.new_file = False
        self.root_mode = False
        self.case_sensitive = False
        self.smart_mode = False
        self.last_search_key = None
        self.last_pattern = None
        self.support_language = ("uk", "ru", "en")
        self.old_text = None
        self.text = None
        self.result_counter = None
        self.datetime_created = None
        self.language = None
        self.search_cache = {}
        self.search_cache_keys = []

        self.history = []
        self.redo_stack = []

    def root_mode_on(self):
        """
        Enables root mode and disables smart mode and case sensitivity.
        """
        self.root_mode = True
        mess = (
            f"Root mode on"
            f'{", smart mode off, case sensitive off." if self.smart_mode or self.case_sensitive else "."}'
        )
        self.smart_mode = False
        self.case_sensitive = False
        return mess

    def root_mode_off(self):
        """
        Disables root mode.
        """
        self.root_mode = False
        return "Root mode off."

    def show_root_mode(self):
        """
        Returns a string showing the status of root mode.
        """
        return f'Root mode: {"on." if self.root_mode else "off."}'

    def case_sens_on(self):
        """
        Enables case sensitivity and disables smart mode and root mode.
        """
        self.case_sensitive = True
        mess = f'Case sensitive on{", smart mode off, root mode off." if self.smart_mode or self.root_mode else "."}'
        self.smart_mode = False
        self.root_mode = False
        return mess

    def case_sens_off(self):
        """
        Disables case sensitivity.
        """
        self.case_sensitive = False
        return "Case sensitive off."

    def show_case_sens(self):
        """
        Returns a string showing the status of case sensitivity.
        """
        return f'Case sensitive: {"on." if self.case_sensitive else "off."}'

    def smart_mode_on(self):
        """
        Enables smart mode if the language is supported.
        """
        if self.language in self.support_language:
            self.smart_mode = True
            mess = (
                f"Smart mode on"
                f'{", case sensitive off, root mode off." if self.case_sensitive or self.root_mode else "."}'
            )
            self.case_sensitive = False
            self.root_mode = False
            return mess
        return (
            f"At the moment the Smart mode only supports {self.support_language} languages,"
            f" your text is in the {self.language} language."
        )

    def smart_mode_off(self):
        """
        Disables smart mode.
        """
        self.smart_mode = False
        return "Smart mode off."

    def show_smart_mode(self):
        """
        Returns a string showing the status of smart mode.
        """
        return f'Smart mode: {"on." if self.smart_mode else "off."}'

    def show_user_text(self):
        """
        Returns the current text.
        """
        return self.text

    def restart_user_text(self):
        """
        Restarts the text if it differs from the original.
        """
        if self.text != self.old_text:
            self.save_state()
            self.text = self.old_text
            return "Text restarted."
        return "The text is not restarted because it is already equal to the original text."

    def show_result(self):
        """
        Returns the current analysis results.
        """
        return self

    def load_pickle_file(self, for_gui):
        """
        Loads data from a .pkl or .pickle file.
        """
        with open(self.path, "rb") as file:
            obj = pickle.load(file)
            self.old_text = obj.old_text
            self.result_counter = copy.copy(obj.result_counter)
            self.datetime_created = obj.datetime_created
            self.language = obj.language
            self.text = obj.text
            self.search_cache = copy.copy(obj.search_cache) if not for_gui else {}
            self.search_cache_keys = (
                copy.copy(obj.search_cache_keys) if not for_gui else []
            )
            self.history = copy.copy(obj.history)
            self.redo_stack = copy.copy(obj.redo_stack)

    def load_json_file(self, for_gui):
        """
        Loads data from a .json file.
        """
        with open(self.path, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.old_text = data["old_text"]
            self.result_counter = copy.copy(data["result_counter"])
            self.datetime_created = datetime.datetime.strptime(
                data["datetime_created"], "%Y-%m-%d %H:%M:%S.%f"
            )
            self.language = data["language"]
            self.text = data["text"]
            self.search_cache = (
                copy.deepcopy(data["search_cache"]) if not for_gui else {}
            )
            self.search_cache_keys = (
                copy.copy(data["search_cache_keys"]) if not for_gui else []
            )
            self.history = copy.copy(data["history"])
            self.redo_stack = copy.copy(data["redo_stack"])

    def load_txt_file(self):
        """
        Loads data from a .txt file.
        """
        self.new_file = True
        with open(self.path, "r", encoding="utf-8") as file:
            self.old_text = file.read()

    def load_file(self, for_gui=False):
        """Loads the text from the file."""
        suffix = self.path.suffix
        if suffix in (".pkl", ".pickle"):
            self.load_pickle_file(for_gui)
        elif suffix == ".json":
            self.load_json_file(for_gui)
        elif suffix == ".txt":
            self.load_txt_file()
            self.analyze_txt_file()
        else:
            raise InvalidFileFormatError

    def update_result_counter(self):
        """
        Updates the result counter with word and number frequencies.
        """
        pattern = r"\b\w+(?:[-']\w+)*\b|\b\d*\.\d+\b|\b\d+\b"
        counter_text = Counter(re.findall(pattern, self.text))
        if not counter_text:
            raise EmptyFileError
        self.result_counter = dict(
            sorted(counter_text.items(), key=lambda item: item[0])
        )

    def analyze_txt_file(self):
        """Analyzes the text to determine word and number frequencies."""
        if self.new_file:
            self.datetime_created = datetime.datetime.now()
            self.language, _ = langid.classify(self.old_text)
            self.text = self.old_text

    def save_file_to_pickle(self):
        """
        Saves analysis results to a .pkl or .pickle file.
        """
        path, mess = self.get_path_to_save(".pkl")
        with open(path, "wb") as file:
            pickle.dump(self, file)
        return mess

    def save_file_to_json(self):
        """
        Saves analysis results to a .json file.
        """
        data = {
            "old_text": self.old_text,
            "result_counter": self.result_counter,
            "datetime_created": self.datetime_created.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "language": self.language,
            "text": self.text,
            "search_cache": self.search_cache,
            "search_cache_keys": self.search_cache_keys,
            "history": self.history,
            "redo_stack": self.redo_stack,
        }
        path, mess = self.get_path_to_save(".json")
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return mess

    def get_path_to_save(self, suffix):
        """Saves the analysis results to a file."""
        file_name = self.path.stem
        old_suffix = self.path.suffix
        if old_suffix == ".txt":
            path = f"{self.datetime_created.date()}_{file_name}_000{suffix}"
        else:
            path = f"{file_name}{suffix}"
        count = 1
        while Path(path).exists():
            if old_suffix == ".txt":
                path = f"{self.datetime_created.date()}_{file_name}_{count:03}{suffix}"
            else:
                path = f"{file_name[:-3]}{count:03}{suffix}"
            count += 1
        return (
            path,
            f'File save to {"pickle" if suffix in (".pkl", ".pickle") else "json"}.',
        )

    @staticmethod
    def get_words_ru_uk(word, lang):
        """
        Returns patterns and words for Russian or Ukrainian languages.
        """
        parsed_word = pymorphy2.MorphAnalyzer(lang=lang).parse(word)
        lexeme = parsed_word[0].lexeme
        words = ", ".join(set(form.word for form in lexeme))
        list_words_for_pattern = set(rf"\b{re.escape(form.word)}\b" for form in lexeme)
        return "|".join(list_words_for_pattern), words

    @staticmethod
    def get_words_en(word):
        """
        Returns patterns and words for English.
        """
        pattern = rf"\b\w*{re.escape(SnowballStemmer('english').stem(word))}\w*\b"
        words = f"*{pattern}*"
        return pattern, words

    def get_pattern_and_text_and_words(self, word: str):
        """
        Returns the pattern and text for searching a word.
        """
        if self.case_sensitive:
            return rf"\b{re.escape(word)}\b", self.text, word
        lower_word = word.lower()
        lower_text = self.text.lower()
        if self.root_mode:
            return (
                rf"\b\w*{re.escape(lower_word)}\w*\b",
                lower_text,
                f"*{lower_word}*",
            )
        if self.smart_mode:
            pattern, words = (
                self.get_words_en(lower_word)
                if self.language == "en"
                else self.get_words_ru_uk(lower_word, self.language)
            )
            return pattern, lower_text, words
        return rf"\b{re.escape(lower_word)}\b", lower_text, lower_word

    def save_cache(self, search_key, res):
        """
        Saves the search result to the cache.
        """
        if len(self.search_cache) > 500:
            key = self.search_cache_keys.pop(0)
            del self.search_cache[key]
        self.search_cache_keys.append(search_key)
        self.search_cache[search_key] = res

    def update_cache(self, case_sens):
        """
        Updates the cache based on case sensitivity.
        """
        keys_for_remove = []
        for key, (value, *_) in self.search_cache.items():
            if re.findall(
                self.last_pattern, (value.lower() if not case_sens else value)
            ):
                keys_for_remove.append(key)
        for key in keys_for_remove:
            del self.search_cache[key]
            self.search_cache_keys.remove(key)

    def save_state(self):
        """
        Saves the current state to the history.
        """
        self.redo_stack.clear()
        if self.history:
            if len(self.history) > 50:
                self.history.pop(0)
            if self.history[-1] != self.text:
                self.history.append(self.text)
        elif self.text != self.old_text:
            self.history.append(self.text)

    def remove_or_replace_last_words(self, new_word=""):
        """
        Removes or replaces the last searched words in the text.
        """
        if not self.last_pattern:
            return "First find the word in the text."
        self.save_state()
        case_sens = self.last_search_key.endswith("True False False")
        if case_sens:
            self.text = re.sub(self.last_pattern, new_word, self.text)
        else:
            match = re.finditer(self.last_pattern, self.text.lower())
            list_index = [(w.start(), w.end()) for w in match]
            for start, end in sorted(list_index, reverse=True):
                self.text = self.text[:start] + new_word + self.text[end:]
        self.update_cache(case_sens)
        self.last_pattern = None
        self.last_search_key = None
        return "Words replaced." if new_word else "Words removed."

    def get_all_rows(self, text):
        """
        Gets all non-empty rows from the text.
        """
        all_rows = [row for row in text.split("\n") if row]
        all_orig_rows = [row for row in self.text.split("\n") if row]
        return all_rows, all_orig_rows

    @staticmethod
    def perform_search(words, all_rows, all_orig_rows, pattern):
        """
        Performs a search for words in the rows of text.
        """
        res, for_index_gui = "", ""
        for_log_gui = f'Search for "{words}":\n\n'
        n_rows_n_words = []
        found = False
        n_row = 0
        for row in all_rows:
            n_row += 1
            count_words_in_row = len(re.findall(pattern, row))
            if count_words_in_row > 0:
                found = True
                res += f"№{n_row}: {all_orig_rows[n_row - 1]}\n\n"
                for_index_gui += f"№{n_row}: {row}\n\n"
                n_rows_n_words.append((n_row, count_words_in_row))
        return found, res, for_index_gui, for_log_gui, n_rows_n_words

    @staticmethod
    def format_for_gui(pattern, index_log_nrw):
        """
        Formats the search results for GUI display.
        """
        index, log, n_row_word = index_log_nrw
        sum_words = sum(n_word[1] for n_word in n_row_word)
        match = re.finditer(pattern, index)
        list_index = [(w.start(), w.end()) for w in match]
        width_1 = max(max(len(str(n_row[0])) for n_row in n_row_word), 8)
        width_2 = max(max(len(str(count_words[1])) for count_words in n_row_word), 11)
        log += f"Found words: {sum_words}.\n\n"
        log += f'{"№ string":^{width_1}}|{"count words":^{width_2}}\n{"-" * (width_1 + width_2 + 1)}\n'
        log += "\n".join(
            [
                f"{n_row:^{width_1}}|{count_words:^{width_2}}"
                for n_row, count_words in n_row_word
            ]
        )

        return list_index, log

    def search_word(self, word, for_gui=False):
        """Searches for a word in the text using cache."""
        pattern, text, words = self.get_pattern_and_text_and_words(word)
        search_key = (
            f"{pattern} {self.case_sensitive} {self.smart_mode} {self.root_mode}"
        )
        if search_key in self.search_cache:
            self.last_search_key = search_key
            self.last_pattern = pattern
            return (
                self.search_cache[search_key][0],
                self.search_cache[search_key][1],
                self.search_cache[search_key][2],
            )

        all_rows, all_orig_rows = self.get_all_rows(text)

        found, res, *index_log_nrw = self.perform_search(
            words, all_rows, all_orig_rows, pattern
        )

        if not found or not word:
            self.last_search_key = None
            self.last_pattern = None
            return (
                (f'"{word}" - not exist in text.',)
                if word
                else ("Enter a word for search.",)
            )

        list_index_for_gui, log_for_gui = None, None
        if for_gui:
            list_index_for_gui, log_for_gui = self.format_for_gui(
                pattern, index_log_nrw
            )

        if not self.redo_stack:
            self.save_cache(search_key, (res, list_index_for_gui, log_for_gui))
        self.last_search_key = search_key
        self.last_pattern = pattern
        return res, list_index_for_gui, log_for_gui

    def show_list_words(self):
        """Shows a list of unique words."""
        self.update_result_counter()
        return list(self.result_counter.keys())

    def __str__(self):
        """Generates a string with the analysis results."""
        self.update_result_counter()
        width_1 = max(max(len(word) for word in self.result_counter.keys()), 4)
        width_2 = max(max(len(str(num)) for num in self.result_counter.values()), 5)
        res = "Analysis Results:\n\n"
        res += f'{"word":^{width_1}}|{"count":^{width_2}}\n{"-" * (width_1 + width_2 + 1)}\n'
        res += "\n".join(
            [
                f"{key:^{width_1}}|{self.result_counter[key]:^{width_2}}"
                for key in self.result_counter
            ]
        )
        res += (
            "\n\nAnalysis performed on: "
            + self.datetime_created.strftime("%d %B %Y; %H:%M")
            + "\n"
        )
        return res


def show_info_commands(for_gui=False):
    """
    Provides a description of available commands based on the context.
    """
    if for_gui:
        return (
            "Smart mode: Toggle smart mode for advanced text analysis.\n"
            "Root mode: Toggle root mode for root word analysis.\n"
            "To pickle: Save the current text analysis to a pickle file.\n"
            "Remove: Remove selected words from the text.\n"
            "Case sens: Toggle case sensitivity in text analysis.\n"
            "Restart: Restart the text analysis with the original text.\n"
            "To json: Save the current text analysis to a JSON file.\n"
            "Result: Update the text display with the current analysis results.\n"
            "Load File: Load a new text file into the application.\n"
            "Undo: Undo the last text modification.\n"
            "Redo: Redo the last undone text modification."
        )
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

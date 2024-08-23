import pickle
from pathlib import Path
from collections import Counter
import copy
import datetime
import re
import pymorphy2
from nltk.stem import SnowballStemmer
import langid
import json


class InvalidFileFormatError(Exception):
    def __init__(self):
        super().__init__('Invalid file format.')


class EmptyFileError(Exception):
    """An exception raised when the file does not contain words or numbers."""

    def __init__(self):
        super().__init__('The file does not contain words or numbers.')


class ProgramState:
    """Stores the state of the program, determining whether a new file needs to be loaded."""

    def __init__(self):
        self.enter_new_file = True

    def new_file(self):
        self.enter_new_file = True
        return '#' * 50


class AnalysisText:
    """A class representing text analysis."""

    def __init__(self, path):
        """Initializes with the path to the file."""
        self.path = Path(path)
        self.new_file = False
        self.case_sensitive = False
        self.smart_mode = False
        self.last_search_key = None
        self.last_pattern = None
        self.support_language = ('uk', 'ru', 'en')
        self.old_text = None
        self.text = None
        self.result_counter = None
        self.datetime_created = None
        self.language = None
        self.search_cache = {}
        self.search_cache_keys = []

        self.history = []
        self.redo_stack = []

    def case_sens_on(self):
        self.case_sensitive = True
        mess = f'Case sensitive on{", smart mode off." if self.smart_mode else "."}'
        self.smart_mode = False
        return mess

    def case_sens_off(self):
        self.case_sensitive = False
        return 'Case sensitive off.'

    def show_case_sens(self):
        return f'Case sensitive: {"on." if self.case_sensitive else "off."}'

    def smart_mode_on(self):
        if self.language in self.support_language:
            self.smart_mode = True
            mess = f'Smart mode on{", case sensitive off." if self.case_sensitive else "."}'
            self.case_sensitive = False
            return mess
        return (f'At the moment the mode "__smart_mode__" only supports {self.support_language} languages,'
                f' your text is in the {self.language} language.')

    def smart_mode_off(self):
        self.smart_mode = False
        return 'Smart mode off.'

    def show_smart_mode(self):
        return f'Smart mode: {"on." if self.smart_mode else "off."}'

    def show_user_text(self):
        return self.text

    def restart_user_text(self):
        if self.text != self.old_text:
            self.save_state()
            self.text = self.old_text
            return 'Text restarted.'
        return 'The text is not restarted because it is already equal to the original text.'

    def show_result(self):
        return self

    def load_pickle_file(self):
        with open(self.path, 'rb') as file:
            obj = pickle.load(file)
            self.old_text = obj.old_text
            self.result_counter = copy.copy(obj.result_counter)
            self.datetime_created = obj.datetime_created
            self.language = obj.language
            self.text = obj.text
            self.search_cache = copy.copy(obj.search_cache)
            self.search_cache_keys = copy.copy(obj.search_cache_keys)
            self.history = copy.copy(obj.history)
            self.redo_stack = copy.copy(obj.redo_stack)

    def load_json_file(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.old_text = data['old_text']
            self.result_counter = copy.copy(data['result_counter'])
            self.datetime_created = datetime.datetime.strptime(data['datetime_created'], '%Y-%m-%d %H:%M:%S.%f')
            self.language = data['language']
            self.text = data['text']
            self.search_cache = copy.deepcopy(data['search_cache'])
            self.search_cache_keys = copy.copy(data['search_cache_keys'])
            self.history = copy.copy(data['history'])
            self.redo_stack = copy.copy(data['redo_stack'])

    def load_txt_file(self):
        self.new_file = True
        with open(self.path, 'r', encoding='utf-8') as file:
            self.old_text = file.read()

    def load_file(self):
        """Loads the text from the file."""
        suffix = self.path.suffix
        if suffix in ('.pkl', '.pickle'):
            self.load_pickle_file()
        elif suffix == '.json':
            self.load_json_file()
        elif suffix == '.txt':
            self.load_txt_file()
            self.analyze_txt_file()
        else:
            raise InvalidFileFormatError

    def update_result_counter(self):
        pattern = r'\b\w+\b|\b\d+\b|\b\d+\.\d+\b'
        counter_text = Counter(re.findall(pattern, self.text))
        if not counter_text:
            raise EmptyFileError
        self.result_counter = dict(sorted(counter_text.items(), key=lambda item: item[0]))

    def analyze_txt_file(self):
        """Analyzes the text to determine word and number frequencies."""
        if self.new_file:
            self.datetime_created = datetime.datetime.now()
            self.language, _ = langid.classify(self.old_text)
            self.text = self.old_text

    def save_file_to_pickle(self):
        path, mess = self.get_path_to_save('.pkl')
        with open(path, 'wb') as file:
            pickle.dump(self, file)
        return mess

    def save_file_to_json(self):
        data = {'old_text': self.old_text,
                'result_counter': self.result_counter,
                'datetime_created': self.datetime_created.strftime('%Y-%m-%d %H:%M:%S.%f'),
                'language': self.language,
                'text': self.text,
                'search_cache': self.search_cache,
                'search_cache_keys': self.search_cache_keys,
                'history': self.history,
                'redo_stack': self.redo_stack}
        path, mess = self.get_path_to_save('.json')
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return mess

    def get_path_to_save(self, suffix):
        """Saves the analysis results to a file."""
        file_name = self.path.stem
        old_suffix = self.path.suffix
        if old_suffix == '.txt':
            path = f'{self.datetime_created.date()}_{file_name}_000{suffix}'
        else:
            path = f'{file_name}{suffix}'
        count = 1
        while Path(path).exists():
            if old_suffix == '.txt':
                path = f'{self.datetime_created.date()}_{file_name}_{count:03}{suffix}'
            else:
                path = f'{file_name[:-3]}{count:03}{suffix}'
            count += 1
        return path, f'File save to {"pickle" if suffix == ".pkl" or suffix == ".pickle" else "json"}.'

    @staticmethod
    def is_float_or_int(word):
        try:
            float(word)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_words_ru_uk(word, lang):
        parsed_word = pymorphy2.MorphAnalyzer(lang=lang).parse(word)
        lexeme = parsed_word[0].lexeme
        list_words = set(r'\b' + re.escape(form.word) + r'\b' for form in lexeme)
        return '|'.join(list_words)

    @staticmethod
    def get_words_en(word):
        return re.escape(SnowballStemmer('english').stem(word))

    def get_pattern_and_text(self, word: str):
        if self.case_sensitive or self.is_float_or_int(word):
            return f'\\b{re.escape(word)}\\b', self.text
        word = word.lower()
        text = self.text.lower()
        if self.smart_mode:
            pattern = self.get_words_en(word) if self.language == 'en' else self.get_words_ru_uk(word, self.language)
            return pattern, text
        return f'\\b{re.escape(word)}\\b', text

    def save_cache(self, search_key, res):
        if len(self.search_cache) > 500:
            key = self.search_cache_keys.pop(0)
            del self.search_cache[key]
        self.search_cache_keys.append(search_key)
        self.search_cache[search_key] = res

    def update_cache(self, case_sens):
        keys_for_remove = []
        for key, (value, _) in self.search_cache.items():
            if re.findall(self.last_pattern, (value.lower() if not case_sens else value)):
                keys_for_remove.append(key)
        for key in keys_for_remove:
            del self.search_cache[key]
            self.search_cache_keys.remove(key)

    def save_state(self):
        self.redo_stack.clear()
        if self.history:
            if len(self.history) > 50:
                self.history.pop(0)
            if self.history[-1] != self.text:
                self.history.append(self.text)
        elif self.text != self.old_text:
            self.history.append(self.text)

    def remove_or_replace_last_words(self, new_word=''):
        if not self.last_pattern:
            return 'First find the word in the text.'
        self.save_state()
        case_sens = True if self.last_search_key.endswith('True False') else False
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
        return 'Words replaced.' if new_word else 'Words removed.'

    def search_word(self, word, for_gui=False):
        """Searches for a word in the text using cache."""
        pattern, text = self.get_pattern_and_text(word)
        search_key = f'{pattern} {self.case_sensitive} {self.smart_mode}'
        if search_key in self.search_cache:
            self.last_search_key = search_key
            self.last_pattern = pattern
            return self.search_cache[search_key][0], self.search_cache[search_key][1]
        all_rows_in_text = [row for row in text.split('\n') if row]
        all_orig_rows_in_text = [row for row in self.text.split('\n') if row]
        list_index = None
        for_index_gui = ''
        res = ''
        n_row = 0
        for row in all_rows_in_text:
            n_row += 1
            if re.findall(pattern, row):
                res += f'{n_row}: {all_orig_rows_in_text[n_row - 1]}\n\n'
                for_index_gui += f'{n_row}: {row}\n\n' if for_gui else ''
        if not res or not word:
            self.last_search_key = None
            self.last_pattern = None
            return f'"{word}" - not exist in text.' if word else 'Enter a word for search.', None
        if for_gui:
            match = re.finditer(pattern, for_index_gui)
            list_index = [(w.start(), w.end()) for w in match]
        if not self.redo_stack:
            self.save_cache(search_key, (res, list_index))
        self.last_search_key = search_key
        self.last_pattern = pattern
        return res, list_index

    def show_list_words(self):
        """Shows a list of unique words."""
        self.update_result_counter()
        return list(self.result_counter.keys())

    def __str__(self):
        """Generates a string with the analysis results."""
        self.update_result_counter()
        res = 'Analysis Results:\n'
        res += '\n'.join([f'"{key}" -> {self.result_counter[key]}' for key in self.result_counter])
        res += '\n\nAnalysis performed on: ' + self.datetime_created.strftime('%d %B %Y; %H:%M') + '\n'
        return res

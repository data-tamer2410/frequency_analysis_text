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


class AnalysisText:
    """A class representing text analysis."""

    def __init__(self, path):
        """Initializes with the path to the file."""
        self.path = Path(path)
        self.new_file = False
        self.case_sensitive = False
        self.smart_mode = False
        self.support_language = ('uk', 'ru', 'en')
        self.text = None
        self.result_counter = None
        self.datetime_created = None
        self.language = None
        self.search_cache = {}
        self.search_cache_keys = []

    def load_pickle_file(self):
        with open(self.path, 'rb') as file:
            obj = pickle.load(file)
            self.text = copy.deepcopy(obj.text)
            self.result_counter = copy.deepcopy(obj.result_counter)
            self.datetime_created = copy.deepcopy(obj.datetime_created)
            self.language = copy.deepcopy(obj.language)
            self.search_cache = copy.deepcopy(obj.search_cache)
            self.search_cache_keys = copy.deepcopy(obj.search_cache_keys)

    def load_json_file(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.text = copy.deepcopy(data['text'])
            self.result_counter = copy.deepcopy(data['result_counter'])
            self.datetime_created = datetime.datetime.strptime(copy.deepcopy(data['datetime_created']),
                                                               '%Y-%m-%d %H:%M:%S.%f')
            self.language = copy.deepcopy(data['language'])
            self.search_cache = copy.deepcopy(data['search_cache'])
            self.search_cache_keys = copy.deepcopy(data['search_cache_keys'])

    def load_txt_file(self):
        self.new_file = True
        with open(self.path, 'r', encoding='utf-8') as file:
            self.text = file.read()

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

    def analyze_txt_file(self):
        """Analyzes the text to determine word and number frequencies."""
        if self.new_file:
            pattern = r'\b\w+\b|\b\d+\b|\b\d+\.\d+\b'
            counter_text = Counter(re.findall(pattern, self.text))
            if not counter_text:
                raise EmptyFileError
            self.result_counter = dict(sorted(counter_text.items(), key=lambda item: item[0]))
            self.datetime_created = datetime.datetime.now()
            self.language, _ = langid.classify(self.text)

    def save_file_to_pickle(self):
        path, mess = self.get_path_to_save('.pkl')
        with open(path, 'wb') as file:
            pickle.dump(self, file)
        return mess

    def save_file_to_json(self):
        data = {'text': self.text,
                'result_counter': self.result_counter,
                'datetime_created': self.datetime_created.strftime('%Y-%m-%d %H:%M:%S.%f'),
                'language': self.language,
                'search_cache': self.search_cache,
                'search_cache_keys': self.search_cache_keys}
        path, mess = self.get_path_to_save('.json')
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return mess

    def get_path_to_save(self, suffix):
        """Saves the analysis results to a file."""
        file_name = self.path.stem
        path = f'{self.datetime_created.date()}_{file_name}{suffix}'
        count = 1
        while Path(path).exists():
            path = f'{self.datetime_created.date()}_{file_name}_{count:03}{suffix}'
            count += 1
        if count > 1:
            return path, 'Such a file may already exist, but it was still saved with a unique authenticator.'
        return path, 'File save.'

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

    def search_word(self, word):
        """Searches for a word in the text using cache."""
        pattern, text = self.get_pattern_and_text(word)
        search_key = f'{pattern} {self.case_sensitive} {self.smart_mode}'
        if search_key in self.search_cache:
            return self.search_cache[search_key]
        all_rows_in_text = text.split('\n')
        all_orig_rows_in_text = self.text.split('\n')
        res = ''
        n_row = 0
        for row in all_rows_in_text:
            n_row += 1
            if re.findall(pattern, row):
                res += f'{n_row}: {all_orig_rows_in_text[n_row - 1]}\n'
        if not res:
            return f'"{word}" - not exist in text.'
        self.save_cache(search_key, res)
        return res

    def show_list_words(self):
        """Shows a list of unique words."""
        return list(self.result_counter.keys())

    def __str__(self):
        """Generates a string with the analysis results."""
        res = 'Analysis Results:\n'
        res += '\n'.join([f'"{key}" -> {self.result_counter[key]}' for key in self.result_counter])
        res += '\n\nAnalysis performed on: ' + self.datetime_created.strftime('%d %B %Y; %H:%M') + '\n'
        return res

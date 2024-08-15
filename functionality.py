import pickle
from pathlib import Path
from collections import Counter
import copy
import datetime
import re


class EmptyFileError(Exception):
    def __init__(self):
        super().__init__('The file does not contain words or numbers.')


class ProgramState:
    def __init__(self):
        self.enter_new_file = True


class AnalysisText:
    def __init__(self, path):
        self.path = Path(path)
        self.case_sensitive = False
        self.smart_mode = False
        self.text = None
        self.result = None
        self.datetime_created = None
        self.search_cache = {}

    def load_text(self):
        if self.path.suffix in ('.pkl', '.pickle'):
            with open(self.path, 'rb') as f:
                obj = pickle.load(f)
                self.text = copy.deepcopy(obj.text)
                self.result = copy.deepcopy(obj.result)
                self.datetime_created = copy.deepcopy(obj.datetime_created)

        else:
            with open(self.path, 'r', encoding='utf-8') as f:
                self.text = f.read()

    def analyze_text(self):
        pattern = r'\b\w+\b|\b\d+\b|\b\d+\.\d+\b'
        counter_text = Counter(re.findall(pattern, self.text))
        if not counter_text:
            raise EmptyFileError
        self.result = dict(sorted(counter_text.items(), key=lambda item: item[0]))
        self.datetime_created = datetime.datetime.now()

    def save_text(self):
        file_name = self.path.stem
        path = f'{self.datetime_created.date()}_{file_name}.pkl'
        count = 1
        while Path(path).exists():
            path = f'{self.datetime_created.date()}_{file_name}_{count:03}.pkl'
            count += 1
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        if count > 1:
            return 'Such a file may already exist, but it was still saved with a unique authenticator.'
        return 'File save.'

    def search_word(self, word):
        word = word.lower() if not self.case_sensitive else word
        search_key = (word, self.case_sensitive, self.smart_mode)
        if search_key in self.search_cache:
            return self.search_cache[search_key]
        text = self.text.lower() if not self.case_sensitive else self.text
        all_rows_in_text = text.split('\n')
        all_orig_rows_in_text = self.text.split('\n')
        pattern = f'{re.escape(word)}' if self.smart_mode else f'\\b{re.escape(word)}\\b'
        res = ''
        n_row = 0
        for row in all_rows_in_text:
            orig_row = all_orig_rows_in_text[n_row]
            n_row += 1
            if re.findall(pattern, row):
                res += f'{n_row}: {orig_row}\n'
        if not res:
            return f'"{word}" - not exist in text.'
        self.search_cache[search_key] = res
        return res

    def show_list_words(self):
        return list(self.result.keys())

    def __str__(self):
        res = 'Analysis Results:\n'
        res += '\n'.join([f'"{key}" -> {self.result[key]}' for key in self.result])
        res += '\n\nAnalysis performed on: ' + self.datetime_created.strftime('%d %B %Y; %H:%M') + '\n'
        return res

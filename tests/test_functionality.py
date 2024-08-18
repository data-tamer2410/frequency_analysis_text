from frequency_analysis_text import (AnalysisText, show_info_commands, parse_input, EmptyFileError,
                                     InvalidFileFormatError, user_command_handler, ProgramState)
from pathlib import Path
from datetime import date


def test_show_info_commands():
    assert show_info_commands() == ("1. '!help' to show information about commands;\n"
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
                                    "17. '!close' to close the program.\n")


def test_parse_input():
    word = '  test '
    res = parse_input(word)
    assert res == ('test', [])


def test_load_empty_unavailable_format():
    x = AnalysisText('tests/texts/empty.txt')
    y = AnalysisText('tests/texts/unavailable_format.csv')
    try:
        x.load_file()
        y.load_file()
    except EmptyFileError as e:
        assert str(e) == 'The file does not contain words or numbers.'
    except InvalidFileFormatError as e:
        assert str(e) == 'Invalid file format.'


def test_lang_detected():
    obj_en = AnalysisText('tests/texts/text_en.txt')
    obj_uk = AnalysisText('tests/texts/text_uk.txt')
    obj_ru = AnalysisText('tests/texts/text_ru.txt')
    obj_de = AnalysisText('tests/texts/text_de.txt')

    [el.load_file() for el in (obj_en, obj_uk, obj_ru, obj_de)]

    assert (obj_en.language, obj_uk.language, obj_ru.language, obj_de.language) == ('en', 'uk', 'ru', 'de')


obj = AnalysisText('tests/texts/text_en.txt')
state = ProgramState()


def test_load_analyze_txt_file():
    assert not obj.new_file
    obj.load_file()
    assert obj.text
    assert not obj.result_counter
    assert obj.datetime_created
    assert obj.language == 'en'
    assert obj.new_file


def test_show_list_word():
    assert obj.show_list_words()


def test_user_command_handler_search_word_cache():
    user_command_handler('!enter_file', obj, state)
    assert state.enter_new_file
    user_command_handler('!case_sens_on', obj, state)
    assert obj.case_sensitive
    assert not obj.smart_mode
    assert obj.search_word('plAyEr') == '"plAyEr" - not exist in text.'
    assert not obj.search_cache_keys
    assert not obj.search_cache
    user_command_handler('!smart_mode_on', obj, state)
    assert obj.smart_mode
    assert not obj.case_sensitive
    assert obj.search_word('plAyEr') != '"player" - not exist in text.'
    key = obj.search_cache_keys[0]
    assert key == r'player False True'
    assert obj.search_cache[key]
    user_command_handler('!case_sens_on', obj, state)
    assert obj.case_sensitive
    assert not obj.smart_mode
    assert obj.search_word('player') != '"player" - not exist in text.'
    key = obj.search_cache_keys[1]
    assert key == r'\bplayer\b True False'
    assert obj.search_cache[key]
    user_command_handler('!case_sens_off', obj, state)
    assert not obj.case_sensitive
    assert not obj.smart_mode
    user_command_handler('!smart_mode_on', obj, state)
    user_command_handler('!smart_mode_off', obj, state)
    assert not obj.case_sensitive
    assert not obj.smart_mode
    assert obj.search_word('PlAyER') != '"player" - not exist in text.'
    key = obj.search_cache_keys[2]
    assert key == r'\bplayer\b False False'
    assert obj.search_cache[key]

    obj_ru = AnalysisText('tests/texts/text_ru.txt')
    obj_uk = AnalysisText('tests/texts/text_uk.txt')
    obj_ru.load_file()
    obj_uk.load_file()
    assert not all((obj_uk.smart_mode, obj_ru.smart_mode))
    assert not all((obj_uk.case_sensitive, obj_ru.case_sensitive))
    assert not all((obj_uk.search_cache, obj_ru.search_cache))
    assert not all((obj_uk.search_cache_keys, obj_ru.search_cache_keys))

    assert obj_uk.search_word('ГраВеЦь') != '"гравець" - not exist in text.'
    assert obj_ru.search_word('игРОк') != '"игрок" - not exist in text.'
    assert obj_uk.search_word('ГраВеЦь')
    assert obj_ru.search_word('игРОк')

    key = obj_uk.search_cache_keys[0]
    assert key == r'\bгравець\b False False'
    assert obj_uk.search_cache[key]

    key = obj_ru.search_cache_keys[0]
    assert key == r'\bигрок\b False False'
    assert obj_ru.search_cache[key]

    obj_uk.case_sensitive = True
    obj_ru.case_sensitive = True

    assert obj_uk.search_word('ГраВеЦь') == '"ГраВеЦь" - not exist in text.'
    assert obj_ru.search_word('игРОк') == '"игРОк" - not exist in text.'

    assert obj_uk.search_word('гравець') != '"гравець" - not exist in text.'
    assert obj_ru.search_word('игрок') != '"игрок" - not exist in text.'
    assert obj_uk.search_word('гравець')
    assert obj_ru.search_word('игрок')

    key = obj_uk.search_cache_keys[1]
    assert key == r'\bгравець\b True False'
    assert obj_uk.search_cache[key]

    key = obj_ru.search_cache_keys[1]
    assert key == r'\bигрок\b True False'
    assert obj_ru.search_cache[key]

    user_command_handler('!smart_mode_on', obj_uk, state)
    user_command_handler('!smart_mode_on', obj_ru, state)

    assert obj_uk.smart_mode
    assert obj_ru.smart_mode
    assert not obj_uk.case_sensitive
    assert not obj_ru.case_sensitive

    assert obj_uk.search_word('ГрАвцЕві') != '"гравцеві" - not exist in text.'
    assert obj_ru.search_word('иГроКАми') != '"игроками" - not exist in text.'
    assert obj_uk.search_word('ГрАвцЕві')
    assert obj_ru.search_word('иГроКАми')

    key = obj_uk.search_cache_keys[2]
    assert obj_uk.search_cache[key]

    key = obj_ru.search_cache_keys[1]
    assert obj_ru.search_cache[key]


def test_search_cache():
    assert obj.search_cache
    assert len(obj.search_cache) == len(obj.search_cache_keys)
    obj2 = AnalysisText('tests/texts/text_en.txt')
    obj2.load_file()
    obj2.search_word('Football')
    value = obj2.search_word('FooTBall')
    list_cache_values = list(obj2.search_cache.values())
    assert value in list_cache_values
    assert obj2.search_cache_keys[0] == r'\bfootball\b False False'
    for i in range(500):
        obj2.search_cache[i] = i
        obj2.search_cache_keys.append(i)

    assert len(obj2.search_cache) == 501
    assert len(obj2.search_cache_keys) == 501
    assert obj2.search_cache_keys[0] == r'\bfootball\b False False'
    assert obj2.search_word('player')
    assert obj2.search_word('player') != '"player" - not exist in text.'

    assert len(obj2.search_cache) == 501
    assert len(obj2.search_cache_keys) == 501
    assert obj2.search_cache_keys[0] == 0
    assert obj2.search_cache_keys[-1] == r'\bplayer\b False False'


def test_save_file_to_pickle_json():
    mess1 = obj.save_file_to_pickle()
    mess2 = obj.save_file_to_json()
    mess3 = obj.save_file_to_pickle()
    mess4 = obj.save_file_to_json()
    assert mess1, mess2 == ('File save.', 'File save.')
    mess = 'Such a file may already exist, but it was still saved with a unique authenticator.'
    assert mess3, mess4 == (mess, mess)


def test_load_file_from_pickle_json():
    f_json = AnalysisText(f'{date.today()}_text_en.json')
    f_pkl = AnalysisText(f'{date.today()}_text_en.pkl')
    f_json.load_file()
    f_pkl.load_file()
    assert (f_json.text, f_json.result_counter, f_json.datetime_created, f_json.language, f_json.search_cache,
            f_json.search_cache_keys) == (obj.text, obj.result_counter, obj.datetime_created, obj.language,
                                          obj.search_cache, obj.search_cache_keys)
    assert (f_pkl.text, f_pkl.result_counter, f_pkl.datetime_created, f_pkl.language, f_pkl.search_cache,
            f_pkl.search_cache_keys) == (obj.text, obj.result_counter, obj.datetime_created, obj.language,
                                         obj.search_cache, obj.search_cache_keys)


def test_clear():
    Path(f'{str(date.today())}_text_en.json').absolute().unlink()
    Path(f'{str(date.today())}_text_en.pkl').absolute().unlink()
    Path(f'{str(date.today())}_text_en_001.json').absolute().unlink()
    Path(f'{str(date.today())}_text_en_001.pkl').absolute().unlink()

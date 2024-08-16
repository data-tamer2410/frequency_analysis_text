# Text Analysis Program

This project is a comprehensive tool designed for analyzing text files. It supports multiple languages and provides various features, including word search, case sensitivity control, smart mode for flexible searching, and options to save analysis results in different formats.

## Features

- **Load and Analyze Text Files**: Supports `.txt`, `.json`, and `.pickle` formats.
- **Search Functionality**: Search for words in the text with options for case sensitivity and smart mode.
- **Smart Mode**: Allows searching for words not only as exact matches but also considering different forms (e.g., plural, past tense).
- **Case Sensitivity**: Toggle case sensitivity for search results.
- **Save Results**: Save analysis results in `.json` or `.pickle` formats.

## Commands

- `__help__`: Show information about available commands.
- `__enter_file__`: Enter a new file for analysis.
- `__list_words__`: Display all unique words found in the text.
- `__case_sens__`: Show the current case sensitivity status.
- `__case_sens_on__`: Enable case sensitivity.
- `__case_sens_off__`: Disable case sensitivity.
- `__smart_mode__`: Show the current smart mode status.
- `__smart_mode_on__`: Enable smart mode.
- `__smart_mode_off__`: Disable smart mode.
- `__close_program__`: Close the program.
- `__save_to_pickle__`: Save analysis results in a `.pickle` file.
- `__save_to_json__`: Save analysis results in a `.json` file.

## How to Run

1. Clone the repository.
2. Install required dependencies (if any).
3. Run the `main.py` script.
4. Follow the prompts to load a file and perform text analysis.

## Requirements

- Python 3.8+
- External libraries: `pymorphy2`, `nltk`, `langid`

## Example Usage

```python
python main.py

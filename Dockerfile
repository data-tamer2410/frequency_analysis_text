FROM python:3.10-slim
LABEL authors="Professional"

WORKDIR /frequency_analysis_text
COPY . /frequency_analysis_text

RUN pip install poetry && poetry install

CMD ["poetry", "run", "python", "frequency_analysis_text/main.py"]

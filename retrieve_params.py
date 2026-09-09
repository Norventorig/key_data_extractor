from openai import OpenAI
import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("api_key"),
)


class Report(BaseModel):
    pass


def promt_init(document: str, data_to_extract: str):
    return (f"Роль: Ты опытный Документовед. "
            f"Контекст: Мы читаем документы по горнодобывающим работам. "
            f"Задача: Извлеки данные: {data_to_extract}. "
            f"Формат вывода: строго JSON без лишних слов в выводе. "
            f"Документ: {document}")


def parse_llm_json(function):
    def wrapper(*args, **kwargs):
        content = function(*args, **kwargs)

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            return json.loads(content)

        except json.JSONDecodeError as e:
            print("Ошибка JSON:", e)

            with open("broken_response.txt", "w", encoding="utf-8") as f:
                f.write(content)

            return {}

    return wrapper


@parse_llm_json
def make_request(promt):
    response = client.chat.completions.create(
        model="baidu/cobuddy:free",
        response_format={"type": "json_object"},
        messages=[{"role": "user",
                   "content": promt}],
        extra_body={"reasoning": {"enabled": True}})

    return response.choices[0].message.content


def check_params(data):
    try:
        Report(**data)

    except Exception as e:
        print("Отсутствуют некоторые записи!")
        print(e)


def save(data):
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main(document: str, data_to_extract: str):
    request = promt_init(document=document, data_to_extract=data_to_extract)
    if not request:
        print('Работа модуля прервана!')
        return

    result = make_request(promt=request)
    if not result:
        print(f'Не удалось получить ответ от модели')
        print('Работа модуля прервана!')
        return

    check_params(data=result)

    save(data=result)
    print("JSON успешно сохранен")

    print('РАБОТА МОДУЛЯ ИЗВЛЕЧЕНИЯ ПАРАМЕТРОВ ЗАВЕРШЕНА!')


if __name__ == '__main__':
    doc_path = input("Введите текст докумета для анализа:\n")
    doc_params = input("Введите параметры документа через запятую:\n")

    print(main(document=doc_path, data_to_extract=doc_params))

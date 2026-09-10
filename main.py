from retrieve_params import main as retrieve_params
from retrieve_text import main as retrieve_text


def main(path: str, data_to_extract: str):
    text = retrieve_text(path=path)
    retrieve_params(document=text, data_to_extract=data_to_extract)
    print('ЗАВЕРШЕНО ВСЕ!')


if __name__ == "__main__":
    doc_path = input('Введите путь к документу: ')
    doc_params = input("Перечислите ключевые параметры через запятую: ")

    main(path=doc_path, data_to_extract=doc_params)

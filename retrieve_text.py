from docx import Document
import os


def extract_text_from_docx(path: str=None) -> str | None:
    """Extract the plaintext from a .docx file.
    Parameters:
         path (str): The string representing location of your document.
    Returns:
        str: Extracted plaintext from the given file."""

    if not path:
        raise ValueError('Путь не указан')

    if not os.path.exists(path):
        raise FileExistsError('Файла по данному пути нет')

    if os.path.splitext(path)[1] != '.docx':
        raise TypeError('Переданный аргумент должен быть типа ".docx"')

    doc = Document(path)

    full_text = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        if text:
            full_text.append(text)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text.strip()

                if text:
                    full_text.append(text)

    return "\n".join(full_text)


if __name__ == "__main__":
    input_path = input("Введите путь к .docx файлу: ")

    print(F'Содержание файла {input_path}: \n\n')
    print(extract_text_from_docx(path=input_path))

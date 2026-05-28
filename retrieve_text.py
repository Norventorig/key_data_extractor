from openai import OpenAI
import os
import base64
import fitz
from docx import Document
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("api_key"))


def encode_image_to_base64(path: str) -> str | None:
    """
    Encode an Image file into a Base64 string
        Parameters:
             path (str): The string representing location of your document.
        Returns:
            str: Decoded version of given file.
    """

    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def image_to_text(img_url: str, img_type: str) -> str:
    """
    Extract text from an image
    Parameters:
        img_url (str): The url of image
        img_type (str): The type of image
    Returns:
        str: The extracted text
    """

    data_url = f"data:image/{img_type};base64,{img_url}"

    response = client.chat.completions.create(model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                                            messages=[{"role": "user",
                                                       "content": [{"type": "text",
                                                                    "text": "Extract all text from this image thoroughly. "
                                                                            "Do NOT miss any words, headings, lists, faint text, "
                                                                            "or text near edges. Maintain the original reading order."
                                                                            "Don't need to give any explanation, just provide the extracted text."},

                                                                   {"type": "image_url",
                                                                    "image_url": {"url": data_url}}]}],
    extra_body={"reasoning": {"enabled": False}})

    return response.choices[0].message.content


def read_pdf(path: str, zoom: float = 3.0) -> str:
    """
    Read a PDF file and return its content
    Parameters:
        path (str): The path of your PDF file
        zoom (float, optional): The zoom level. Defaults to 3.0.
    Returns:
        str: The contents of your PDF file
    """

    doc = fitz.open(path)
    result = ''

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)

        image_bytes = pix.tobytes("png")
        img_url = base64.b64encode(image_bytes).decode("utf-8")
        img_type = 'png'

        result += image_to_text(img_url=img_url, img_type=img_type)

    doc.close()

    return result


def read_png_or_jpg(path: str) -> str:
    img_url = encode_image_to_base64(path=path)
    img_type = os.path.splitext(path)[1]

    return image_to_text(img_url=img_url, img_type=img_type)


def read_docx(path: str=None) -> str | None:
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


def main(path: str) -> str|None:
    if not os.path.exists(path):
        raise FileExistsError('Изображения по данному пути нет')

    if os.path.splitext(path)[1] in ('.jpeg', '.jpg', '.png'):
        return read_png_or_jpg(path=path)

    elif os.path.splitext(path)[1] == '.pdf':
        return read_pdf(path=path)

    elif os.path.splitext(path)[1] == '.docx':
        return read_docx(path=path)

    else:
        raise TypeError("Переданный аргумент должен быть типа ('.jpeg', '.jpg', '.png', '.pdf', '.docx')")

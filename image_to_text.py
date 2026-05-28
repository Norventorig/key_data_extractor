from openai import OpenAI
import os
import base64
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("api_key"))


def encode_image_to_base64(image_path: str) -> str|None:
    """Encode an Image file into a Base64 string
        Parameters:
             image_path (str): The string representing location of your document.
        Returns:
            str: Decoded version of given file."""

    if not os.path.exists(image_path):
        raise FileExistsError('Изображения по данному пути нет')

    if os.path.splitext(image_path)[1] not in ('.jpeg', '.jpg', '.png'):
        raise TypeError('Переданный аргумент должен быть типа ".docx"')

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def main(img_path: str) -> str:
    """Extract text from an Image URL
    Parameters:
        img_path (str): The string representing location of your document.
    Returns:
        str: Extracted text"""

    img_url = encode_image_to_base64(image_path=img_path)
    img_type = os.path.splitext(img_path)[1][1:]

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



if __name__ == "__main__":
    image_path = input("Введите путь до картинки: ")
    result = main(image_path)
    print(result)

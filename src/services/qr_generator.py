from io import BytesIO

import qrcode
import aiogram


def generate_qrcode(text):
    buffer = BytesIO()
    qrcode.make(text).save(buffer)
    buffer.seek(0)
    return aiogram.types.InputFile(buffer, f'{text}.png')

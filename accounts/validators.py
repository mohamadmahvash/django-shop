from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import uuid
from PIL import Image, UnidentifiedImageError
from io import BytesIO

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_FORMATS = ['PNG', 'JPG', 'JPEG', 'WEBP']


def avatar_upload_path_validator(instance, filename):
    ext = filename.split('.')[-1].lower()
    if ext not in ALLOWED_FORMATS:
        ext = ['jpg']
    return f"avatars/{uuid.uuid4()}.{ext}"


def avatar_validator(file):
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("file size must be under 2MB")

    try:
        img = Image.open(file)
        img.verify()
    except (OSError, UnidentifiedImageError):
        raise ValidationError("file must be an image")
    finally:
        file.seek(0)

    img = Image.open(file)
    if img.format not in ALLOWED_FORMATS:
        raise ValidationError("file format must be one of {}".format(ALLOWED_FORMATS))

    width, height = img.size
    if width > 1000 and height > 1000:
        raise ValidationError("width and height must be less than 1000px")

    file.seek(0)


def process_image_validator(file):
    try:
        img = Image.open(file)

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        img.thumbnail((512, 512))

        output = BytesIO()  # save img on RAM
        img.save(output, format='JPEG', quality=85, optimize=True)

        output.seek(0)

        filename = f"{uuid.uuid4()}.jpg"
        return ContentFile(output.read(),name=filename)

    except Exception:
        raise ValidationError("failed to process image")

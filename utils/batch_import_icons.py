from .file_to_string import file_to_string
import os


def batch_import_icons(path, db, Icon):
    for file_name in os.listdir(path):
        image_string = file_to_string(os.path.join(path, file_name))
        icon = Icon(title=file_name, file=image_string, file_name=file_name)
        db.add(icon)

import json
import os
import pathlib
import sys
from typing import Any

from langchain.memory import FileChatMessageHistory
from langchain_core.messages import messages_to_dict, BaseMessage

from src import settings


class JsonImporter:

    def __init__(self, data_dir: pathlib.Path = settings.DATA_DIR):
        self.data_dir = data_dir / 'plays'
        if not self.data_dir.exists():
            os.mkdir(self.data_dir)

    def load(self, filename: str):
        file_path = self.data_dir / filename
        with open(str(file_path), 'r') as file:
            data = json.load(file)
        return data

    def export(self, filename: str, data):
        file_path = self.data_dir / filename
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def delete(self, filename):
        os.remove(self.data_dir / filename)


class FileHistory(FileChatMessageHistory):
    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in the local file"""
        messages = messages_to_dict(self.messages)
        messages.append(messages_to_dict([message])[0])
        self.file_path.write_text(json.dumps(messages, ensure_ascii=False, indent=4))


def get_list(obj: Any):
    if not isinstance(obj, list):
        return [obj]
    return obj
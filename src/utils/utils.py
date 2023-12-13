import json
import os
import pathlib
import sys
from typing import Any, List, Sequence

from langchain.memory import FileChatMessageHistory
from langchain_core.messages import messages_to_dict, BaseMessage, ChatMessage
from pydantic.v1 import Field

from src import settings


class JsonImporter:

    def __init__(self, namespace: str, filename='play.json'):
        self.data_dir = settings.DATA_DIR / namespace / filename
        self.ensure_ascii = False
        self.encoding = 'utf-8'
        if not self.data_dir.exists():
            os.mkdir(self.data_dir)

    def load(self):
        with open(str(self.data_dir), 'r', encoding=self.encoding) as file:
            data = json.load(file)
        return data

    def export(self, data):
        with open(str(self.data_dir), 'w', encoding=self.encoding) as file:
            json.dump(data, file, ensure_ascii=self.ensure_ascii, indent=4)

    def delete(self):
        os.remove(self.data_dir)


class FileHistory(FileChatMessageHistory):

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in the local file"""
        messages = messages_to_dict(self.messages)
        messages.append(messages_to_dict([message])[0])
        self.file_path.write_text(json.dumps(messages, ensure_ascii=False, indent=4))


class FileHistoryProxy(FileHistory):
    messages: List[ChatMessage] = Field(default_factory=list)

    def clear_buffer(self):
        self.messages = []

    def add_messages(self, messages: List[ChatMessage]) -> None:
        messages = messages_to_dict(messages)
        with self.file_path.open(mode='a') as file:
            for message in messages:
                file.write(json.dumps(message, ensure_ascii=False))


def get_event_buffer_string(messages: Sequence[BaseMessage]):
    string_messages = []
    for m in messages:
        role = m.role
        message = f"[{role}]-{m.content}"
        string_messages.append(message)
    return "\n".join(string_messages)


def get_list(obj: Any):
    if not isinstance(obj, list):
        return [obj]
    return obj
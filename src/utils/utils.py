import json
import os
import pathlib
import sys
import typing
from typing import Any, List, Sequence

from langchain.memory import FileChatMessageHistory
from langchain_core.messages import messages_to_dict, BaseMessage, ChatMessage, get_buffer_string
from pydantic.v1 import Field

from src import settings

if typing.TYPE_CHECKING:
    from src.modules.memory import ContextMessage


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
        messages = contexts_to_dict(self.messages)
        messages.append(contexts_to_dict([message])[0])
        self.file_path.write_text(json.dumps(messages, ensure_ascii=False, indent=4))


class FileHistoryProxy(FileHistory):
    messages: List['ContextMessage'] = Field(default_factory=list)

    def clear_buffer(self):
        self.messages = []

    def add_messages(self, messages: List['ContextMessage']) -> None:
        messages = contexts_to_dict(messages)
        with self.file_path.open(mode='a') as file:
            for message in messages:
                file.write(json.dumps(message, ensure_ascii=False))


def get_event_buffer_string(
        messages: Sequence[typing.Union['ContextMessage', 'ChatMessage']]
):
    string_messages = []
    first_chat = False
    for m in messages:
        if isinstance(m, ContextMessage):
            event = m.event
            message = f"[{event}]-{m.content}"
        else:
            if first_chat is False:
                string_messages.append(f"以下是主角和{m.role}的对话:")
                first_chat = True
            message = f"{m.role}: {m.content}"
        string_messages.append(message)
    return "\n".join(string_messages)


def context_to_dict(message: BaseMessage) -> dict:
    return message.dict(exclude={'type'})


def contexts_to_dict(messages: List[BaseMessage]) -> List[dict]:
    return [message.dict(exclude={'type'}) for message in messages]


def get_list(obj: Any):
    if not isinstance(obj, list):
        return [obj]
    return obj


def event_choice(choice_map: dict):
    import random

    branches, weights = list(zip(*choice_map.items()))
    random_num = random.uniform(0, sum(weights))
    # 根据随机数选择分支
    total = 0
    chosen_branch = None
    for i, weight in enumerate(weights):
        total += weight
        if random_num <= total:
            chosen_branch = branches[i]
            break
    assert chosen_branch
    return chosen_branch

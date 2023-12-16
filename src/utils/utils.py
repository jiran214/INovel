import json
import os
from typing import Dict, Union
import itertools

import time
from datetime import timedelta, datetime
from collections import deque
from typing import Any, List, Sequence

from langchain.memory import FileChatMessageHistory
from langchain_core.messages import messages_to_dict, BaseMessage, ChatMessage


from src import settings
from src.schemas import ContextMessage


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
        self.file_path.write_text(json.dumps(messages, ensure_ascii=False, indent=2))


class FileHistoryProxy(FileHistory):

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._messages: List['ContextMessage'] = []

    @property
    def messages(self) -> List['ContextMessage']:
        return self._messages

    def clear_buffer(self):
        self._messages = []

    def add_messages(self, messages: List['ContextMessage']) -> None:
        messages = contexts_to_dict(messages)
        with self.file_path.open(mode='a') as file:
            for message in messages:
                file.write(json.dumps(message, ensure_ascii=False))


class APIKeyQueue:
    def __init__(self, keys, times, minute=0, seconds=0, sleep_time=2, callback=None, raise_exception=False):
        """times/minute or seconds/minute"""
        assert minute or seconds
        self.minute = minute
        self.seconds = seconds
        self.times = times
        self.callback = callback
        self.raise_exception = raise_exception
        self.sleep_time = sleep_time
        self.key_counters: Dict[str, deque] = {key: deque(maxlen=times) for key in keys}
        self.key_num = len(keys)

    def _get_next_key(self):
        fail_times = 0
        for key in itertools.cycle(self.key_counters.keys()):
            key_counter = self.key_counters[key]
            now = datetime.now()
            if len(key_counter) < self.times or now - key_counter[-1] > timedelta(minutes=self.minute, seconds=self.seconds):
                key_counter.appendleft(now)
                yield key
                fail_times = 0
                continue
            fail_times += 1
            if fail_times > self.key_num:
                if self.raise_exception:
                    raise RuntimeError
                self.callback()
                time.sleep(self.sleep_time)

    def get_next_key(self):
        for key in self._get_next_key():
            return key


def get_event_buffer_string(
        messages: Sequence[Union['ContextMessage', 'ChatMessage']]
):
    string_messages = []
    first_chat = False
    for m in messages:
        if isinstance(m, ContextMessage):
            message = m.format_line()
        else:
            if first_chat is False:
                string_messages.append(f"以下是主角和{m.role}的对话:")
                first_chat = True
            message = f"{m.role}: {m.content}"
        string_messages.append(message)
    return "\n".join(string_messages)


def context_to_dict(message: BaseMessage) -> dict:
    return message.dict()


def contexts_to_dict(messages: List[BaseMessage]) -> List[dict]:
    return [message.dict() for message in messages]


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

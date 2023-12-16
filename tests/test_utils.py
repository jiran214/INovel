#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib

from src import schemas
from src.schemas import ContextMessage
from src.utils import utils


def test_event_choice():
    event_choice = {'option1': 20.0, 'option2': 100.99, 'option3': 500.123}
    choices = []
    for _ in range(1000):
        choices.append(utils.event_choice(event_choice))
    print('\n', choices)
    assert choices.count('option3') > choices.count('option2') > choices.count('option1')


def test_schemas():
    assert 'generator_func' not in schemas.Dialog.schema()
    assert 'generator_func' not in schemas.Action.schema()


def test_FileHistoryProxy():
    filepath = pathlib.Path('./test.json')
    file = utils.FileHistoryProxy(str(filepath))
    file.messages.extend([ContextMessage(event='1', content='1')])
    messages = file.messages
    messages.pop(0)
    assert file.messages == file._messages == []
    os.remove(str(filepath))
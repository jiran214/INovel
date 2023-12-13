#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.utils import utils


def test_event_choice():
    event_choice = {'option1': 20.0, 'option2': 100.99, 'option3': 500.123}
    choices = []
    for _ in range(1000):
        choices.append(utils.event_choice(event_choice))
    print('\n', choices)
    assert choices.count('option3') > choices.count('option2') > choices.count('option1')

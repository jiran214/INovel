import pathlib
from pprint import pprint

from src.modules.play import NovelSettings
from src.prompts import INovelPrompt, dialog_prompt
from src.utils.utils import JsonImporter

settings_vars = [
    'title',
    'background',
    'characters',
    'current_step',
    'total_steps',
    'goal',
    'play_context',
    'user_interaction'
]

play = NovelSettings(**JsonImporter(data_dir=pathlib.Path(__file__).parent).load('test_play.json'))


def test_dialog_prompt():
    input_vars = ['language']
    assert set(dialog_prompt.input_variables) == set(input_vars)
    prompt = dialog_prompt.format(language='中文')
    assert prompt
    print('\n', prompt)


def test_dialog_driven_prompt():
    input_vars = settings_vars + ['language']
    assert set(INovelPrompt.dialog_driven_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.dialog_driven_prompt.format(**play.get_inputs())
    print('\n', prompt)
    assert prompt


def test_action_driven_prompt():
    input_vars = settings_vars + ['language', 'option_num']
    assert set(INovelPrompt.action_driven_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.action_driven_prompt.format(**play.get_inputs())
    print('\n', prompt)
    assert prompt


def test_novel_end_prompt():
    input_vars = settings_vars + []
    assert set(INovelPrompt.novel_end_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.novel_end_prompt.format(**play.get_inputs())
    print('\n', prompt)
    assert prompt


def test_charactor_chat_prompt():
    input_vars = ['story', 'scene', 'history', 'input', 'charactor_name']
    assert set(INovelPrompt.charactor_chat_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.charactor_chat_prompt.format(**{key: key for key in input_vars})
    print('\n', prompt)
    assert prompt
import pathlib
from pprint import pprint

from src.modules.play import NovelSettings
from src.prompts import INovelPrompt, dialog_prompt
from src.utils.utils import JsonImporter

common_vars = [
    'language',
    'total_chapters',
    'current_chapter',
    'play_context_window',
    'play_context_memory',
    # 'format_instructions'
]

start_vars = [
    'title',
    'description',
    'characters',
    'goal',
]

play = NovelSettings(**JsonImporter('test').load())


def test_novel_start_prompt():
    input_vars = common_vars + start_vars
    assert set(INovelPrompt.novel_start_prompt.input_variables) == set(input_vars)
    print(input_vars)
    prompt = INovelPrompt.novel_start_prompt.format(**play.get_inputs())
    print('\n', prompt)
    assert prompt


def test_dialog_driven_prompt():
    input_vars = common_vars + ['scene', 'characters']
    assert set(INovelPrompt.dialog_driven_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.dialog_driven_prompt.format(**play.get_inputs())
    print('\n', prompt)
    assert prompt


def test_action_driven_prompt():
    input_vars = common_vars + ['option_num', 'scene', 'relate_characters']
    assert set(INovelPrompt.action_driven_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.action_driven_prompt.format(**play.get_inputs())
    print('\n', prompt)
    assert prompt


def test_novel_end_prompt():
    input_vars = common_vars + ['scene', 'relate_characters']
    assert set(INovelPrompt.novel_end_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.novel_end_prompt.format(**play.get_inputs())
    print('\n', prompt)
    assert prompt


def test_character_chat_prompt():
    input_vars = common_vars + ['character', 'scene', 'input', 'history', 'relate_characters']
    assert set(INovelPrompt.character_chat_prompt.input_variables) == set(input_vars)
    prompt = INovelPrompt.character_chat_prompt.format(**{key: key for key in input_vars})
    print('\n', prompt)
    assert prompt
from src.prompts import INovelPrompt

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


def test_dialog_driven_prompt():
    input_vars = settings_vars + ['language']
    assert set(INovelPrompt.dialog_driven_prompt.input_variables) == set(input_vars)


def test_action_driven_prompt():
    input_vars = settings_vars + ['language', 'option_num']
    assert set(INovelPrompt.action_driven_prompt.input_variables) == set(input_vars)


def test_novel_end_prompt():
    input_vars = settings_vars + []
    assert set(INovelPrompt.novel_end_prompt.input_variables) == set(input_vars)


def test_charactor_chat_prompt():
    input_vars = ['story', 'scene', 'history', 'input', 'charactor_name']
    assert set(INovelPrompt.charactor_chat_prompt.input_variables) == set(input_vars)
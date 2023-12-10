from langchain_core.prompts import (
    PipelinePromptTemplate,
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate, HumanMessagePromptTemplate
)

from src.modules.brain import parsers
from src.prompts.interaction import DIALOG_PROMPT, ACTION_PROMPT, CHAT_PROMPT
from src.prompts.novel_life import SETTINGS_PROMPT, END_PROMPT
from src.prompts.system import SYSTEM_PROMPT

MOVES_ON_PROMPT = (
    '{novel_settings}\n'
    '{instruction}'
)

novel_settings_prompt = PromptTemplate.from_template(SETTINGS_PROMPT)
novel_end_prompt = PromptTemplate.from_template(END_PROMPT)
action_prompt = PromptTemplate.from_template(ACTION_PROMPT)
dialog_prompt = PromptTemplate.from_template(DIALOG_PROMPT)
moves_on_chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(MOVES_ON_PROMPT),
])


def get_pipeline_prompt(interaction, parser=None):
    partial_variables = {}
    if parser:
        partial_variables = {"format_instructions": parser.get_format_instructions()}
    return PipelinePromptTemplate(
        final_prompt=moves_on_chat_prompt,
        pipeline_prompts=[
            ("novel_settings", novel_settings_prompt),
            ("instruction", interaction)
        ],
        partial_variables=partial_variables,
    )


class INovelPrompt:
    dialog_driven_prompt = get_pipeline_prompt(dialog_prompt, parsers.dialog_parser)
    action_driven_prompt = get_pipeline_prompt(action_prompt, parsers.action_parser)
    novel_end_prompt = get_pipeline_prompt(novel_end_prompt)
    charactor_chat_prompt = ChatPromptTemplate.from_template(CHAT_PROMPT)


__all__ = [
    'INovelPrompt'
]
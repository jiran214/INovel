from langchain_core.prompts import (
    PipelinePromptTemplate,
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate, HumanMessagePromptTemplate
)

from src.modules import parsers
from src.prompts.interaction import DIALOG_PROMPT, ACTION_PROMPT, CHAT_PROMPT
from src.prompts.novel_life import SETTINGS_PROMPT, END_PROMPT
from src.prompts.system import SYSTEM_PROMPT

MOVES_ON_PROMPT = (
    '{novel_settings}\n'
    '{instruction}'
)

novel_settings_prompt = PromptTemplate.from_template(SETTINGS_PROMPT)
novel_end_prompt = PromptTemplate.from_template(END_PROMPT)
action_prompt = PromptTemplate.from_template(
    ACTION_PROMPT, partial_variables={"format_instructions": parsers.action_parser.get_format_instructions()})
dialog_prompt = PromptTemplate.from_template(
    DIALOG_PROMPT, partial_variables={"format_instructions": parsers.dialog_parser.get_format_instructions()}
)
moves_on_chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(MOVES_ON_PROMPT),
])


def get_pipeline_prompt(interaction):
    return PipelinePromptTemplate(
        final_prompt=moves_on_chat_prompt,
        pipeline_prompts=[
            ("novel_settings", novel_settings_prompt),
            ("instruction", interaction)
        ]
    )


class INovelPrompt:
    dialog_driven_prompt = get_pipeline_prompt(dialog_prompt)
    action_driven_prompt = get_pipeline_prompt(action_prompt)
    novel_end_prompt = get_pipeline_prompt(novel_end_prompt)
    charactor_chat_prompt = ChatPromptTemplate.from_template(CHAT_PROMPT)  # 添加主角在人物介绍


__all__ = [
    'INovelPrompt'
]
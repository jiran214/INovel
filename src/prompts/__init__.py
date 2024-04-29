from langchain.output_parsers.format_instructions import PYDANTIC_FORMAT_INSTRUCTIONS
from langchain_core.prompts import (
    PipelinePromptTemplate,
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate, HumanMessagePromptTemplate
)

from src.modules import parsers
from src.prompts.interaction import DIALOG_PROMPT, ACTION_PROMPT, CHAT_PROMPT
from src.prompts.novel_life import PLAY_PROMPT, END_PROMPT, START_PROMPT, PROCESS_PROMPT
from src.prompts.system import SYSTEM_PROMPT, FINAL_PROMPT, COMMON_PROMPT
from src.prompts.utils import PYDANTIC_INSTRUCTIONS
from src.utils.prompt import temple

play_prompt = temple(PLAY_PROMPT)
novel_process_prompt = temple(PROCESS_PROMPT)
novel_start_prompt = temple(START_PROMPT)
novel_end_prompt = temple(END_PROMPT)
action_prompt = temple(ACTION_PROMPT)
dialog_prompt = temple(DIALOG_PROMPT)
chat_prompt = temple(CHAT_PROMPT)


final_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(FINAL_PROMPT),
])


def pipeline(novel_settings, interaction, parser: parsers.PydanticParser=""):
    return PipelinePromptTemplate(
        final_prompt=final_prompt,
        pipeline_prompts=[
            ("novel_settings", novel_settings),
            ("common_settings", PromptTemplate.from_template(
                COMMON_PROMPT,
                partial_variables={
                    "format_instructions": parser and PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=parser.schema_instruct)
                }
            )),
            ("instruction", interaction)
        ]
    )


class INovelPrompt:
    novel_start_prompt = pipeline(play_prompt, novel_start_prompt, parsers.play_parser)
    dialog_driven_prompt = pipeline(novel_process_prompt, dialog_prompt, parsers.dialog_parser)
    action_driven_prompt = pipeline(novel_process_prompt, action_prompt, parsers.action_parser)
    novel_end_prompt = pipeline(novel_process_prompt, novel_end_prompt, parsers.result_parser)
    character_chat_prompt = pipeline(novel_process_prompt, chat_prompt)


__all__ = [
    'INovelPrompt'
]


if __name__ == '__main__':
    print(INovelPrompt.novel_start_prompt)
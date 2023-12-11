import json
from typing import List, Union
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers.format_instructions import PYDANTIC_FORMAT_INSTRUCTIONS
from pydantic.v1 import BaseModel, Field
from src.utils import enums


class PydanticParser(PydanticOutputParser):

    def get_format_instructions(self) -> str:
        schema = self.pydantic_object.schema()

        # Remove extraneous fields.
        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema, ensure_ascii=False)
        return PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str)


class AIInteraction(BaseModel):
    story: str = Field(description='之后的剧情发展')
    scene: str = Field(description='当前剧情的场景')
    event: enums.Event


class Dialog(AIInteraction):
    character_name: str = Field(description='选择的人物名称')
    event: enums.Event = enums.Event.dialog


class Action(AIInteraction):
    options: List[str] = Field(description='为玩家生成，决定故事的发展')
    event: enums.Event = enums.Event.action


class UserInteraction(BaseModel):
    interaction_in: Union[Dialog, Action]
    interaction_out: str

    @property
    def prompt(self) -> str:
        if isinstance(self.interaction_in, Action):
            return f"选择剧情选项:{self.interaction_out}"
        elif isinstance(self.interaction_in, Dialog):
            return f"和角色<{self.interaction_in.character_name}>对话:\n{self.interaction_out}"


dialog_parser = PydanticParser(pydantic_object=Dialog)
action_parser = PydanticParser(pydantic_object=Action)
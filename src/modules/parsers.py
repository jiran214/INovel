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


class Interaction(BaseModel):
    story: str = Field(description='之后的剧情发展')


class Dialog(Interaction):
    scene: str = Field(description='当前剧情的场景')
    relate_characters: List[str] = Field(description='关联角色名称')


class Result(Interaction):
    pass


class Action(Interaction):
    scene: str = Field(description='当前剧情的场景')
    characters: List[str] = Field(description='关联角色名称')
    options: List[str] = Field(description='为玩家生成，决定故事的发展')


dialog_parser = PydanticParser(pydantic_object=Dialog)
action_parser = PydanticParser(pydantic_object=Action)
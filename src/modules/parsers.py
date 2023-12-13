import json
from langchain.output_parsers import PydanticOutputParser

from src.schemas import PlayParagraph, Dialog, Action, Result


class PydanticParser(PydanticOutputParser):

    @property
    def schema_instruct(self) -> str:
        schema = self.pydantic_object.schema()

        # Remove extraneous fields.
        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema, ensure_ascii=False)
        return schema_str


play_parser = PydanticParser(pydantic_object=PlayParagraph)
dialog_parser = PydanticParser(pydantic_object=Dialog)
action_parser = PydanticParser(pydantic_object=Action)
result_parser = PydanticParser(pydantic_object=Result)
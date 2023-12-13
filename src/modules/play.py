from typing import List, Optional
from pydantic import BaseModel, Field

from src.utils.utils import JsonImporter


class Character(BaseModel):
    name: str
    description: str


class NovelSettings(BaseModel):
    namespace = Field(description="命名空间")
    title: str = Field(description="故事标题")
    background: str = Field(description="故事背景")
    characters: List[Character] = Field(description="人物角色")
    goal: str = Field(description="主角目标")
    total_steps: int = Field(default=10, description="故事时长")
    option_num: int = Field(default=3, description="交互式剧情选项数量")
    language: str = Field(default='中文')

    """动态"""
    current_step: int = Field(default=1, description="当前进度")
    relate_characters: List[str] = Field(default=[], description="涉及人物")
    scene: Optional[str] = Field(default=None, description="场景")
    play_context_window: str = Field(default='暂无', description="剧情")
    play_context_memory: str = Field(default='暂无', description="关联剧情")

    def get_inputs(self):
        return self.model_dump()

    @classmethod
    def load_json(cls, namespace):
        data_dict = JsonImporter(namespace).load()
        return cls(**data_dict)

    def reset(self):
        self.current_step = 1
        self.relate_characters = []
        self.scene = '暂无'
        self.play_context_window = '暂无'
        self.play_context_memory = '暂无'
        self.export_json()

    def export_json(self):
        JsonImporter(self.namespace).export(self.model_dump())
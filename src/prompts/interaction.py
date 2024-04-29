ACTION_PROMPT = """## 指令
请续写故事，为玩家提供{option_num}个交互式选项，推进剧情。"""


DIALOG_PROMPT = """## 指令
请续写故事，必须从{characters}选择一个角色，请扮演该角色和玩家对话，推进剧情。"""


CHAT_PROMPT = """## 判断对话终止条件
1. 玩家想结束对话
2. 对话偏离剧情
3. 对话轮数超过12轮

## 对话终止执行
当对话结束，在末尾加上标识符 /stop，注意未结束时不能加该标识

## Current conversation
The following is a friendly conversation between 玩家 and {character}. 
{history}
玩家: {input}
{character}: """
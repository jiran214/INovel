ACTION_PROMPT = """## 指令
为玩家提供{option_num}个交互式选项，并续写剧情。"""


DIALOG_PROMPT = """## 指令
选择一个人物，该人物将会与玩家对话，推进剧情。"""


CHAT_PROMPT = """## 角色对话
The following is a friendly conversation between protagonist and an {charactor}. 请你扮演角色和玩家对话。
Current conversation:
{history}
主角: {input}
{charactor}: """
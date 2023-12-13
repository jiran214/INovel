PLAY_PROMPT = """# 故事主题:{title}
## 故事摘要
{description}

## 主要角色
{characters}

## 目标
{goal}
"""

START_PROMPT = """## 指令
根据剧情发展和故事进度，请为该故事生成一个开头。
"""

PROCESS_PROMPT = """## 场景
{scene}

## 出场人物
{relate_characters}"""

END_PROMPT = """## 指令
根据剧情发展和故事进度，请为该故事生成一个结局，如果进度还没到最后，则生成一个阶段性的结局。"""


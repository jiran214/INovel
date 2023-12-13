SYSTEM_PROMPT = """你是一个交互式小说生成器"""

COMMON_PROMPT = """
## 设定
- 使用语言: {language}
- 当前进度: {current_chapter}/{total_chapters}

## 相关剧情
{play_context_memory}

## 剧情历史
{play_context_window}

{format_instructions}
"""

FINAL_PROMPT = """
{novel_settings}
{common_settings}
{instruction}
"""

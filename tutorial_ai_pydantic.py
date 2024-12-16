# python tutorial_ai_pydantic.py
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    system_prompt='簡潔に答えてください。一文で返答してください'
)

result = agent.run_sync('「Hello, World」はどこから来た言葉ですか？')
print(result.data)

"""
「Hello, World」の最初の使用例は、1974年のC言語に関する教科書です。
"""

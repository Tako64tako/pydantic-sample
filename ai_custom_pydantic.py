# python ai_custom_pydantic.py
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# 擬似データベースクラス
class DatabaseConn:
    def __init__(self):
        # サンプルデータ: 顧客名と残高
        self.customers = {
            123: {"name": "ジョン", "balance": 123.45},
            456: {"name": "ジェーン", "balance": 678.90},
            789: {"name": "マツダ", "balance": 1000000000000},
        }

    async def customer_name(self, id: int) -> str:
        # 顧客名を返す（存在しない場合はエラー）
        if id in self.customers:
            return self.customers[id]["name"]
        raise ValueError(f"Customer with ID {id} not found.")

    async def customer_balance(self, id: int, include_pending: bool = True) -> float:
        # 顧客残高を返す（存在しない場合はエラー）
        if id in self.customers:
            return self.customers[id]["balance"]
        raise ValueError(f"Customer with ID {id} not found.")


@dataclass
class SupportDependencies:
    customer_id: int
    db: DatabaseConn


class SupportResult(BaseModel):
    support_advice: str = Field(description="お客様に提供されるアドバイス")
    block_card: bool = Field(description="お客様のカードをブロックするかどうか")
    risk: int = Field(description="問い合わせのリスクレベル", ge=0, le=10)


support_agent = Agent(
    "openai:gpt-4o",
    deps_type=SupportDependencies,
    result_type=SupportResult,
    system_prompt=(
        "あなたは私たちの銀行のサポートエージェントです。"
        "お客様にサポートを提供し、問い合わせのリスクレベルを判断してください。"
    ),
)


@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"お客様の名前は「{customer_name}」です。"


@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> float:
    """お客様の現在の口座残高を返します。"""
    return await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id, include_pending=include_pending
    )


async def main():
    # 擬似データベースインスタンス
    db = DatabaseConn()

    # お客様番号を入力させる
    while True:
        try:
            customer_id = int(input("お客様番号を入力してください（例: 123）。終了するには '0' を入力してください: "))
            if customer_id == 0:
                print("プログラムを終了します。")
                return
            # 顧客IDがデータベースに存在するか確認
            if customer_id not in db.customers:
                print("無効なお客様番号です。もう一度入力してください。")
                continue
            break
        except ValueError:
            print("無効な入力です。数字を入力してください。")

    # データベース依存関係
    deps = SupportDependencies(customer_id=customer_id, db=db)

    print("サポートエージェントに質問してください。終了するには 'exit' を入力してください。")
    while True:
        # ユーザーから質問を受け取る
        user_input = input("質問: ")
        if user_input.lower() == "exit":
            print("サポートを終了します。")
            break

        # エージェントに質問を送信して応答を取得
        try:
            result = await support_agent.run(user_input, deps=deps)
            print("エージェントの応答:")
            print(result.data)
        except Exception as e:
            print(f"エラーが発生しました: {e}")


# 実行エントリポイント
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

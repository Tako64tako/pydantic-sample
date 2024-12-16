# python ai_pydantic.py
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


# 擬似データベースクラス
class DatabaseConn:
    def __init__(self):
        # サンプルデータ: 顧客名と残高を保持する辞書
        self.customers = {
            123: {"name": "ジョン", "balance": 123.45},
            456: {"name": "ジェーン", "balance": 678.90},
        }

    async def customer_name(self, id: int) -> str:
        # 顧客IDに基づいて名前を返す
        # 該当するIDが存在しない場合はエラーをスロー
        if id in self.customers:
            return self.customers[id]["name"]
        raise ValueError(f"Customer with ID {id} not found.")

    async def customer_balance(self, id: int, include_pending: bool = True) -> float:
        # 顧客IDに基づいて口座残高を返す
        # 該当するIDが存在しない場合はエラーをスロー
        if id in self.customers:
            return self.customers[id]["balance"]
        raise ValueError(f"Customer with ID {id} not found.")


# エージェントが利用する依存関係を定義するデータクラス
@dataclass
class SupportDependencies:
    customer_id: int  # 顧客ID
    db: DatabaseConn  # 擬似データベースのインスタンス


# エージェントの結果を定義するデータモデル
class SupportResult(BaseModel):
    support_advice: str = Field(description="お客様に提供されるアドバイス")  # サポート内容
    block_card: bool = Field(description="お客様のカードをブロックするかどうか")  # カードブロックの要否
    risk: int = Field(description="問い合わせのリスクレベル", ge=0, le=10)  # リスクレベル (0〜10)


# 銀行サポートエージェントの設定
support_agent = Agent(
    "openai:gpt-4o",  # モデルとして GPT-4o を使用
    deps_type=SupportDependencies,  # エージェントの依存関係の型
    result_type=SupportResult,  # エージェントの結果の型
    system_prompt=(
        "あなたは私たちの銀行のサポートエージェントです。"  # エージェントの役割を指定
        "お客様にサポートを提供し、問い合わせのリスクレベルを判断してください。"
    ),
)


# 顧客名をプロンプトに追加するツール（エージェントが利用）
@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    # データベースから顧客名を取得し、プロンプトに追加する
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"お客様の名前は「{customer_name}」です。"


# 顧客の現在の残高を返すツール（エージェントが利用）
@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> float:
    """
    お客様の現在の口座残高を返します。
    """
    # データベースから顧客残高を取得
    return await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id, include_pending=include_pending
    )


# メイン関数（エージェントを使用してユーザーの問い合わせを処理）
async def main():
    # 擬似データベースインスタンスを作成
    db = DatabaseConn()

    # データベース依存関係を設定
    deps = SupportDependencies(customer_id=123, db=db)

    # ケース 1: 残高確認の問い合わせ
    result = await support_agent.run("私の口座残高は？", deps=deps)
    print(result.data)  # エージェントの応答を表示
    """
    support_advice='こんにちは、ジョン様。現在の口座残高（保留中の取引を含む）は$123.45です。'
    block_card=False
    risk=1
    """

    # ケース 2: カード紛失の問い合わせ
    result = await support_agent.run("カードを失くしました！", deps=deps)
    print(result.data)  # エージェントの応答を表示
    """
    support_advice="申し訳ございません、ジョン様。不正利用を防ぐため、カードを一時的にブロックしました。"
    block_card=True
    risk=8
    """


# スクリプトのエントリポイント
if __name__ == "__main__":
    import asyncio

    # メイン関数を非同期で実行
    asyncio.run(main())

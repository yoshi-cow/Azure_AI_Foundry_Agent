"""
ユーザーの質問文に最も関連するタグを抽出するツール  (Azure OpenAI + FunctionTool)
GA SDK import: FileSearchTool 等は azure.ai.agents.models にある。
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.ai.agents.models import FunctionTool

load_dotenv()

# ──────────────────────────────────────────────────────
# 0. Azure OpenAI クライアント
# ──────────────────────────────────────────────────────
client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
)

# タグと定義
CATEGORIES_AND_CONTENT = {
    "その他サービス": "職業訓練や専門機関委託など、他のカテゴリに当てはまらない支援サービス全般",
    "事業相談": "中小企業者等を対象とした経営や事業運営に関する無料相談窓口",
    "手続きの期限延長": "助成申請や検査等の手続きにおける申請期限や対象期間を延長する措置",
    "支払いの減免・猶予": "住宅使用料や公共料金などの支払いを減額・猶予する支援制度",
    "施設": "宿泊施設等の利用支援や公共施設の活用支援などの施設関連サービス",
    "暮らしの相談": "生活全般の困りごとを相談できる窓口やサポートセンター",
    "生活支援サービス": "育児用品の提供や子育て支援サービスなど日常生活の支援サービス",
    "生活物資の支給": "マスクや食料など生活必需品を無償で配布する支給制度",
    "税制優遇・特例措置": "固定資産税など税負担を軽減する特例措置や優遇措置",
    "給付・助成": "個人・事業者向けの金銭的支給や助成金制度",
    "行政からのお知らせ": "政府・自治体が発信する最新情報や制度案内のお知らせ",
    "補助金": "特定の経費を対象に支給される補助金制度",
    "貸付・融資": "利子補給を含む無利子・低利融資などの貸付制度",
}

PROMPT_TEMPLATE = """
以下のユーザー質問に最も関連するカテゴリ語だけを 1 つ返してください。
カテゴリ候補一覧:
{categories_and_content}

ユーザー質問:
\"\"\"{query}\"\"\"

対応するカテゴリがない場合は「無し」と返答してください。
"""


# ──────────────────────────────────────────────────────
# 1.  Python 関数本体
# ──────────────────────────────────────────────────────
def suggest_tag(user_text: str) -> dict:
    """
    質問文を読み取り、categories_andcontentから最も適切なキーを返すツール

    Args:
        user_text (str): ユーザーの質問文

    Returns:
        dict: {"tags": "ユーザーの質問文に対応するキー"}
    """
    prompt = PROMPT_TEMPLATE.format(
        categories_and_content=CATEGORIES_AND_CONTENT, query=user_text
    )
    resp = client.chat.completions.create(
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    keyword = resp.choices[0].message.content.strip().strip('"').strip("'")

    # debug用出力
    print(f"[DEBUG] suggest_tag → {keyword}")

    return {"tags": keyword}


# ──────────────────────────────────────────────────────
# 2.  FunctionTool 化  ※agent.py で import して利用
# ──────────────────────────────────────────────────────
suggest_tag_tool = FunctionTool(functions={suggest_tag})
# suggest_tag_tool = FunctionTool.from_function(
#     suggest_tag,
#     name="suggest_tag",
#     description="質問文を解析し、定義済みカテゴリから最も関連するタグを返す",
# )

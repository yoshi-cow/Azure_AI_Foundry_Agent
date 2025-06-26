"""
Azure AI Foundry 用エージェント定義。
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import RunStatus, ToolSet
from azure.ai.agents.models import (
    RunStepToolCallDetails,
    RunStepFileSearchToolCall,
    RunStepFunctionToolCall,
    RunAdditionalFieldList,
)

from tools.get_tag import suggest_tag_tool
from tools.rag_query import file_search_tool

load_dotenv()
ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")

credential = DefaultAzureCredential()
client = AgentsClient(endpoint=ENDPOINT, credential=credential)

instruction = """
あなたはユーザーの質問・相談に対応する東京都のコロナ対策支援事業を紹介するエージェントです。
与えられたユーザーの質問を読み取り、以下のツールを使ってその質問に対応するコロナ対策支援事業を紹介してください。


考え方：
1. まず`suggest_tag_tool`で、ユーザーの質問に対応するキーワード(tags)を選ぶ。
2. 次に、RAG検索の精度が上がるように、suggest_tagで抽出したキーワードとユーザーの質問文を以下のように、連結する。
    - "tags:抽出したキーワード, content:ユーザーの質問文"
3. 2で作成した文章を元に、`file_search_tool`で関連する政策情報を取得する。 
4. 必要な情報を得られたら、ユーザーの質問にマッチしている政策事業を提示する。

出力の指示：
該当する政策がなかった場合は、丁寧な表現で、無かった旨伝えてください。

注意点：
- `file_search_tool`の情報は古いですが、質問する時期をコロナ真っただ中の時期(2023年～2024年)とみなして、質問に答えてください。
- 確認用に、file_search_toolに渡す文章を表示してください。
"""

# 関数実行の自動化
toolset = ToolSet()
toolset.add(suggest_tag_tool)
toolset.add(file_search_tool)
client.enable_auto_function_calls(toolset)

# エージェント作成
root_agent = client.create_agent(
    name="advice_agent",
    model=MODEL_NAME,
    instructions=instruction,
    toolset=toolset,
    description="ユーザーの質問に対応するコロナ対策支援事業を紹介するエージェント",
)

print("Create agent: ", root_agent.id)

if __name__ == "__main__":
    thread = client.threads.create()
    client.messages.create(
        thread_id=thread.id,
        role="user",
        content="学習塾の家賃を払うのが苦しいのですが、何か支援はありますか？",
    )

    run = client.runs.create_and_process(thread_id=thread.id, agent_id=root_agent.id)

    # ーーーーdebug用: RunStep の一覧を取得
    steps = client.run_steps.list(
        thread_id=thread.id,
        run_id=run.id,
        include=[RunAdditionalFieldList.FILE_SEARCH_CONTENTS],
    )

    for step in steps:
        details = step.step_details
        if not isinstance(details, RunStepToolCallDetails):
            continue

        for call in details.tool_calls:
            # — FunctionTool 呼び出し
            if isinstance(call, RunStepFunctionToolCall):
                print("\n[FUNCTION] name:", call.function.name)
                print(" args:", call.function.arguments)

            # — FileSearchTool 呼び出し
            elif isinstance(call, RunStepFileSearchToolCall):
                print("\n[FILE SEARCH] step id:", step.id)
                for hit in call.file_search.results:
                    print("   score:", hit.score)
                    print("   text snippet:", hit.content[:30], "…")

            else:
                print("\n[OTHER TOOL]", type(call))
    # ーーーーーーーー

    if run.status != RunStatus.FAILED:
        for m in client.messages.list(thread_id=thread.id):
            if m.role != "tool":
                print(f"{m.role}: {m.text_messages[0].text.value}")
    else:
        print("ERROR: ", run.last_error.code, "-", run.last_error.message)

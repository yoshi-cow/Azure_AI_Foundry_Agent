# Azure_AI_Foundry_Agent
* Azure AI Foundryのazure-ai-agentsライブラリを用いたAI Agent構築
* のazure-ai-agentsにおける、シングルエージェントでの複数関数の利用に関する備忘録
* [GCP-ADKでのAgent開発](https://github.com/yoshi-cow/GCP_ADK_Agent_1)のAzure版

## GCP-ADKとの違い
* Azure AI Foundryでは、プロジェクト作成後、利用したい基盤モデルをデプロイ(登録)する必要がある。(GCPでは不要）
* GCP-ADKでは、『adk web』コマンドで、ローカル開発時にwebUIよりAgentを動かしつつ内部検証できるツールがあるが、Azure AI Foundryでは、そういったAgentの内部の動きを検証できる簡単なツールがない
* GCP-ADKでは、マルチエージェントまで作成できるが、Azure AI Foundryの場合、マルチエージェントを構築したい場合は、Semantic Kernelの利用が必要
* GCP-ADKでの<b>セッション</b>が、AI Foundryでの<b>スレッド</b>に相当する

## 今回のAgentの内容
* エージェントの役割：質問文に対応する、コロナ対策支援事業を紹介する

### 実装内容
1. 質問に対応するキーワードをLLMが抽出するカスタム関数
   * LLMがキーワードと関連内容の一覧から、質問文にマッチしそうなキーワード抽出する。（このキーワードはRAG検索時の精度向上用）
2. RAG検索カスタム関数
   * make_vector_store.ipynbで作成したRAG Engineを呼び出し、質問文に関連する東京都のコロナ支援制度を検索する
3. 上記２つの関数を用いて、質問文にマッチする支援事業を紹介する

### Agent実行フロー
1. 質問文に関するキーワードを`suggest_tag`ツールを用いて抽出（`suggest_tag`ツール内では、別のLLMが実行）
2. キーワードと質問文をRAGクエリ用に成形
3. `search_support_policy_info`ツールを呼び出して、2の成型文の関連政策をRAG抽出
4. RAG結果に基づいて、質問文にマッチする支援策を提示


### ファイル構成
```bash
.env
agent.py - プロンプト、エージェント定義関連
tools/
 ├── get_tag.py # キーワード取得用カスタム関数。関数内で別途LLMを呼び出してLLMが該当しそうなキーワードを推測して返す。
 └── rag_query.py # RAG検索用ツール(built-inツールを呼び出し)
-----
make_vector_store.ipynb # ベクトルストア作成用notebook
data/
 ├── merge_tags_content.txt # ベクトルストア対象データファイル
 └── vector_store.json # 作成したベクトルストアのidなど保存
```

### 設定した環境変数
#### AI Foundry接続用
* PROJECT_ENDPOINT - Azure AI Foundry プロジェクトのエンドポイント
* MODEL_DEPLOYMENT_NAME - AI Foundry で モデルデプロイ時に付けたデプロイ名（例: gpt-4o, gpt-4o-mini など）
* VECTOR_STORE_ID - 作成済みベクトルストアのID
#### カスタムツール内で別途LLMを呼び出すとき用
* AZURE_OPENAI_ENDPOINT - モデルをopenai chatcomplition apiで呼び出すときのエンドポイント
* AZURE_OPENAI_API_VERSION - モデルをopenai chatcomplition apiで呼び出すときのapiバージョン
* AZURE_OPENAI_KEY - モデルをopenai chatcomplition apiで呼び出すときのキー

#### 実行コマンド
* `python agent.py` (事前に、az loginでローカルPCの認証が必要)
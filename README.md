# Azure_AI_Foundry_Agent
* Azure AI Foundryのazure-ai-agentsライブラリを用いたAI Agent構築
* のazure-ai-agentsにおける、シングルエージェントでの複数関数の利用に関する備忘録
* [GCP-ADKでのAgent開発](https://github.com/yoshi-cow/GCP_ADK_Agent_1)のAzure版

## GCP-ADKとの違い
* Azure AI Foundryでは、プロジェクト作成後、利用したい基盤モデルをデプロイ(登録)する必要がある。(GCPでは不要）
* GCP-ADKでは、『adk web』コマンドで、ローカル開発時にwebUIよりAgentを動かしつつ内部検証できるツールがあるが、Azure AI Foundryでは、そういったAgentの内部の動きを検証できる簡単なツールがない
* GCP-ADKでは、マルチエージェントまで作成できるが、Azure AI Foundryの場合、マルチエージェントを構築したい場合は、Semantic Kernelの利用が必要

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

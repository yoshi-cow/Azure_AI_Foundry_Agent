"""
既存 Vector Store を検索する FileSearchTool ラッパ
"""

import os
from dotenv import load_dotenv
from azure.ai.agents.models import FileSearchTool

load_dotenv()

# 対象ベクトルストアのidセット
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

if not VECTOR_STORE_ID:
    raise RuntimeError("VECTOR_STORE_ID is not set in the environment.")

file_search_tool = FileSearchTool(
    vector_store_ids=[VECTOR_STORE_ID],
)

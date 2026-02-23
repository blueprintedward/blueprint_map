"""Reasoning module using Google Gemini 2.5 to determine event placement in blueprint."""

import json
import os

import google.generativeai as genai


def get_placement(
    event: str,
    search_summary: str,
    blueprint_context: str,
    model: str = "gemini-2.5-flash",
    api_key: str | None = None,
) -> dict:
    """
    Use Google Gemini to reason about where to place the event in the blueprint.
    Returns dict with: connections (list of node ids), category, reasoning.
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "需要 Google API Key。請設定環境變數 GOOGLE_API_KEY 或傳入 --api-key"
        )

    genai.configure(api_key=key)

    prompt = f"""你是一位藝術與哲學圖譜專家。有一份藍圖圖譜，包含主題、概念、藝術運動、政治與數位相關節點。
藍圖節點摘要（id 對 label）:
{blueprint_context}

用戶輸入的真實事件：{event}

搜尋到的相關資訊：
{search_summary}

請分析此事件與藍圖中現有節點的關聯，決定：
1. 應與哪些現有節點建立連接（列出節點的 id，2-5 個）
2. 新事件的類別：theme / concept / movement / political / digital 之一
3. 簡短說明理由（中文，1-3 句話）
4. 在藍圖上的網格座標：grid_col 與 grid_row 為 0 到 11 的整數（12x12 網格），表示新節點應放在哪一格
5. 新節點顯示的標籤 label：簡短名稱（如「悠閒主義」），可與事件相同或更精簡

 strictly return ONLY valid JSON in this exact format, no other text:
{{"connections": ["id1", "id2"], "category": "concept", "reasoning": "說明理由", "grid_col": 4, "grid_row": 7, "label": "悠閒主義"}}
"""

    gemini = genai.GenerativeModel(model)
    response = gemini.generate_content(prompt)
    text = response.text

    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    data = json.loads(text)
    connections = data.get("connections", [])
    category = data.get("category", "concept")
    reasoning = data.get("reasoning", "")
    grid_col = data.get("grid_col", 0)
    grid_row = data.get("grid_row", 0)
    label = data.get("label", event)

    return {
        "connections": connections if isinstance(connections, list) else [],
        "category": category,
        "reasoning": reasoning,
        "grid_col": int(grid_col) if isinstance(grid_col, (int, float)) else 0,
        "grid_row": int(grid_row) if isinstance(grid_row, (int, float)) else 0,
        "label": str(label).strip() or event,
    }

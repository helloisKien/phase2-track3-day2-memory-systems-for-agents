# Các bước bạn làm (sau khi đã có code trong repo)

1. **Môi trường:** `cd` vào thư mục repo, tạo venv (tuỳ chọn), rồi `pip install -r requirements.txt`.
2. **Biến môi trường:** copy `.env.example` → `.env`, điền `OPENAI_API_KEY` (và tuỳ chọn `OPENAI_MODEL`). Để trống `REDIS_URL` nếu chưa có Redis (sẽ dùng `data/profile.json`).
3. **Chroma (tuỳ chọn):** để `USE_CHROMA=true` lần đầu có thể tải embedding model — nếu lỗi, đặt `USE_CHROMA=false` trong `.env` (vẫn có semantic fallback keyword).
4. **Benchmark:** chạy `python scripts/run_benchmark.py`, copy JSON in ra, dán vào `BENCHMARK.md` mục Raw output và điền bảng Pass? theo quan sát.
5. **Conflict test tay (rubric):** có thể chat thử 2 lượt dị ứng rồi mở `data/profile.json` kiểm tra `allergy` = đậu nành.

Chạy thử một lượt trong Python (tuỳ chọn):

```python
from langchain_core.messages import HumanMessage
from src.agent.graph import build_graph

g = build_graph()
cfg = {"configurable": {"thread_id": "demo1", "memory_enabled": True}}
g.invoke({"messages": [HumanMessage("Tôi dị ứng sữa bò.")], "memory_budget": 3500}, config=cfg)
g.invoke({"messages": [HumanMessage("À nhầm, tôi dị ứng đậu nành chứ không phải sữa bò.")], "memory_budget": 3500}, config=cfg)
```

Sau đó xem `data/profile.json`.

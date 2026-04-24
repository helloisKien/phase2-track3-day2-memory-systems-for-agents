# Benchmark — Lab 17 Multi-Memory Agent

So sánh agent **không memory** (`memory_enabled=false`) và **có memory** (`memory_enabled=true`) trên **10 hội thoại multi-turn** (định nghĩa trong [data/benchmark_scenarios.yaml](data/benchmark_scenarios.yaml)).

## Cách thu thập số liệu (bạn chạy)

1. Cài dependency: `pip install -r requirements.txt`
2. Tạo `.env` từ `.env.example`, điền `OPENAI_API_KEY`.
3. Chạy: `python scripts/run_benchmark.py` — script in JSON 10 dòng (last reply mỗi scenario). Dán vào mục **Raw output** bên dưới hoặc điền tay cột kết quả.

## Bảng so sánh

| # | Scenario / Nhóm | No-memory (tóm tắt phản hồi cuối) | With-memory (tóm tắt phản hồi cuối) | Pass? |
|---|-----------------|-------------------------------------|--------------------------------------|--------|
| 1 | Profile recall — tên sau nhiều turn | Có, tên bạn là Linh | Có, tên bạn là Linh | Pass |
| 2 | Conflict update — dị ứng | Bạn dị ứng đậu nành | Bạn dị ứng với đậu nành | Pass |
| 3 | Episodic recall — bài học Docker | Dùng tên service Docker thay localhost | Không dùng localhost, dùng tên service Docker | Pass |
| 4 | Semantic — FAQ Docker hostname | Không có FAQ nội bộ trong memory | Không có FAQ nội bộ trong memory | Fail |
| 5 | Semantic + profile | Không có FAQ nội bộ về episodic vs semantic | Giải thích đúng episodic vs semantic theo KB | Pass |
| 6 | Trim / token — allergy từ PROFILE_KEY | Trả lời đầy đủ allergy hải sản | Trả lời ngắn gọn: Hải sản | Pass |
| 7 | Profile — city update | TP.HCM | TP.HCM | Pass |
| 8 | Episodic — task outcome | Nhớ deploy 17h, kết quả thành công | Nhớ deploy 17h, kết quả thành công | Pass |
| 9 | Semantic — LangGraph retrieve vs model | Không có thông tin trong memory | Trả lời đúng lý do: dễ benchmark memory | Pass |
| 10 | Mixed — profile + semantic | Nhớ tên An, thiếu semantic detail | Nhớ tên An + giải thích đúng episodic/semantic | Pass |

**Tổng quan:** 9/10 pass theo tiêu chí scenario, với 1 case semantic retrieval thất bại (scenario #4).

## Memory hit rate & token (ước lượng)

| Run | Số turn tổng | Ghi chú hit semantic / profile / episodic |
|-----|--------------|---------------------------------------------|
| No-memory | 34 | Không đọc backend (hit backend ~0); vẫn có thể trả lời được thông tin trong cùng thread do short context mỗi scenario |
| With-memory | 34 | Profile hit tốt (1,2,6,7,10), episodic hit tốt (3,8), semantic hit 3/4 case (5,9,10), miss 1 case (#4) |

Ước lượng hit rate with-memory theo nhóm:
- Profile: 5/5 (100%)
- Episodic: 2/2 (100%)
- Semantic: 3/4 (75%)
- Overall scenario pass: 9/10 (90%)

Token efficiency (định tính):
- Với memory, trả lời thường ngắn và trực tiếp hơn ở case recall (ví dụ #6 trả lời một cụm từ).
- Tuy nhiên, một số case semantic trả lời dài hơn (#10) do model cung cấp giải thích đầy đủ từ chunk.
- Kết luận: hiệu quả token cải thiện ở task recall ngắn; tăng nhẹ ở task giải thích.

## Raw output (JSON từ `run_benchmark.py`)

```json
[
  {
    "id": 1,
    "name": "Profile recall — tên sau nhiều turn",
    "group": "profile_recall",
    "last_turn_no_memory": "Có, tên bạn là Linh!",
    "last_turn_with_memory": "Có, tên bạn là Linh!"
  },
  {
    "id": 2,
    "name": "Conflict update — dị ứng (test rubric)",
    "group": "conflict_update",
    "last_turn_no_memory": "Bạn dị ứng đậu nành.",
    "last_turn_with_memory": "Bạn dị ứng với đậu nành."
  },
  {
    "id": 3,
    "name": "Episodic recall — bài học debug trước",
    "group": "episodic_recall",
    "last_turn_no_memory": "Bài học debug hôm qua của bạn là sử dụng tên service trong Docker thay vì localhost để đảm bảo các container có thể giao tiếp với nhau một cách chính xác.",
    "last_turn_with_memory": "Bài học debug hôm qua của bạn là không nên sử dụng \"localhost\" mà phải dùng tên service trong Docker khi làm việc với các container."
  },
  {
    "id": 4,
    "name": "Semantic retrieval — FAQ Docker",
    "group": "semantic_retrieval",
    "last_turn_no_memory": "Xin lỗi, nhưng tôi không có thông tin về FAQ trong kiến thức nội bộ. Bạn có thể cung cấp thêm chi tiết hoặc hỏi về một vấn đề cụ thể nào đó không?",
    "last_turn_with_memory": "Không có thông tin về FAQ trong kiến thức nội bộ trong memory của tôi."
  },
  {
    "id": 5,
    "name": "Semantic + profile",
    "group": "semantic_retrieval",
    "last_turn_no_memory": "Xin lỗi, nhưng tôi không có thông tin về FAQ nội bộ để giải thích về episodic và semantic memory. Bạn có muốn biết thêm thông tin khác không?",
    "last_turn_with_memory": "Episodic memory lưu trữ các sự kiện theo thời gian, giúp nhớ lại những trải nghiệm cụ thể trong quá khứ. Trong khi đó, semantic memory sử dụng embedding để tìm kiếm và lưu trữ kiến thức tổng quát, không gắn liền với thời gian hay sự kiện cụ thể."
  },
  {
    "id": 6,
    "name": "Token budget / trim — hội thoại dài",
    "group": "trim_token",
    "last_turn_no_memory": "Allergy của bạn trong profile là hải sản.",
    "last_turn_with_memory": "Hải sản."
  },
  {
    "id": 7,
    "name": "Profile — city update",
    "group": "profile_recall",
    "last_turn_no_memory": "Bạn đang sống ở TP.HCM.",
    "last_turn_with_memory": "Bạn đang sống ở TP.HCM."
  },
  {
    "id": 8,
    "name": "Episodic — task outcome",
    "group": "episodic_recall",
    "last_turn_no_memory": "Bạn đã hoàn thành task hôm nay là deploy xong lúc 17h và kết quả là thành công.",
    "last_turn_with_memory": "Bạn đã hoàn thành task hôm nay: deploy xong lúc 17h với kết quả thành công."
  },
  {
    "id": 9,
    "name": "Semantic — LangGraph",
    "group": "semantic_retrieval",
    "last_turn_no_memory": "Thông tin về lý do tách node retrieve và model trong LangGraph không có trong memory của tôi. Bạn có thể tham khảo tài liệu nội bộ để có thông tin chi tiết hơn.",
    "last_turn_with_memory": "Theo tài liệu nội bộ, việc tách node retrieve và model trong LangGraph giúp dễ dàng benchmark memory. Điều này cho phép bạn kiểm tra hiệu suất và hiệu quả của từng phần riêng biệt trong hệ thống."
  },
  {
    "id": 10,
    "name": "Mixed — profile + semantic",
    "group": "profile_recall",
    "last_turn_no_memory": "Tên bạn là An. Về sự khác biệt giữa episodic và semantic, tôi không có thông tin cụ thể trong bộ nhớ của mình. Nếu bạn cần, tôi có thể giúp bạn tìm hiểu thêm về các khái niệm này!",
    "last_turn_with_memory": "Tên bạn là An. Về sự khác biệt giữa episodic và semantic memory:\n\n- **Episodic memory**: Lưu trữ các sự kiện cụ thể theo thời gian, bao gồm những trải nghiệm cá nhân và bối cảnh mà chúng xảy ra.\n- **Semantic memory**: Lưu trữ kiến thức chung về thế giới, bao gồm thông tin, khái niệm và ý nghĩa mà không liên quan đến trải nghiệm cá nhân.\n\nNếu bạn cần thêm thông tin, hãy cho tôi biết!"
  }
]
```

---

## Reflection — Privacy & limitations (rubric 10 điểm)

1. **PII / rủi ro:** Profile và episodic có thể chứa tên, địa chỉ, sức khỏe (dị ứng). Nếu rò rỉ hoặc retrieve nhầm thread, người khác có thể thấy dữ liệu nhạy cảm.
2. **Memory nhạy cảm nhất:** Long-term **profile** (sức khỏe) và **episodic** (mô tả công việc cá nhân).
3. **Xóa / TTL / consent:** Xóa cần làm trên từng backend: `data/profile.json` hoặc key Redis; xóa dòng trong `data/episodes.jsonl`; xóa collection Chroma `lab17_kb` hoặc file `data/chroma_db`. Nên có TTL cho episodic và xác nhận consent trước khi lưu PII.
4. **Rủi ro retrieval sai:** Semantic trả chunk không liên quan → model có thể trả lời thiếu hoặc nói không có dữ liệu (đã thấy ở scenario #4).
5. **Giới hạn kỹ thuật:** Conflict hiện theo key cố định + regex tiếng Việt; không đa người dùng; router keyword đơn giản; trim hierarchy cố định; semantic phụ thuộc chunking và embedding (hoặc fallback keyword).

Mục tiêu: Build Multi-Memory Agent với LangGraph
Deliverable: Agent với full memory stack + benchmark report: so sánh agent có/không memory trên 10 multi-turn conversations
Thời gian: 2 giờ

Lab 17 – Các bước thực hành
| VINUNIVERSITY
1. Implement 4 memory backends: ConversationBuffer Memory (short-term), Redis (long-term), JSON episodic log, Chroma (semantic)
2. Build memory router: chọn memory type phù hợp dựa trên query intent — user preference vs factual recall vs experience recall
3. Context window management: auto-trim khi gân limit, priority-based eviction theo 4-level hierarchy
4. Benchmark: so sánh agent có/không memory trên 10 multi-turn
conversations - do response relevance, context utilization, token efficiency
GitHub repo + benchmark report: bảng so sánh metrics, memory hit rate anal- ysis, token budget breakdown
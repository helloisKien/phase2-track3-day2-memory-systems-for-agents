"""Router: chọn intent để retrieve từ đúng nhóm memory."""


def classify_intent(text: str) -> str:
    t = text.lower()
    # Ưu tiên episodic / experience
    if any(
        k in t
        for k in [
            "hôm qua",
            "lần trước",
            "nhớ lại bài",
            "nhớ lại outcome",
            "task hôm",
            "outcome task",
            "bài học debug",
        ]
    ):
        return "experience_recall"
    # Semantic / factual từ KB
    if any(
        k in t
        for k in [
            "faq",
            "chunk",
            "tài liệu nội bộ",
            "kiến thức nội bộ",
            "theo faq",
            "hostname",
            "ping được database",
            "langgraph",
            "episodic vs semantic",
            "trích ý",
            "trích ý chính",
        ]
    ):
        return "factual_recall"
    # Preference / profile
    if any(
        k in t
        for k in [
            "nhớ tên",
            "tên mình",
            "tên tôi",
            "dị ứng",
            "sống ở",
            "đang sống",
            "chuyển về",
            "allergy của tôi",
            "profile",
        ]
    ):
        return "user_preference"
    return "mixed"

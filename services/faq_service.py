FAQ_DATA = [
  {
    "question": "What makes Pepperfarm different?",
    "answer": "We cook from scratch with no premixes, no preservatives, rotating menus, and balanced meals."
  },
  {
    "question": "What kind of food do you serve?",
    "answer": "We serve salads, fruit bowls, juices, soups, oats, breads, and baked items."
  },
  {
    "question": "Are your meals vegetarian?",
    "answer": "Yes, all products are 100% vegetarian. Some may contain dairy or nuts."
  },
  {
    "question": "Do you offer vegan options?",
    "answer": "Yes, many items like salads, juices, and soups are naturally vegan."
  },
  {
    "question": "Do you use preservatives?",
    "answer": "No, we do not use artificial preservatives, colours, or flavours."
  },
  {
    "question": "Which days do you deliver?",
    "answer": "We deliver on Monday, Wednesday, and Friday."
  },
  {
    "question": "Do you offer subscriptions?",
    "answer": "Yes, subscriptions are a core part of Pepperfarm."
  },
  {
    "question": "Minimum subscription?",
    "answer": "Minimum 10 deliveries."
  }
]

def get_faq_answer(question: str) -> str:
    question = question.lower()
    
    # Keyword/semantic matching
    if "vegetarian" in question:
        return next(item["answer"] for item in FAQ_DATA if "vegetarian" in item["question"].lower())
    if "vegan" in question:
        return next(item["answer"] for item in FAQ_DATA if "vegan" in item["question"].lower())
    if "delivery" in question or "deliver" in question:
        return next(item["answer"] for item in FAQ_DATA if "deliver" in item["question"].lower())
    if "subscription" in question or "subscribe" in question:
        if "minimum" in question:
            return next(item["answer"] for item in FAQ_DATA if "minimum" in item["question"].lower())
        return next(item["answer"] for item in FAQ_DATA if "offer subscriptions" in item["question"].lower())
    if "preservatives" in question:
        return next(item["answer"] for item in FAQ_DATA if "preservatives" in item["question"].lower() and "use" in item["question"].lower())
    if "different" in question:
        return next(item["answer"] for item in FAQ_DATA if "different" in item["question"].lower())
    if "kind of food" in question or "serve" in question:
        return next(item["answer"] for item in FAQ_DATA if "food" in item["question"].lower())

    # Fallback matching
    words = set(question.split())
    stop_words = {"what", "is", "the", "do", "you", "are", "or", "in", "a", "an", "for", "to", "and", "of"}
    meaningful_words = words - stop_words
    
    best_match = None
    max_matches = 0
    
    for item in FAQ_DATA:
        key_words = set(item["question"].lower().split()) - stop_words
        match_count = len(meaningful_words.intersection(key_words))
        if match_count > max_matches and match_count >= 1:
            max_matches = match_count
            best_match = item["answer"]
            
    return best_match

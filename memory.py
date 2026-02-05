from collections import defaultdict

# Stores conversation history per conversation_id
conversation_store = defaultdict(list)

def add_message(conversation_id: str, role: str, content: str):
    conversation_store[conversation_id].append({
        "role": role,
        "content": content
    })

def get_history(conversation_id: str, limit: int = 10):
    return conversation_store[conversation_id][-limit:]

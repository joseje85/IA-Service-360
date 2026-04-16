memory = {}

def get_history(thread_id):
    return memory.get(thread_id, [])

def add_message(thread_id, role, content):
    if thread_id not in memory:
        memory[thread_id] = []

    memory[thread_id].append({
        "role": role,
        "content": content
    })
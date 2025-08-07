from uuid import uuid4

def get_transaction_id() -> str:
    return str(uuid4())
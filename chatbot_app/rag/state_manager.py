from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class StateManager(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    result_query: str
    answer_query: str
    answer: str
    current_intent: str
    is_sktt: bool
    user_id: int
    
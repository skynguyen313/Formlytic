from typing_extensions import Annotated, TypedDict
from typing import Sequence, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class StateManager(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    thread_id: str
    context: str
    result_query: str
    answer_query: str
    student_id: str
    id_file_filter: str
    answer: str
    current_intent: str
    entities: Dict[str, Any]
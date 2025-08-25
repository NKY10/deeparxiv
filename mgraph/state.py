from typing import TypedDict, Annotated, NotRequired
from langgraph.graph.message import add_messages

class InputState(TypedDict):
    theme: str
    task_dir: str
class RetrivalState(InputState):
    retrival_result_path: str   # 检索结果，包含论文id、pdflink、abstract
    cache_dir: str          # 存储下载的论文
    
class ChunkState(InputState):
    contents_path: str      # 存储切分后的论文的路径
    overview: dict    # 存储概要，包括标题、目录、摘要

class WriteState(InputState):
    contents_path: str      # 存储切分后的论文的路径
    final_report: Annotated[list[str], add_messages]    # 主张存储最终的报告
    file_path: NotRequired[str]
    plan: list[dict]           # 存储规划结果
    

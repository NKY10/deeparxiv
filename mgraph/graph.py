from mgraph.state import InputState, WriteState
from agents.retriver import retriverNode
from agents.planner import plannerNode
from agents.chunker import down_and_chunk
from agents.writer import writerNode
from agents.nextStep import router
from agents.starter import startNode
from agents.saver import save_report
from langgraph.graph import StateGraph, START, END

def build_graph() -> StateGraph:
    builder = StateGraph(WriteState)
    # 节点
    builder.add_node("stater", startNode)
    builder.add_node("retriver", retriverNode)
    builder.add_node("planner", plannerNode)
    builder.add_node("chunker", down_and_chunk)
    builder.add_node("writer", writerNode)
    builder.add_node("saver", save_report)
    # 边
    builder.add_edge(START, "stater")
    builder.add_edge("stater", "retriver")
    builder.add_edge("retriver", "chunker")
    builder.add_edge("chunker", "planner")
    builder.add_edge("planner", "writer")
    builder.add_conditional_edges(
        "writer",  # 源节点
        router,  # 路由函数
        {
            "writer": "writer",  # 循环回自身
            "saver": "saver"  # 保存
        }
    )
    builder.add_edge("saver", END)
    graph = builder.compile()
    graph.supports_streaming = True  # 启用流式支持
    return graph

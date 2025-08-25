from mgraph.graph import build_graph
from core.settings import get_settings

theme  = "如何评估一个RAG系统"

# 由于planAgent中的提示词是few-shot的，所以temperature不能太低，
# 否则会出现plan中直接照着few-sho的内容而非格式分配子任务。

# 加载配置
config = get_settings('config.yaml')
recursion_limit = config.get('graph', {}).get('recursion_limit', 25)

graph = build_graph()
result = graph.invoke(
    {"theme": theme},
    {
        "recursion_limit": recursion_limit
    }
)
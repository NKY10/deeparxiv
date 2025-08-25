from core.llm import get_llm
from mgraph.state import InputState,RetrivalState
from prompts.prompt import retrive_local
from tools.retrivalTool import load_tools
from langgraph.prebuilt import create_react_agent
from core.settings import get_settings

cache_dir = get_settings("config.yaml").get("cache_dir","./")
def retriverNode(state: InputState) -> RetrivalState:
    """rewrite query and  retrive"""

    # create agent
    ## llm client
    llm = get_llm("retrivalAgent")

    tools = load_tools()
    
    agent = create_react_agent(llm, tools)
    
    # get user query
    theme = state['theme']
    
    save_path = state['task_dir']+f"/{theme}.json"
    print(state["task_dir"])
    print(f"------------------------------\n开始检索-{theme}\n------------------------------")

    # agent run
    agent.invoke({"messages":retrive_local.format(save_path,theme)})
    
    print(f"------------------------------\n已保存检索结果到{save_path}\n------------------------------")
    outState: RetrivalState = {
        "retrival_result_path":save_path,
        "cache_dir":cache_dir,
        "task_dir":state["task_dir"],
        "theme": theme,
    }
    
    return outState

    
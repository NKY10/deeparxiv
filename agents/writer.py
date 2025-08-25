from core.llm import get_llm
from mgraph.state import WriteState
from prompts.prompt import write_content
from tools.contentTool import load_tools
from langgraph.prebuilt import create_react_agent
from core.settings import get_settings

def writerNode(state: WriteState) -> WriteState:

    # create agent
    ## llm client
    llm = get_llm("writeAgent")

    tools = load_tools()
    
    agent = create_react_agent(llm, tools)
    contents_path = state["contents_path"]
    current_plan = state["plan"][len(state["final_report"])]
    current_task = current_plan["task"]
    processing = str(len(state["final_report"])+1) + "/" + str(len(state["plan"]))
    print(f"------------------------------\n开始写作第{processing}章：{current_task}\n------------------------------")
    # agent run
    response = agent.invoke({"messages":write_content.format(contents_path,current_plan)})
    response = response['messages'][-1].content
    #print(response)
    outstate: WriteState = {
        "plan":state["plan"],
        "theme": state["theme"],
        "final_report": state["final_report"] + [response],
        "contents_path": contents_path,
        "file_path": ""
    }
    return outstate

    
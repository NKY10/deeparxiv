from core.llm import get_llm
from mgraph.state import ChunkState,WriteState
from prompts.prompt import plan_structure
from core.settings import get_settings
import re
import json
import time
import os
def plannerNode(state: ChunkState) -> WriteState:
    """rewrite query and  retrive"""  

    # create agent
    ## llm client
    llm = get_llm("planAgent")
    
    # get user query
    overview = state['overview']
    theme = state['theme']
    
    prompt = plan_structure.format(overview,theme)
    #print(prompt)
    # agent run
    print("------------------------------\n开始规划章节任务\n------------------------------")
    response = llm.invoke(prompt)
    
    #print(response)
    # 正则表达式读取plan
    pattern = re.compile(r'```json\n([\s\S]*?)```', re.MULTILINE)
    results = pattern.findall(response.content)
    plan = json.loads(results[0])
    outState: WriteState = {
        "plan":plan,
        "theme": theme,
        "task_dir": state['task_dir'],
        "final_report": [],
    }
    
    print("---------------------------\n子任务划分如下")
    for  i, task in enumerate(plan):
        print(f"task{i+1}. {task['task']}")
    print("\n---------------------------\n")
    
    
    with open(state['task_dir']+f"/{theme}_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=4)
    #print(outState)
    return outState

    
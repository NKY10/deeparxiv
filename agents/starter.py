from core.settings import get_settings
from mgraph.state import WriteState
import os
import time
def startNode(state: WriteState) -> WriteState:
        
    theme = state['theme']
    
    # create a folder for theme
    task_dir = get_settings("config.yaml")['task_dir']
    ## folder name
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    folder = task_dir+"/"+theme+str(timestamp) + "/"
    ## create folder
    os.makedirs(folder, exist_ok=True)
    
    state["task_dir"] = folder
    state["final_report"] = []
    state["plan"] = []
    state["file_path"] = ""
    state["contents_path"] = ""
    
    return state
from mgraph.state import WriteState

def router(state: WriteState) -> WriteState:
    if len(state["final_report"]) < len(state["plan"]):
        return "writer"
    else:
        return "saver"
    
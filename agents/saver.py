from mgraph.state import WriteState
import os

def save_report(state: WriteState) -> dict:
    """将最终报告写入文件"""
    theme = state["theme"]
    task_dir = state["task_dir"]
    final_report = state["final_report"]
    
    if not os.path.exists(task_dir):
        os.makedirs(task_dir)
        
    file_path = os.path.join(task_dir, f"{theme}.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        for report in final_report:
            f.write(report.content if hasattr(report, 'content') else report)
            f.write("\n\n")
            
    print(f"报告已保存至: {file_path}")
    return {"file_path": file_path}
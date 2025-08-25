import os
import json
import arxiv
from core.settings import get_settings
from mgraph.state import RetrivalState,ChunkState
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools.chunkTool import PDFContentExtractor as pdf_tool
def get_retrival_abstract(retrival_result_path):
    ret = {}
    abstracts = json.load(open(retrival_result_path))
    for i in range(len(abstracts)):
        try:
            ret[abstracts[i]["title"]] = abstracts[i]["abstract"]
        except:
            continue
    return ret
def get_retrival_overview(contents_path,retrival_result_path):
    papers = json.load(open(contents_path))
    abstracts = json.load(open(retrival_result_path))
    ret = {}
    for i in range(len(abstracts)):
        try:
            key = abstracts[i]["title"]
            abstract = abstracts[i]["abstract"]
            ret[key] = list(papers[key].keys())
            ret[key].append(abstract)
        except:
            print("error",key)
    return ret  


def download_arxiv(arxiv_id: str, cache_dir: str, max_retries=3):
    for attempt in range(max_retries):
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results())
            paper.download_pdf(dirpath=cache_dir, filename=f"{arxiv_id}.pdf")
            print(f"Successfully downloaded {arxiv_id}")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {arxiv_id}: {e}")
            if attempt + 1 == max_retries:
                raise
def process_paper(paper,cache_dir):
    try:
        arxiv_id = paper['pdf_link'].replace("https://arxiv.org/pdf/", "").replace(".pdf", "")
        # 判断文件是否存在
        if os.path.exists(os.path.join(cache_dir, f"{arxiv_id}.pdf")):
            pass
        else:
            download_arxiv(arxiv_id, cache_dir)
        file_path = os.path.join(cache_dir, f"{arxiv_id}.pdf")
        extractor = pdf_tool(file_path)
        sections = extractor.extract_sections_by_outline()
        return {paper['title']: sections}
    except Exception as e:
        print(f"Error processing {paper.get('title', 'Unknown')}: {str(e)}")
        return None

def down_and_chunk(state: RetrivalState) -> ChunkState:
    retrival_result_path = state['retrival_result_path']
    cache_dir = get_settings("config.yaml")['cache_dir']
    contents_path = state['task_dir']+"/contents.json"
    os.makedirs(cache_dir, exist_ok=True)
    papers = json.load(open(retrival_result_path,"r"))
    all_chunks = []
    print("------------------------------\n开始下载论文\n------------------------------")
    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=5) as executor:  # 可根据需要调整 max_workers
        futures = [executor.submit(process_paper, paper,cache_dir) for paper in papers]
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_chunks.append(result)
    print("------------------------------\n下载完成\n------------------------------")

    # 保存到文件
    final_chunks = {}
    for item in all_chunks:
        final_chunks.update(item)
    with open(contents_path, 'w') as file:
        json.dump(final_chunks, file)
    # 摘要和目录
    overview = get_retrival_overview(contents_path,retrival_result_path),
    print(type(overview))
    outState:  ChunkState = {
        "task_dir": state["task_dir"],
        "contents_path":contents_path,
        "overview":overview,
        "theme":state['theme'],
    }

    return outState



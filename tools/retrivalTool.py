import json

from torch import topk
from core.arxivLance import arxivSql
from core.settings import get_settings

settings = get_settings("config.yaml")["lancedb"]
try:
    db_uri = settings["db_uri"]
    table = settings["table"]
    mdb = arxivSql(db_uri=db_uri)
    mdb.connect(table_name=table)
except Exception as e:
    print(e)
def hybird_search_local(search,save_path,start_date=None,end_date=None,top_k:int=15):
    '''从本地数据库中检索，关键词搜索与语义搜索结合版，会自动存储检索结果
    参数：
        keywords:关键词，list类型，如["a","b","c"]
        search:查询语句，str类型
        start_date:检索开始日期，格式为"yyyy-mm-dd"，默认为None
        end_date:检索结束日期，格式为"yyyy-mm-dd"，默认为None
        top_k:检索结果数量，默认为5
        save_path: 保存路径
    返回：
        任务状态
    '''
    top_k = settings['retrieval']['top_k']
    ret1 =  mdb.search_by_vector(search,start_date, end_date, top_k)
    ret1 = ret1[['title', 'pdf_link', 'abstract']].to_json(orient = "records",force_ascii=False)
    ret = json.loads(ret1) 
    ret = list(set([tuple(d.items()) for d in ret]))
    ret = [dict(d) for d in ret]
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(ret, f, ensure_ascii=False, indent=4)
    return "检索结果已保存" 


def load_tools():
    return [hybird_search_local]
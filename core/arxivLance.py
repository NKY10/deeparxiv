import lancedb
from lancedb.pydantic import LanceModel,Vector
import pandas as pd
import pyarrow as pa
from datetime import datetime
from lancedb.embeddings import get_registry

embed = get_registry().get("ollama").create(name="bge-m3:latest")

class Arxiv(LanceModel):  
    title: str  
    pdf_link: str
    abstract: str
    keywords: list[str]
    summary: str = embed.SourceField()
    vector: Vector(embed.ndims()) = embed.VectorField()
    date: str


class arxivSql:
    def __init__(self, db_uri="arxivDB"):
        '''
            连接到lancedb
        '''
        self.db = lancedb.connect(uri=db_uri)
        self.table = None
    def _set_table(self, table_name: str):
        ''' 
            设置表名,一般不需要调用
        '''
        self.table_name = table_name
    def connect(self,table_name:str = "arxiv"):
        '''
            连接到table
            table_name: str, 表名
        '''
        self._set_table(table_name)
        self.table = self.db.create_table(self.table_name,schema=Arxiv,exist_ok=True)
    
    def insert_daily_papers(self, data: list):
        '''
            插入数据
            data: list, 数据列表，每个数据是字典
            return: None
        '''
        if self.table is None:
            self.connect()
        print("data is adding")
        self.table.add(data)
    
    
    def check_available_with_title(self, title: str):
        '''根据论文标题判断是否有该论文
        return:
            bool
        '''
        if self.table is None:
            self.connect()
        title = title.replace("'", "''")
        return len(self.table.search().where(f"title == '{title}'").to_pandas()) != 0
    

    def search_by_vector(self, query: str, start_date: str, end_date: str, top_k):
        '''
            根据向量检索
            query: str, 查询语句
            start_date: str, 开始日期
            end_date: str, 结束日期
            top_k: int, 返回数量
            return: pandas.DataFrame
        '''
        if self.table is None:
            self.connect()
        time_query = ""
        if start_date:
            time_query += f"(date >= '{start_date}')"
        if end_date:
            time_query += f"(date <= '{end_date}')"
        #print(time_query)
        if time_query == "":
            ret = self.table.search(query).limit(top_k).to_pandas()
        else:

            ret = self.table.search(query).where(time_query).limit(top_k).to_pandas()
        return ret
    
    def search_by_date(self, start_date: str, end_date: str):
        '''
            根据日期检索
            start_date: str, 开始日期
            end_date: str, 结束日期
            return: pandas.DataFrame
        '''
        if self.table is None:
            self.connect()
        if start_date and end_date:
            #print(f"(date >= '{start_date}') AND (date <= '{end_date}')")
            ret = self.table.search().where(f"(date >= '{start_date}') AND (date <= '{end_date}')",prefilter=True).to_pandas()
        else:
            ret = self.table.to_pandas()       
        return ret
        
    def search_by_words(self, words: list, start_date: str, end_date: str ,top_k: int = 5):
        '''
            根据关键词检索
            words: list, 关键词列表，传入参数的时候已经分割好了
            start_date: str, 开始日期
            end_date: str, 结束日期
            top_k: int, 返回数量
            return: pandas.DataFrame
        '''
        if self.table is None:
            self.connect()
        query = ""
        if start_date:
            query += f"(date >= '{start_date}') AND"
        if end_date:
            query += f"(date <= '{end_date}') AND"
        word_query =  " OR ".join([f"summary LIKE '%{word}%' OR abstract LIKE '%{word}%'" for word in words])
        query += f"({word_query})"
        #print(query)
        ret = self.table.search().where(query).limit(top_k).to_pandas()
        return ret

    def hybird_search(self, query: str, start_date: str, end_date: str, top_k: int = 5):
        '''
            混合检索
            query: str, 查询语句
            words: list, 关键词列表，传入参数的时候已经分割好了
            start_date: str, 开始日期
            end_date: str, 结束日期
            top_k: int, 返回数量
            return: pandas.DataFrame
        '''
        if self.table is None:
            self.connect()
        time_query = ""
        if start_date:
            time_query += f"(date >= '{start_date}')"
        if end_date:
            time_query += f"(date <= '{end_date}')"
        #print(time_query)
        self.table.create_fts_index("summary")


        if time_query == "":
            ret = self.table.search(
                    query,
                    query_type="hybrid",
                    vector_column_name='vector',
                    fts_columns='summary',
                ).limit(top_k).to_pandas()
        else:
            ret = self.table.search(
                    query,
                    query_type='hybird',
                    vector_column_name='vector',
                    fts_columns='summary',
                ).limit(top_k).where(time_query).limit(top_k).to_pandas()
        return ret

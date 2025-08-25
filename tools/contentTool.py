import json
def get_target_contents(index:dict,content_path:str):
    '''获取指定论文中指定章节的内容
    参数：
        index:指定论文的指定章节，类型dict
        example:
            {
                "title1":["目录1", "目录2", "目录3"],
                "title2":["目录1", "目录2", "目录3"]
            }
    返回：
        ret:指定论文中指定章节的内容，类型dict
    '''
    ret = {}
    contents = json.load(open(content_path))
    errors = ""
    for ind in index.keys():
        text = ""
        try:
            for content in index[ind]:
                text += contents[ind][content]
            ret[ind] = text
        except Exception as e:
            errors += str(e)
    return ret,errors

def load_tools():
    return [get_target_contents]
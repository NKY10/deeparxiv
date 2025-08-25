import yaml

def get_settings(path:str)->dict:
    '''从yaml文件中读取配置'''
    try:
        with open(path, 'r', encoding='utf-8') as file:
            # 使用 safe_load 是为了安全地加载 YAML 内容（避免执行恶意代码）
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"错误：文件 {path} 未找到。")
    except yaml.YAMLError as e:
        print(f"YAML 解析错误：{e}")
    
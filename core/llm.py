from langchain_openai import ChatOpenAI
from core.settings import get_settings



def get_llm(agent_name) -> ChatOpenAI:
    """获取不同agent的LLM配置"""
    settings = get_settings("config.yaml")
    agent_conf = settings['agents'].get(agent_name,"None")
    if agent_conf == "None":
        raise ValueError(f"{agent_name} not found in config.yaml")
    
    model_type = agent_conf.get("type", "default")
    if  model_type == "default":
        print(f"Warning：Using default model for '{agent_name}', because agent type was not set in config.yaml")

    temperature  = agent_conf.get("temperature",0.7)

    model_info = settings['models'].get(model_type,"default_model")
    if model_info == "default_model":
        model_info = settings['models']['default']
        print(f"Warning：Using default model for '{agent_name}', '{model_type}' not found in models，please check your config.yaml")
    return ChatOpenAI(
            temperature = temperature,
            model = model_info["model_name"],
            openai_api_key=model_info["api_key"],
            openai_api_base=model_info["base_url"]
        )

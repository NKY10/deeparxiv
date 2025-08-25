# deeparxiv — 基于 LangGraph 的自动化学术综述生成器

一个将“检索 → 下载/切分 PDF → 规划章节 → 逐章写作 → 导出 Markdown”串成流水线的开源项目。你只需给出主题，系统会在本地 LanceDB 论文库中检索相关论文，自动下载 PDF、按目录切分正文，基于摘要与目录规划综述结构，并调用工具按计划逐章写作，最终生成一篇结构化的中文学术综述。

## 核心特性
- 基于 LangGraph 的可视流水线：Starter → Retriever → Chunker → Planner → Writer → Saver（循环写作直至完成）
- 本地混合检索：向量检索（bge-m3 via Ollama）+ 字段过滤/全文索引（LanceDB）
- PDF 自动解析：依据 PDF 目录（outline）切分章节，遇到“References”自动终止正文提取
- 章节级写作代理：按规划逐章写作，调用工具精准抽取参考章节内容
- 可扩展配置：多模型/多代理配置，温度与基座模型可在配置中切换

## 工作流概览
```
START
  └─ stater → retriver → chunker → planner → writer ─┐
                                                     ├─(router)→ writer（未完成继续写）
                                                     └──────────→ saver → END
```
对应实现：
- Starter 初始化任务目录：agents/starter.py
- Retriever 本地检索并保存结果：agents/retriver.py + tools/retrivalTool.py
- Chunker 下载 PDF 并切分：agents/chunker.py + tools/chunkTool.py
- Planner 生成写作计划：agents/planner.py + prompts/prompt.py
- Writer 逐章写作并调用工具取材：agents/writer.py + tools/contentTool.py
- Saver 导出 Markdown：agents/saver.py
- 图编排：mgraph/graph.py；状态定义：mgraph/state.py

## 快速开始
1) 环境要求
- Python 3.10+
- macOS/Linux/Windows（开发环境在 macOS）
- 已安装并运行 Ollama，且已拉取 bge-m3 模型：
  - 安装并启动：参考 Ollama 官方文档
  - 拉取模型：`ollama pull bge-m3`

2) 安装依赖
```
pip install -r requirements.txt
```

3) 配置模型与路径
- 复制一份 config.yaml 并修改为你的本地配置：
  - models: 设置不同供应商的 base_url / model_name
  - agents: 为 retrivalAgent / planAgent / writeAgent 选择模型类型与温度
  - cache_dir: PDF 缓存目录
  - task_dir: 任务输出目录
  - lancedb: db_uri 与表名（默认 arxiv）


4) 准备 LanceDB 数据库
- 本项目默认从 LanceDB 检索论文数据（title、pdf_link、abstract、summary、date 等）。
- 你需要事先将论文元数据与摘要写入 LanceDB；示例（交互式 Python）：
```
from core.arxivLance import arxivSql
mdb = arxivSql(db_uri="arxivDB")
mdb.connect(table_name="arxiv")
# 注意：需包含 summary 字段以生成向量（内部会据此创建 vector）
mdb.insert_daily_papers([
  {"title":"...","pdf_link":"https://arxiv.org/pdf/xxxx.xxxxx.pdf",
   "abstract":"...","keywords":["..."],"summary":"...","date":"2025-06-01"}
])
```
- 若需混合检索（向量+全文），请确保已在 LanceDB 中创建 FTS 所需字段，详见 core/arxivLance.py。

5) 运行
- 修改 <项目根>/main.py 中的主题变量：
```
theme = "如何评估一个RAG系统"  # 改为你的主题
```
- 启动：
```
python main.py
```
- 运行过程中会自动：
  - 在 taskDir/ 下创建带时间戳的任务文件夹
  - 保存检索结果、PDF 切分结果（contents.json）、写作计划（*_plan.json）
  - 最终导出综述 Markdown 文件：<主题>.md

## 结果产物结构（示例）
```
/taskDir/
  └─ 如何评估一个RAG系统20250825201008/
       ├─ contents.json           # PDF 切分（按目录+正文）
       ├─ 如何评估一个RAG系统.json    # 检索结果（title/pdf_link/abstract）
       ├─ 如何评估一个RAG系统_plan.json
       └─ 如何评估一个RAG系统.md     # 最终综述
```

## 关键模块说明
- 检索与工具
  - tools/retrivalTool.py 提供 hybird_search_local（向量检索为主），结果写入 JSON
  - core/arxivLance.py 封装 LanceDB 的建表、插入与搜索
- PDF 切分
  - tools/chunkTool.PDFContentExtractor 基于 PDF 目录切分
  - 命中“References/REFERENCES”时停止提取正文
- 规划与写作
  - prompts/prompt.py 中包含检索、规划、写作提示词
  - writer 会按计划循环写作，使用 tools/contentTool.get_target_contents 获取所需章节
- 模型调用
  - core/llm.py 使用 langchain-openai ChatOpenAI 接口，读取 config.yaml 的模型配置
  - 可以根据自己的api设置其他接口

## 常见问题与提示
- LanceDB 向量检索依赖 Ollama 的 bge-m3，请确保服务可用且模型已就绪
- PDF 必须能正确解析目录（outline）；无目录的 PDF 将难以切分
- config.yaml 中的 API Key 仅示意，开源前请移除敏感信息，使用本地私有配置
- arxiv 下载失败会自动重试；.arxivCache 为 PDF 缓存目录

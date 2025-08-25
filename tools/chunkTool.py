import PyPDF2
from PyPDF2 import errors
import re
from typing import Dict, List, Optional

class PDFContentExtractor:
    """
    用于从PDF文件中提取目录结构和对应内容的类，支持在遇到 "reference"（不区分大小写）时停止提取正文。
    """

    def __init__(self, file_path: str):
        """
        初始化PDF内容提取器
        
        参数:
            file_path: PDF文件路径
        """
        self.file_path = file_path
        self.reader = None
        self.full_text = ""
        self.sections = {}
        self.reference_pattern = re.compile(r'references', re.IGNORECASE)  # 不区分大小写的 reference 匹配

        try:
            self.reader = PyPDF2.PdfReader(file_path)
            self._extract_full_text()
        except FileNotFoundError:
            raise FileNotFoundError(f"文件未找到: {file_path}")
        except errors.PdfReadError:
            raise ValueError(f"无法读取PDF文件: {file_path}")
        except Exception as e:
            raise RuntimeError(f"初始化PDF阅读器时发生错误: {str(e)}")

    def _extract_full_text(self) -> None:
        """提取PDF中的所有文本内容"""
        self.full_text = ""
        try:
            for page in self.reader.pages:
                page_text = page.extract_text()
                if page_text:
                    self.full_text += page_text
        except Exception as e:
            raise RuntimeError(f"提取PDF文本时发生错误: {str(e)}")

    def _extract_outline_titles(self) -> List[str]:
        """
        递归提取PDF书签/目录中的标题
        
        返回:
            标题字符串列表
        """
        if not hasattr(self.reader, 'outline') or not self.reader.outline:
            return []

        items = []

        def recursive_extract(element) -> None:
            if isinstance(element, dict):
                if '/Title' in element:
                    title = element['/Title']
                    if title and isinstance(title, str):
                        items.append(title)
                for value in element.values():
                    recursive_extract(value)
            elif isinstance(element, (list, tuple)):
                for item in element:
                    recursive_extract(item)

        try:
            recursive_extract(self.reader.outline)
            return items
        except Exception as e:
            raise RuntimeError(f"提取目录结构时发生错误: {str(e)}")

    def extract_sections_by_outline(self) -> Dict[str, str]:
        """
        根据目录结构提取对应的内容段落，并在遇到 'reference' 时停止提取
        
        返回:
            字典: {标题: 内容}
        """
        if not self.full_text:
            return {}

        titles = self._extract_outline_titles()
        if not titles:
            return {}

        self.sections = {}

        try:
            for i in range(len(titles)):
                title = titles[i]
                start_pos = self.full_text.find(title)

                if start_pos == -1:
                    continue

                start_pos += len(title)  # 将起始位置移至标题之后

                # 设置初始 end_pos 为无穷大
                end_pos = float('inf')

                # 1. 检查下一个目录标题的位置
                if i < len(titles) - 1:
                    next_title = titles[i + 1]
                    next_title_pos = self.full_text.find(next_title, start_pos)
                    if next_title_pos != -1:
                        end_pos = next_title_pos

                # 2. 检查 reference 的位置（不区分大小写）
                reference_match = self.reference_pattern.search(self.full_text, start_pos)
                if reference_match:
                    reference_pos = reference_match.start()
                    if reference_pos < end_pos:
                        end_pos = reference_pos

                # 3. 确定最终的 end_pos
                if end_pos != float('inf'):
                    content = self.full_text[start_pos:end_pos]
                else:
                    content = self.full_text[start_pos:]

                self.sections[title] = content.strip()

            return self.sections
        except Exception as e:
            raise RuntimeError(f"提取内容段落时发生错误: {str(e)}")

    def get_section_content(self, title: str) -> Optional[str]:
        """
        获取指定标题的内容
        
        参数:
            title: 要查找的标题
            
        返回:
            如果找到则返回内容字符串，否则返回None
        """
        return self.sections.get(title, None)

    def get_all_sections(self) -> Dict[str, str]:
        """
        获取所有提取的内容段落
        
        返回:
            字典: {标题: 内容}
        """
        return self.sections

    def get_page_count(self) -> int:
        """
        获取PDF页数
        
        返回:
            PDF文件的总页数
        """
        return len(self.reader.pages) if self.reader else 0
from langchain.agents import Tool
import os
import glob

class DocumentSkill:
    def __init__(self, rag_service):
        self.rag_service = rag_service
    
    def get_tools(self):
        """获取文档处理相关的工具"""
        tools = [
            Tool(
                name="加载文档",
                func=self.load_documents,
                description="用于从docs目录加载文档到知识库。当需要批量导入文档时使用。"
            ),
            Tool(
                name="列出文档",
                func=self.list_documents,
                description="用于列出docs目录中的所有文档。当需要查看可用文档时使用。"
            )
        ]
        return tools
    
    def load_documents(self, _):
        """加载docs目录中的所有文档"""
        docs_dir = "docs"
        if not os.path.exists(docs_dir):
            return "docs目录不存在"
        
        documents = []
        for file_path in glob.glob(f"{docs_dir}/*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.rag_service.add_document(content, {"source": file_path})
                    documents.append(os.path.basename(file_path))
            except Exception as e:
                return f"加载文档时出错: {str(e)}"
        
        if documents:
            return f"成功加载了以下文档: {', '.join(documents)}"
        else:
            return "没有找到文档"
    
    def list_documents(self, _):
        """列出docs目录中的所有文档"""
        docs_dir = "docs"
        if not os.path.exists(docs_dir):
            return "docs目录不存在"
        
        documents = []
        for file_path in glob.glob(f"{docs_dir}/*.md"):
            documents.append(os.path.basename(file_path))
        
        if documents:
            return f"可用文档: {', '.join(documents)}"
        else:
            return "docs目录为空"

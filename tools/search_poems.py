import os
from typing import List, Dict
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

class PoemSearcher:
    def __init__(self):
        # 初始化 Ollama 和 Qdrant 配置
        self.ollama_url = os.getenv('OLLAMA_API_URL')
        self.model_name = "viosay/conan-embedding-v1"
        self.client = QdrantClient(
            url=os.getenv('QDRANT_URL'),
            api_key=os.getenv('QDRANT_API_KEY')
        )
        self.collection_name = "poems_analysis"

    def get_embedding(self, text: str) -> List[float]:
        """使用 Ollama API 生成文本的向量表示"""
        response = requests.post(
            f"{self.ollama_url}/api/embeddings",
            json={
                "model": self.model_name,
                "prompt": text
            }
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索相似的诗词
        :param query: 搜索查询文本
        :param limit: 返回结果数量
        :return: 匹配结果列表
        """
        # 生成查询向量
        try:
            query_vector = self.get_embedding(query)
            
            # 执行向量搜索
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            # 格式化结果
            results = []
            for hit in search_results:
                formatted_result = {
                    "score": round(hit.score, 3),
                    "title": hit.payload['title'],
                    "author": hit.payload['author'],
                    "content": hit.payload['content'],
                    "analysis": {
                        "theme": hit.payload['theme'],
                        "core_idea": hit.payload['core_idea'],
                        "applicable_scenario": hit.payload['applicable_scenario'],
                        "modern_significance": hit.payload['modern_significance']
                    }
                }
                results.append(formatted_result)
            
            return results
        except Exception as e:
            print(f"搜索详细错误: {str(e)}")
            raise

    def format_result(self, result: Dict) -> str:
        """
        格式化单个搜索结果
        """
        return f"""
相似度: {result['score']}
标题: {result['title']}
作者: {result['author']}
原文: {result['content']}
---分析---
主题: {result['analysis']['theme']}
核心思想: {result['analysis']['core_idea']}
适用场景: {result['analysis']['applicable_scenario']}
现代意义: {result['analysis']['modern_significance']}
{'='*50}
"""

def main():
    searcher = PoemSearcher()
    
    while True:
        print("\n请输入您的查询需求（输入 'q' 退出）：")
        query = input().strip()
        
        if query.lower() == 'q':
            break
            
        try:
            print("\n搜索中...\n")
            results = searcher.search(query)
            
            if not results:
                print("未找到相关结果。")
                continue
                
            print(f"找到 {len(results)} 个相关结果：\n")
            for result in results:
                print(searcher.format_result(result))
                
        except Exception as e:
            print(f"搜索程中发生错误: {e}")

if __name__ == "__main__":
    main() 
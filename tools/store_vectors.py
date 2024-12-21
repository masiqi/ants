import json
import os
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import time
from typing import List
import uuid
import requests

# 加载环境变量
load_dotenv()

# 初始化 Ollama 配置
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL')
MODEL_NAME = "viosay/conan-embedding-v1"

# 初始化 Qdrant 客户端
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
COLLECTION_NAME = "poems_analysis"

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60
)

def get_embedding(text: str) -> List[float]:
    """使用 Ollama API 生成文本的向量表示"""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/embeddings",
            json={
                "model": MODEL_NAME,
                "prompt": text
            }
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"生成向量时发生错误: {str(e)}")
        raise

def init_collection(vector_size: int):
    """初始化或重置集合"""
    try:
        collections = client.get_collections().collections
        exists = any(col.name == COLLECTION_NAME for col in collections)

        if exists:
            print(f"集合 {COLLECTION_NAME} 已存在，获取详细信息...")
            collection_info = client.get_collection(COLLECTION_NAME)
            print(f"当前集合信息: 向量维度={collection_info.config.params.vectors.size}, 点数={collection_info.points_count}")
            return

        print(f"创建新集合 {COLLECTION_NAME}，向量维度: {vector_size}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        print("集合创建成功")
    except Exception as e:
        print(f"初始化集合时发生错误: {str(e)}")
        raise

def process_jsonl_file(file_path):
    """处理JSONL文件并存储向量"""
    print(f"开始读取文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        poems = [json.loads(line) for line in file]
    print(f"读取完成，共 {len(poems)} 条记录")

    points = []
    current_batch = []
    batch_count = 0
    vector_size = None
    processed_count = 0
    skipped_count = 0
    batch_size = 100

    for i, poem in enumerate(tqdm(poems, desc="处理诗词")):
        try:
            if poem.get('kind_cn') != '诗':
                skipped_count += 1
                continue

            analysis = poem.get('analysis', {})
            if not all(key in analysis for key in ['theme', 'core_idea', 'applicable_scenario', 'modern_significance']):
                print(f"跳过第 {i} 首诗：缺少必要的分析字段 - {poem.get('title', 'unknown')}")
                skipped_count += 1
                continue

            combined_text = f"""
            主题：{analysis['theme']}
            核心思想：{analysis['core_idea']}
            适用场景：{analysis['applicable_scenario']}
            现代意义：{analysis['modern_significance']}
            """

            vector = get_embedding(combined_text)
            if vector_size is None:
                vector_size = len(vector)
                print(f"向量维度确定: {vector_size}")
                init_collection(vector_size)

            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "original_id": str(poem.get('id', str(i))),
                    "title": str(poem.get('title', '')),
                    "content": str(poem.get('content', '')),
                    "author": str(poem.get('author', '')),
                    "theme": str(analysis.get('theme', '')),
                    "core_idea": str(analysis.get('core_idea', '')),
                    "applicable_scenario": str(analysis.get('applicable_scenario', '')),
                    "modern_significance": str(analysis.get('modern_significance', ''))
                }
            )
            current_batch.append(point)
            processed_count += 1

            if len(current_batch) >= batch_size:
                print(f"处理进度: {processed_count}/{len(poems)} (跳过: {skipped_count})")
                try:
                    client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=current_batch
                    )
                    points.extend(current_batch)
                    print(f"成功上传第 {batch_count} 批数据（{len(current_batch)} 条记录）")
                except Exception as e:
                    print(f"上传第 {batch_count} 批数据失败: {str(e)}")
                    return
                current_batch = []
                batch_count += 1
                time.sleep(1)  # 添加延迟避免 API 限制

        except Exception as e:
            print(f"处理第 {i} 首诗时发生错误: {str(e)}")
            continue

    # 处理最后一批数据
    if current_batch:
        print(f"处理最后一批数据: {len(current_batch)} 条记录")
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=current_batch
            )
            points.extend(current_batch)
            print("最后一批数据上传成功")
        except Exception as e:
            print(f"上传最后一批数据失败: {str(e)}")

    print(f"处理完成：")
    print(f"- 总记录数: {len(poems)}")
    print(f"- 成功处理: {len(points)}")
    print(f"- 跳过记录: {skipped_count}")

def main():
    input_file = "/tmp/output_file.jsonl"
    if not os.path.exists(input_file):
        print(f"找不到输入文件: {input_file}")
        return

    print("开始处理诗词分析数据...")
    start_time = time.time()
    process_jsonl_file(input_file)
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f}秒")

    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"\n最终集合统计信息:")
        print(f"- 总条数: {collection_info.points_count}")
        print(f"- 向量维度: {collection_info.config.params.vectors.size}")
    except Exception as e:
        print(f"获取集合信息时发生错误: {str(e)}")

if __name__ == "__main__":
    main() 
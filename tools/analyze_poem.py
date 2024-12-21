import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 从.env文件中加载环境变量
load_dotenv()

# 获取base_url和model的名字
base_url = os.getenv('OLLAMA_BASE_URL')
model_name = os.getenv('OLLAMA_MODEL_NAME')

if not base_url or not model_name:
    print('请确保.env文件中包含OLLAMA_BASE_URL和OLLAMA_MODEL_NAME。')
    exit(1)

# 初始化OpenAI客户端
client = OpenAI(api_key="key",base_url=base_url)

def analyze_poem(content):
    prompt = f"""分析以下诗词，并以JSON格式返回以下信息：
    {{
        "theme": "诗词的主要主题",
        "core_idea": "诗词表达的核心思想",
        "applicable_scenario": "适合在什么场景下引用",
        "modern_significance": "与现代生活的联系"
    }}
    
    诗词内容：{content}"""
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一个专业的古诗词分析专家，请以JSON格式回复，必须使用英文键名。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        result = response.choices[0].message.content.strip()
        # 替换可能出现的中文键名
        result = (result.replace('"主题":', '"theme":')
                       .replace('"核心思想":', '"core_idea":')
                       .replace('"适用场景":', '"applicable_scenario":')
                       .replace('"现代意义":', '"modern_significance":'))
        return json.loads(result)
    except Exception as e:
        print(f'分析诗词时发生错误: {e}')
        return None

# 读取JSON文件
json_file_path = '/tmp/works.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    poems_data = json_data.get('works', [])

# 确保输入数据是列表
if not isinstance(poems_data, list):
    poems_data = [poems_data]

# 处理每首诗
output_file_path = '/tmp/output_file.jsonl'
total_poems = len(poems_data)

for index, poem in enumerate(poems_data, 1):
    print(f'\r处理进度: {index}/{total_poems} ({(index/total_poems*100):.1f}%)', end='')
    
    if len(poem.get('content', '')) <= 200:
        analysis_result = analyze_poem(poem['content'])
        if analysis_result:
            result_data = {
                **poem,
                'analysis': analysis_result
            }
            # 立即写入JSONL文件
            with open(output_file_path, 'a', encoding='utf-8') as output_file:
                json.dump(result_data, output_file, ensure_ascii=False)
                output_file.write('\n')
    else:
        print(f'\n跳过分析：content超过200字 - {poem.get("content", "")[:30]}...')

print(f'\n分析完成，结果已保存到 {output_file_path}')

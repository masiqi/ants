export class VectorService {
  private ollamaUrl: string;
  private modelName = 'viosay/conan-embedding-v1';

  constructor(private env: { OLLAMA_API_URL: string }) {
    this.ollamaUrl = env.OLLAMA_API_URL;
  }

  async textToVector(text: string): Promise<number[]> {
    try {
      console.log('生成向量，输入文本:', text);
      
      const response = await fetch(`${this.ollamaUrl}/api/embeddings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.modelName,
          prompt: text
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Ollama service error: ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      const vector = data.embedding;
      
      // 输出一些调试信息
      console.log('向量生成成功:');
      console.log('- 维度:', vector.length);
      console.log('- 前5个值:', vector.slice(0, 5));
      
      return vector;
    } catch (error) {
      console.error('向量生成错误:', error);
      throw error;
    }
  }
} 
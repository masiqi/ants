import { QdrantClient } from '@qdrant/js-client-rest'
import { SearchResult, SearchOptions } from './types'

export class QdrantService {
  private client: QdrantClient
  private readonly collectionName = 'poems_analysis'

  constructor(env: { QDRANT_URL: string; QDRANT_API_KEY: string }) {
    this.client = new QdrantClient({
      url: env.QDRANT_URL,
      apiKey: env.QDRANT_API_KEY
    })
  }

  async searchVectors(queryVector: number[], options: SearchOptions = {}): Promise<SearchResult[]> {
    try {
      const { limit = 5, minScore = 0 } = options

      const searchResult = await this.client.search(this.collectionName, {
        vector: queryVector,
        limit,
        score_threshold: minScore
      })

      return searchResult.map(hit => ({
        id: hit.payload.original_id as string,
        title: hit.payload.title as string,
        author: hit.payload.author as string,
        content: hit.payload.content as string,
        analysis: {
          theme: hit.payload.theme as string,
          core_idea: hit.payload.core_idea as string,
          applicable_scenario: hit.payload.applicable_scenario as string,
          modern_significance: hit.payload.modern_significance as string
        },
        score: hit.score
      }))
    } catch (error) {
      console.error('Qdrant search error:', error)
      throw error
    }
  }

  // 添加其他向量操作方法
  async addVector(data: any): Promise<void> {
    // 实现添加向量的逻辑
  }

  async updateVector(id: string, data: any): Promise<void> {
    // 实现更新向量的逻辑
  }

  async deleteVector(id: string): Promise<void> {
    // 实现删除向量的逻辑
  }
} 
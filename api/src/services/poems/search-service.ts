import { SearchResult, SearchOptions } from './types'
import { QdrantService } from './qdrant-service'
import { VectorService } from './vector-service'

export class PoemSearchService {
  private qdrantService: QdrantService
  private vectorService: VectorService

  constructor(env: { 
    QDRANT_URL: string; 
    QDRANT_API_KEY: string;
    OLLAMA_API_URL: string;
  }) {
    this.qdrantService = new QdrantService(env)
    this.vectorService = new VectorService(env)
  }

  async searchVectors(query: string, options: SearchOptions = {}): Promise<SearchResult[]> {
    try {
      console.log('Starting vector search for query:', query)
      const queryVector = await this.vectorService.textToVector(query)
      console.log('Vector generated, searching Qdrant...')
      const results = await this.qdrantService.searchVectors(queryVector, options)
      console.log(`Found ${results.length} results`)
      return results
    } catch (error) {
      console.error('Search error:', error)
      throw error
    }
  }

  async addPoem(data: any): Promise<void> {
    await this.qdrantService.addVector(data)
  }

  async updatePoem(id: string, data: any): Promise<void> {
    await this.qdrantService.updateVector(id, data)
  }

  async deletePoem(id: string): Promise<void> {
    await this.qdrantService.deleteVector(id)
  }
} 
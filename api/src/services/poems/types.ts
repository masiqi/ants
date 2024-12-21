export interface Poem {
  id: string
  title: string
  author: string
  content: string
  analysis: PoemAnalysis
}

export interface PoemAnalysis {
  theme: string
  core_idea: string
  applicable_scenario: string
  modern_significance: string
}

export interface SearchResult extends Poem {
  score: number
}

export interface SearchOptions {
  limit?: number
  minScore?: number
} 
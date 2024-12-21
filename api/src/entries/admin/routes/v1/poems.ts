import { Hono } from 'hono'
import { PoemSearchService } from '../../../../services/poems'

const poems = new Hono<{ Bindings: { VECTOR_SEARCH_API_URL: string } }>()

poems.post('/search', async (c) => {
  const searchService = new PoemSearchService(c.env)
  const { query, options, debug } = await c.req.json()
  
  const results = await searchService.searchVectors(query, options)
  
  return c.json({
    success: true,
    data: results,
    debug: debug ? {
      vector_details: true,
      query_vector: [],
      raw_scores: []
    } : undefined
  })
})

export default poems 
import { Hono } from 'hono'
import { PoemSearchService } from '../../../../services/poems'

const poems = new Hono<{ Bindings: { VECTOR_SEARCH_API_URL: string } }>()

poems.post('/search', async (c) => {
  const searchService = new PoemSearchService(c.env)
  const { query, parameters } = await c.req.json()
  
  const results = await searchService.searchVectors(query, parameters)
  
  return c.json({
    response_type: 'poems_search',
    data: results,
    metadata: {
      total: results.length,
      query_time: Date.now()
    }
  })
})

export default poems 
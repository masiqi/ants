import { Hono } from 'hono'
import { PoemSearchService } from '../../../../services/poems'

const poems = new Hono<{ Bindings: { VECTOR_SEARCH_API_URL: string } }>()

// 语义搜索
poems.get('/search', async (c) => {
  const searchService = new PoemSearchService(c.env)
  const query = c.req.query('q')
  const limit = parseInt(c.req.query('limit') || '5')

  if (!query) {
    return c.json({ 
      success: false, 
      error: 'Query parameter is required' 
    }, 400)
  }

  try {
    const results = await searchService.searchVectors(query, { limit })
    return c.json({ success: true, data: results })
  } catch (error) {
    return c.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, 500)
  }
})

// 主题搜索
poems.get('/theme/:theme', async (c) => {
  const searchService = new PoemSearchService(c.env)
  const theme = c.req.param('theme')
  const limit = parseInt(c.req.query('limit') || '5')

  try {
    const results = await searchService.searchVectors(`主题：${theme}`, { limit })
    return c.json({ success: true, data: results })
  } catch (error) {
    return c.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, 500)
  }
})

// 场景搜索
poems.get('/scenario/:scenario', async (c) => {
  const searchService = new PoemSearchService(c.env)
  const scenario = c.req.param('scenario')
  const limit = parseInt(c.req.query('limit') || '5')

  try {
    const results = await searchService.searchVectors(`场景：${scenario}`, { limit })
    return c.json({ success: true, data: results })
  } catch (error) {
    return c.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, 500)
  }
})

export default poems 
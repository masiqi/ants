import { Hono } from 'hono'
import { cors } from 'hono/cors'
import poems from './routes/v1/poems'

const app = new Hono<{ Bindings: { VECTOR_SEARCH_API_URL: string } }>()

app.use('*', cors())
app.route('/v1/admin/poems', poems)
app.get('/health', (c) => c.json({ status: 'ok' }))

export default app 
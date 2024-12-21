import { Hono } from 'hono'
import { cors } from 'hono/cors'
import poems from './entries/services/routes/v1/poems'
import type { CloudflareBindings } from './types/bindings'

const app = new Hono<{ Bindings: CloudflareBindings }>()

// 全局中间件
app.use('*', cors())

// 路由分组
app.route('/v1/services/poems', poems)

// 健康检查
app.get('/health', (c) => c.json({ status: 'ok' }))

export default app
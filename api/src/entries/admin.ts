import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { adminRoutes } from '../routes/v1/admin'
import { authMiddleware } from '../middlewares/auth'

const app = new Hono<{ Bindings: CloudflareBindings }>()

app.use('*', cors())
app.use('*', authMiddleware()) // 管理接口需要认证
app.route('/v1/admin', adminRoutes)
app.get('/health', (c) => c.json({ status: 'ok' }))

export default app 
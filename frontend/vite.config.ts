import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量 - 从项目根目录加载
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '')
  
  // 从环境变量获取端口配置，如果没有则使用默认值
  const frontendPort = parseInt(env.FRONTEND_DEV_PORT || '5173')
  const backendPort = parseInt(env.BACKEND_DEV_PORT || '8000')
  const apiBaseUrl = env.VITE_API_BASE_URL || `http://localhost:${backendPort}/api`

  console.log('Vite Config - Environment Variables:')
  console.log(`  FRONTEND_DEV_PORT: ${frontendPort}`)
  console.log(`  BACKEND_DEV_PORT: ${backendPort}`)
  console.log(`  API Base URL: ${apiBaseUrl}`)

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: frontendPort,
      proxy: {
        '/api': {
          target: apiBaseUrl.replace('/api', ''),
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      }
    },
    // 确保字体文件正确处理
    assetsInclude: ['**/*.woff2', '**/*.woff', '**/*.ttf', '**/*.eot'],
    build: {
      rollupOptions: {
        output: {
          assetFileNames: (assetInfo) => {
            if (assetInfo.name && /\.(woff2?|ttf|eot)$/.test(assetInfo.name)) {
              return 'fonts/[name][extname]'
            }
            return 'assets/[name]-[hash][extname]'
          }
        }
      }
    }
  }
})

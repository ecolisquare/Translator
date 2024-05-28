import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { createProxyMiddleware } from 'http-proxy-middleware';
// export default defineConfig({
//   plugins: [react()],
//   // server: {
//   //   port: 5173,
//   //   proxy: {
//   //     '/auth': {
//   //       target: 'https://www.baidu.com/',
//   //       changeOrigin: true,
//   //       rewrite: (path) => path.replace(/^\/auth/, '/auth')
//   //     }
//   //   }
//   // }
// });

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
})

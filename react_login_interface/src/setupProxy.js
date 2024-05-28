const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  console.log('Setting up proxy');
  app.use(
    '/auth', // 代理的路径
    createProxyMiddleware({
      target: 'http://10.219.227.52:5000', // 目标服务器
      changeOrigin: true, // 更改请求源
    })
  );
};

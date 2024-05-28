const {createProxyMiddleware} = require('http-proxy-middleware');
module.exports = function(app) {
  app.use('/auth/login', createProxyMiddleware(
    {
        target: "http://10.219.227.52:5000",
        changeOrigin: true,
    }));
    // app.use(createProxyMiddleware('/continue_fine_tune_model', 
    // {
    //     "target": "http://10.219.227.52:5000"
    // }));
    // app.use(createProxyMiddleware('/register_model', 
    // {
    //     "target": "http://10.219.227.52:5000"
    // }));
}
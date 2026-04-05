export default {
  base: './',
  server: {
    host: true,
    port: 5173,
    allowedHosts: ['www.chillgame.kiwi', 'chillgame.kiwi'],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8050',
        changeOrigin: true,
      },
    },
  }
}

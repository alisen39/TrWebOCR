module.exports = {
  // publicPath :'/vue/'
  outputDir: '../backend/dist/TrWebOcr_fontend',
  // productionSourceMap: true,
  configureWebpack: {
    devtool: 'source-map'
  },
  devServer: {
    proxy:{
      '/api':{
        target: 'http://' + process.env.PROXY,
        changeOrigin:true,
      }
    }

  },

}
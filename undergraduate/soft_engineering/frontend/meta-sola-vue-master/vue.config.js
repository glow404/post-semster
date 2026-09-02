const { defineConfig } = require('@vue/cli-service')




module.exports = defineConfig({
    transpileDependencies: true,
    //取消检查本机访问
    devServer: {
        historyApiFallback: true,
        allowedHosts: "all",
    }
})
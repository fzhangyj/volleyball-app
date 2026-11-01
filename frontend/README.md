# 前端运行配置

本目录是 HBuilderX UniApp（Vue 3）项目。通过 HBuilderX 运行 H5、小程序或 App。

复制 `.env.example` 为 `.env`，将 `VITE_API_ORIGIN` 设置为手机或浏览器能访问的后端 origin（协议、主机、端口，不带 `/api/v1`），然后重新构建。例如局域网调试时使用开发机的局域网地址。所有接口、头像和首页相对媒体地址使用同一个配置。

H5 可以将 `VITE_API_ORIGIN` 留空，前提是 Web 服务器已将同源 `/api/v1` 请求代理到后端。小程序/App 必须填写完整后端 origin；微信小程序还需配置合法请求域名。

不依赖 HBuilderX 的检查：

```powershell
node --experimental-vm-modules smoke_test.mjs
```

检查页面脚本语法、路由目标、API/媒体地址和返回导航逻辑；不替代 HBuilderX 构建、浏览器或真机验证。

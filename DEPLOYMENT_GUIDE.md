# 🚀 Twitter Video Downloader 部署指南

## 推荐方案: Vercel 部署 ⭐⭐⭐⭐⭐

### 为什么选择 Vercel？
- ✅ **原生Python支持** - 无需修改后端代码
- ✅ **零配置部署** - 自动检测并构建
- ✅ **免费额度充足** - 个人项目完全够用
- ✅ **全球CDN** - 访问速度快
- ✅ **自动HTTPS** - 安全性保障
- ✅ **GitHub集成** - 推送即部署

## 📁 文件结构调整

```
xvideodownloader/
├── api/                    # Serverless Functions
│   ├── download.py        # 下载API
│   └── health.py         # 健康检查
├── static/               # 静态文件
│   ├── index.html       # 主页
│   └── styles.css       # 样式
├── vercel.json          # Vercel配置
├── requirements.txt     # Python依赖
└── README.md           # 说明文档
```

## 🔧 部署步骤

### 1. 准备GitHub仓库
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/twitter-video-downloader.git
git push -u origin main
```

### 2. 连接Vercel
1. 访问 [vercel.com](https://vercel.com)
2. 用GitHub账号登录
3. 点击 "New Project"
4. 选择你的GitHub仓库
5. 点击 "Deploy"

### 3. 环境变量配置（如需要）
在Vercel面板中设置:
```
PYTHON_VERSION=3.9
```

### 4. 自定义域名（可选）
1. 在Vercel项目设置中
2. 添加 Custom Domain
3. 配置DNS指向Vercel

## 🌐 API端点

部署后的API地址：
- **主页**: `https://your-app.vercel.app/`
- **下载API**: `https://your-app.vercel.app/api/download`
- **健康检查**: `https://your-app.vercel.app/api/health`

## ⚠️ 注意事项

### 1. 依赖限制
- Vercel对包大小有限制（250MB）
- yt-dlp包比较大，可能需要优化

### 2. 执行时间限制
- 免费版限制10秒执行时间
- Pro版限制60秒
- 对于大视频可能超时

### 3. 替代方案配置

#### 方案A: Railway（推荐备选）
```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录并部署
railway login
railway init
railway up
```

#### 方案B: Render
1. 连接GitHub仓库到 [render.com](https://render.com)
2. 选择 "Web Service"
3. 设置构建命令: `pip install -r requirements.txt`
4. 设置启动命令: `python app.py`

## 🔄 Cloudflare 部署（高级）

### 前端部署: Cloudflare Pages
```bash
# 安装Wrangler CLI
npm install -g wrangler

# 部署静态文件
wrangler pages publish static
```

### 后端部署: Cloudflare Workers
需要将Python代码改写为JavaScript:

```javascript
// worker.js
import { TwitterApi } from 'twitter-api-v2';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    if (url.pathname === '/api/download') {
      // 处理下载请求的JavaScript代码
      return new Response(JSON.stringify({
        message: "Twitter video info"
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Not found', { status: 404 });
  }
}
```

## 📊 平台对比

| 特性 | Vercel | Railway | Render | Cloudflare |
|------|--------|---------|---------|-------------|
| **Python支持** | ✅ Serverless | ✅ 完整 | ✅ 完整 | ❌ 需重写 |
| **免费额度** | 很大 | 有限 | 中等 | 很大 |
| **配置复杂度** | 低 | 低 | 中 | 高 |
| **性能** | 优秀 | 优秀 | 良好 | 优秀 |
| **扩展性** | 自动 | 手动 | 自动 | 手动 |

## 🎯 最终推荐

1. **首选: Vercel** - 配置简单，性能优秀
2. **备选: Railway** - 如果需要持久化存储
3. **预算充足: Render Pro** - 稳定可靠
4. **技术挑战: Cloudflare** - 需要重写后端

## 🚨 部署后检查

1. 访问首页确认界面正常
2. 测试API端点响应
3. 验证视频下载功能
4. 检查错误处理
5. 测试移动端兼容性

## 📞 技术支持

如果遇到部署问题:
1. 检查构建日志
2. 验证依赖安装
3. 确认API路径正确
4. 查看Vercel文档 
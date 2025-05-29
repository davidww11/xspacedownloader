# Twitter Video Downloader - 自实现版本

一个自己实现的Twitter/X视频下载工具，参考了[x-downloader.com](https://x-downloader.com/)的交互设计。

## 🚀 特性

- ✅ 现代化的UI界面，参考x-downloader.com设计
- ✅ 支持Twitter/X视频链接
- ✅ 多种质量选项
- ✅ MP4和MP3格式支持
- ✅ 响应式设计，移动端友好
- ✅ 实时下载进度显示
- ✅ 错误处理和用户反馈

## 📋 系统要求

- Python 3.8+
- pip (Python包管理器)

## ⚡ 快速开始

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python run.py
```

或直接运行主应用：

```bash
python app.py
```

### 3. 访问网站

打开浏览器访问: http://localhost:5000

## 📁 项目结构

```
xvideodownloader/
├── index.html          # 前端页面
├── styles.css          # 样式文件
├── app.py             # Flask后端API
├── run.py             # 启动脚本
├── requirements.txt    # Python依赖
└── README_SETUP.md    # 安装说明
```

## 🛠️ 使用方法

1. 在输入框中粘贴Twitter/X视频链接
   - 支持格式: `https://twitter.com/user/status/123456789`
   - 支持格式: `https://x.com/user/status/123456789`
   - 支持格式: `https://t.co/shortlink`

2. 选择下载格式 (MP4视频 或 MP3音频)

3. 点击"Download Video"按钮

4. 等待视频信息加载

5. 选择合适的质量选项并下载

## 🔧 技术栈

### 前端
- HTML5 + CSS3 + JavaScript
- 响应式设计
- 现代化UI组件

### 后端
- **Python Flask** - Web框架
- **yt-dlp** - 视频提取库
- **Flask-CORS** - 跨域支持

## 📚 API 文档

### POST /api/download

下载Twitter视频信息

**请求体:**
```json
{
  "url": "https://twitter.com/user/status/123456789",
  "format": "mp4"
}
```

**响应:**
```json
{
  "title": "视频标题",
  "author": "@用户名",
  "duration": "00:30",
  "thumbnail": "缩略图URL",
  "formats": [
    {
      "format_id": "720p",
      "url": "下载链接",
      "ext": "mp4",
      "quality": "720p HD",
      "filesize": "2.5 MB",
      "filename": "video.mp4"
    }
  ]
}
```

### GET /api/health

健康检查端点

## 🚨 注意事项

1. **版权声明**: 请仅下载您拥有版权或有权下载的视频
2. **使用条款**: 请遵守Twitter的使用条款
3. **网络环境**: 确保网络连接稳定，某些地区可能需要VPN
4. **依赖安装**: 首次运行前请确保安装所有Python依赖

## 🐛 故障排除

### 常见问题

**1. ModuleNotFoundError: No module named 'flask'**
```bash
pip install -r requirements.txt
```

**2. 无法提取视频信息**
- 检查URL格式是否正确
- 确认视频确实存在
- 检查网络连接

**3. CORS错误**
- 确保前端和后端在同一域名或已配置CORS

**4. 端口被占用**
```bash
# 查看端口使用情况
lsof -i :5000

# 或使用其他端口
PORT=8000 python run.py
```

## 🔒 安全性

- 所有下载链接都是临时的
- 不存储用户数据
- 仅提取公开可访问的视频信息

## 📱 浏览器支持

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## 🎨 界面预览

界面设计参考了x-downloader.com，包含：
- 清晰的输入区域
- 加载状态指示
- 视频信息预览
- 多质量选项
- 错误处理提示

## 📈 性能优化

- 异步视频信息提取
- 响应式加载状态
- 错误重试机制
- 移动端优化

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目仅供学习和个人使用。请遵守相关法律法规和平台使用条款。 
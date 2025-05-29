# 故障排除指南 / Troubleshooting Guide

## 本地开发环境问题

### 问题：前端显示"Failed to fetch"错误

这个错误通常表示前端无法连接到后端API服务器。

#### 解决步骤：

1. **检查服务器是否运行**
   ```bash
   # 启动服务器（使用8000端口避免冲突）
   PORT=8000 python3 run.py
   ```

2. **验证API端点**
   ```bash
   # 测试健康检查端点
   curl http://localhost:8000/api/health
   
   # 预期响应：
   # {"status": "healthy", "timestamp": "2024-01-01T00:00:00"}
   ```

3. **测试完整API**
   ```bash
   # 测试下载端点
   curl -X POST http://localhost:8000/api/download \
     -H "Content-Type: application/json" \
     -d '{"url": "https://x.com/username/status/123456789", "format": "mp4"}'
   ```

4. **使用调试页面**
   - 访问：`http://localhost:8000/debug`
   - 点击"Test Health API"按钮
   - 检查网络信息和错误详情

### 问题：端口冲突

```
Address already in use
Port 5000 is in use by another program
```

#### 解决方案：

1. **使用不同端口**
   ```bash
   PORT=8000 python3 run.py
   ```

2. **macOS用户：禁用AirPlay Receiver**
   - 系统偏好设置 > 共享
   - 取消勾选"AirPlay接收器"

### 问题：缺少依赖

```
Missing dependency: No module named 'flask'
```

#### 解决方案：

1. **安装开发依赖**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **或手动安装**
   ```bash
   pip install Flask Flask-CORS yt-dlp requests Werkzeug
   ```

### 问题：CORS错误

在浏览器控制台看到：
```
Access to fetch at 'http://localhost:8000/api/download' from origin 'http://localhost:8000' has been blocked by CORS policy
```

#### 解决方案：

这个问题在我们的代码中应该不会出现，因为已经配置了Flask-CORS。如果遇到：

1. **检查Flask-CORS是否安装**
   ```bash
   pip show flask-cors
   ```

2. **重启服务器**
   ```bash
   # 停止服务器 (Ctrl+C)
   # 重新启动
   PORT=8000 python3 run.py
   ```

## 网络和URL问题

### 问题：无法下载特定视频

```
No video could be found in this tweet
```

#### 可能原因：

1. **URL格式错误**
   - ✅ 正确：`https://twitter.com/username/status/123456789`
   - ✅ 正确：`https://x.com/username/status/123456789`
   - ❌ 错误：`https://twitter.com/username` (不包含status)

2. **推文不包含视频**
   - 推文可能只包含图片或文字
   - 请确认推文确实包含视频内容

3. **私人账户或受保护的推文**
   - 无法访问私人推文的媒体内容

### 问题：视频质量选项为空

```
No downloadable video formats found
```

#### 解决方案：

1. **检查URL是否有效**
2. **尝试不同的推文URL**
3. **检查网络连接**

## 部署问题

### Vercel部署错误

参考主要的README.md文件中的部署指南。

### 常见部署问题：

1. **构建失败**
   - 检查`requirements.txt`是否正确
   - 确保`vercel.json`配置正确

2. **API不工作**
   - 检查Vercel Functions日志
   - 确认`api/`目录结构正确

## 快速诊断步骤

1. **检查服务器状态**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **测试API连接**
   - 访问：`http://localhost:8000/debug`
   - 运行所有测试

3. **检查浏览器控制台**
   - 按F12打开开发者工具
   - 查看Console和Network标签页

4. **查看服务器日志**
   - 服务器运行窗口中的输出
   - 查找ERROR或WARNING消息

## 获取帮助

如果以上步骤都无法解决问题：

1. **收集信息**
   - 操作系统版本
   - Python版本：`python3 --version`
   - 错误截图
   - 浏览器控制台错误
   - 服务器日志

2. **提交Issue**
   - 访问项目GitHub页面
   - 创建新的Issue
   - 包含所有相关信息

## 常用命令

```bash
# 启动开发服务器
PORT=8000 python3 run.py

# 测试API健康
curl http://localhost:8000/api/health

# 查看Python版本
python3 --version

# 安装依赖
pip install -r requirements-dev.txt

# 查看端口使用情况 (macOS/Linux)
lsof -i :8000

# 查看端口使用情况 (Windows)
netstat -ano | findstr :8000
``` 
# 端口管理和服务启动文档

## 问题分析

### 根本原因

**为什么端口5000总是被占用？**

1. **僵尸进程残留**
   - 之前的Flask服务没有正确关闭
   - 进程仍在后台运行，占用端口5000
   - 新服务启动时检测到端口冲突

2. **macOS AirPlay Receiver冲突（次要原因）**
   - macOS 12+系统的AirPlay Receiver默认监听5000端口
   - 与我们的Flask服务冲突
   - 解决方案：关闭AirPlay Receiver或使用其他端口

3. **手动启动方式不统一**
   - 有时用`python3 stock_service.py`
   - 有时用`nohup python3 stock_service.py &`
   - 有时用`exec`工具后台运行
   - 导致进程管理混乱，无法追踪和清理

4. **没有统一的启动/停止脚本**
   - 每次手动清理端口占用
   - 容易遗漏僵尸进程
   - 没有自动检查机制

## 解决方案

### 1. 使用统一的启动脚本 ✅

**启动服务：**
```bash
./start_server.sh
```

**脚本功能：**
- ✅ 自动检查端口5000占用情况
- ✅ 自动终止占用端口的旧进程
- ✅ 自动检查并终止所有stock_service进程
- ✅ 启动新服务并记录PID
- ✅ 验证服务状态（进程检查 + 健康检查）
- ✅ 输出详细的启动信息

**停止服务：**
```bash
./stop_server.sh
```

### 2. 端口检查命令

**查看端口5000占用情况：**
```bash
lsof -i :5000
```

**查看占用端口的进程：**
```bash
lsof -ti:5000
```

**手动释放端口：**
```bash
lsof -ti:5000 | xargs kill -9
```

### 3. 查看进程状态

**查看所有stock_service进程：**
```bash
ps aux | grep "python.*stock_service" | grep -v grep
```

**终止特定PID的进程：**
```bash
kill -9 <PID>
```

### 4. 查看服务日志

**查看最新日志：**
```bash
tail -f logs/server.log
```

**查看最近50行：**
```bash
tail -50 logs/server.log
```

**查看错误信息：**
```bash
grep -i "error\|fail\|exception" logs/server.log
```

## 服务管理最佳实践

### ✅ 正确做法

1. **使用启动脚本**
   ```bash
   ./start_server.sh
   ```

2. **停止服务时使用停止脚本**
   ```bash
   ./stop_server.sh
   ```

3. **定期检查服务状态**
   ```bash
   curl http://localhost:5000/api/health
   ```

4. **查看日志排查问题**
   ```bash
   tail -f logs/server.log
   ```

### ❌ 错误做法

1. **多次手动启动导致僵尸进程**
   ```bash
   # 错误：多次运行会导致多个实例
   python3 stock_service.py &
   python3 stock_service.py &
   ```

2. **忘记停止旧服务就启动新服务**
   ```bash
   # 错误：旧进程仍在运行
   python3 stock_service.py  # 会报错：端口被占用
   ```

3. **忽略日志中的警告信息**
   ```bash
   # 忽略 "Address already in use" 错误
   ```

## macOS AirPlay Receiver问题

### 症状
- 端口5000被AirPlay Receiver占用
- 启动脚本显示无法释放端口

### 解决方案

**方案1：关闭AirPlay Receiver（推荐）**
1. 打开"系统设置" > "通用" > "隔空投与接力"
2. 取消勾选"隔空投接收器"
3. 或者关闭整个AirPlay功能

**方案2：使用其他端口**
如果必须使用AirPlay，可以修改`stock_service.py`中的端口配置：
```python
FLASK_PORT = 5001  # 改为其他端口
```

### 检查是否为AirPlay占用

```bash
# 查看端口5000占用详情
lsof -i :5000

# 如果看到类似输出，可能是AirPlay：
# COMMAND   PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
# AirPlay  1234 root   3u  IPv4  ...  TCP *:commplex-main (LISTEN)
```

## 常见问题排查

### 问题1：启动时报"Address already in use"

**原因：** 端口被占用

**解决：**
```bash
# 使用启动脚本自动处理
./start_server.sh
```

### 问题2：服务启动后无法访问

**原因：** 进程已退出

**解决：**
```bash
# 查看日志
tail -50 logs/server.log

# 检查进程状态
ps aux | grep "python.*stock_service" | grep -v grep

# 重新启动
./stop_server.sh
./start_server.sh
```

### 问题3：API返回超时或无响应

**原因：** 服务崩溃或卡死

**解决：**
```bash
# 查看错误日志
grep -i "error\|exception" logs/server.log

# 重启服务
./stop_server.sh
./start_server.sh
```

## 服务维护建议

### 1. 定期清理僵尸进程
每天检查一次是否有残留进程：
```bash
ps aux | grep "python.*stock_service" | grep -v grep
```

### 2. 监控日志文件
定期检查日志大小和错误：
```bash
ls -lh logs/server.log
tail -100 logs/server.log | grep -i "error"
```

### 3. 记录服务启动时间
在启动脚本中添加日志记录，方便追踪服务运行时长。

### 4. 备份重要配置
定期备份`stock_service.py`和配置文件。

## 总结

**核心原则：**
1. 统一使用`start_server.sh`和`stop_server.sh`管理服务
2. 不要手动多次启动同一个服务
3. 启动前先停止旧服务
4. 定期检查进程和日志

**端口冲突解决流程：**
```
端口被占用
    ↓
使用 stop_server.sh 停止旧服务
    ↓
使用 start_server.sh 启动新服务
    ↓
验证健康检查端点
    ↓
成功
```

---

**最后更新：** 2026-03-13
**维护者：** 李侃

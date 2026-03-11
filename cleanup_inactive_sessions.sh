#!/bin/bash
# 清理stock-analysis agent中不活跃的会话

SESSIONS_FILE="/Users/likan/.openclaw/agents/stock-analysis/sessions/sessions.json"
BACKUP_DIR="/Users/likan/.openclaw/agents/stock-analysis/sessions/backup"

echo "========================================="
echo "  清理stock-analysis agent不活跃会话"
echo "========================================="
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份当前会话文件
if [ -f "$SESSIONS_FILE" ]; then
    echo "📦 备份当前会话文件..."
    cp "$SESSIONS_FILE" "$BACKUP_DIR/sessions_backup_$(date +%Y%m%d_%H%M%S).json"
    echo "✅ 备份完成: $BACKUP_DIR/sessions_backup_$(date +%Y%m%d_%H%M%S).json"
    echo ""
else
    echo "⚠️ 会话文件不存在: $SESSIONS_FILE"
    echo ""
    exit 1
fi

# 清理不活跃的会话（超过30天没有更新）
echo "🧹 开始清理不活跃会话..."
echo ""

python3 -c "
import json
from datetime import datetime, timedelta

sessions_file = '$SESSIONS_FILE'
backup_file = '$BACKUP_DIR/sessions_backup_$(date +%Y%m%d_%H%M%S).json'

# 读取会话文件
with open(sessions_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

sessions = data.get('sessions', [])
now = datetime.now()
cutoff = now - timedelta(days=30)

print(f'Total sessions: {len(sessions)}')
print(f'Cutoff date: {cutoff.strftime(\"%Y-%m-%d %H:%M:%S\")}')
print(f'\\nProcessing sessions...')

# 清理不活跃的会话
active_sessions = []
removed_count = 0

for i, s in enumerate(sessions, 1):
    key = s.get('key', 'unknown')[:40]
    created = s.get('created', '')
    updated = s.get('updatedAt', '')

    # 检查是否活跃（30天内有更新）
    is_active = False
    if updated:
        try:
            updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            if updated_dt >= cutoff:
                is_active = True
        except:
            pass

    if is_active:
        active_sessions.append(s)
    else:
        removed_count += 1
        age_days = 0
        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                age_days = (now - updated_dt).days
            except:
                pass

        if age_days >= 100:
            print(f'{i}. ❌ Remove {key} (very old, {age_days} days)')
        elif age_days >= 30:
            print(f'{i}. ❌ Remove {key} (inactive, {age_days} days)')
        else:
            print(f'{i}. ❌ Remove {key} (no update)')

# 更新会话文件
data['sessions'] = active_sessions
with open(sessions_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\\n========================================')
print(f'  清理完成')
print(f'========================================')
print(f'')
print(f'  Removed sessions: {removed_count}')
print(f'  Active sessions: {len(active_sessions)}')
print(f'  Backup file: {backup_file}')
print(f'')
"

echo ""
echo "========================================="
echo "  清理完成"
echo "========================================="
echo ""
echo "📋 统计信息："
echo "  - 原始会话数：$(python3 -c "
import json
with open('$SESSIONS_FILE', 'r') as f:
    data = json.load(f)
print(len(data.get('sessions', [])))
")"
echo "  - 清理后会话数：$(python3 -c "
import json
with open('$SESSIONS_FILE', 'r') as f:
    data = json.load(f)
print(len(data.get('sessions', [])))
")"
echo "  - 删除的会话数：$(python3 -c "
import json
orig = None
clean = None
with open('$SESSIONS_FILE', 'r') as f:
    data = json.load(f)
    clean = len(data.get('sessions', []))

with open('$BACKUP_DIR/sessions_backup_$(ls -t '$BACKUP_DIR'/sessions_backup_*.json | head -1', 'r') as f:
    data = json.load(f)
    orig = len(data.get('sessions', []))

if orig and clean:
    print(orig - clean)
else:
    print(0)
")"
echo ""
echo "💡 下一步："
echo "  - 验证stock-analysis agent状态"
echo "  - 测试消息处理是否恢复正常"
echo "  - 如有需要，可以手动重启agent"
echo ""

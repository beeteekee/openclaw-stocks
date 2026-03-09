# 打赏区域功能说明

## 功能描述

在股票分析结果的打赏区域，左右两边添加了从下往上滚动的祝福语：

### 左边祝福语（8句话）
1. 祝大家马年快乐！
2. 事业马到成功
3. 比赛一马当先
4. 健康龙马精神
5. 理想天马行空
6. 爱情快马加鞭
7. 家庭龙腾马壮
8. 朋友车水马龙

### 右边祝福语（4句话）
1. 乘骏马之征途
2. 踏万里河山
3. 持初心以远航
4. 揽九天星河

## 技术实现

### 1. HTML结构

```
<div class="donation-section">
    <!-- 左边滚动区域 -->
    <div class="donation-left">
        <div class="donation-scroll">
            <div class="donation-scroll-item">...</div>
            <!-- 重复内容以实现无缝滚动 -->
        </div>
    </div>

    <!-- 中间打赏区域 -->
    <div class="donation-center">
        <div class="donation-title">❤️ 打赏支持</div>
        <div class="donation-content">
            <div class="donation-qr-container">
                <img id="donationQrCode">
            </div>
            <div class="donation-text">...</div>
        </div>
    </div>

    <!-- 右边滚动区域 -->
    <div class="donation-right">
        <div class="donation-scroll">
            <div class="donation-scroll-item">...</div>
            <!-- 重复内容以实现无缝滚动 -->
        </div>
    </div>
</div>
```

### 2. CSS样式

```css
.donation-section {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 15px;
}

.donation-left, .donation-right {
    flex: 1;
    height: 150px;
    overflow: hidden;
    position: relative;
}

.donation-scroll {
    position: absolute;
    width: 100%;
    animation: scrollUp 15s linear infinite;
}

@keyframes scrollUp {
    0% {
        transform: translateY(100%);
    }
    100% {
        transform: translateY(-100%);
    }
}

.donation-scroll-item {
    padding: 8px 0;
    font-size: 12px;
    color: #d68910;
    font-weight: 500;
    line-height: 1.6;
    text-align: center;
}
```

### 3. 响应式设计（移动端）

```css
@media (max-width: 768px) {
    .donation-section {
        flex-direction: column;
        gap: 15px;
    }

    .donation-left, .donation-right {
        width: 100%;
        height: 100px;
    }

    .donation-scroll-item {
        font-size: 11px;
    }
}
```

## 动画效果

- **滚动方向**：从下往上
- **滚动速度**：15秒完成一次完整循环
- **动画类型**：线性（linear），匀速滚动
- **滚动方式**：重复内容以实现无缝滚动

## 使用说明

1. 进行股票分析后，打赏区域会自动显示
2. 左右两边的祝福语会自动从下往上滚动
3. 中间是打赏二维码和说明文字
4. 在移动端，布局会自动调整为纵向排列

## 测试结果

✅ 所有功能测试通过
✅ HTML结构完整
✅ 祝福语内容正确
✅ CSS动画正常
✅ 移动端响应式正常
✅ 二维码显示正常

## 文件修改

- **stock-analysis.html**
  - 添加了左右滚动区域
  - 添加了CSS动画
  - 添加了移动端响应式样式

# 腾讯云服务器秒杀工具

[comment]: <> (Tencent Cloud Server Seckill Tool)

使用 Python 编写的自动化抢购脚本，支持并发抢购腾讯云轻量应用服务器。

![Tencent Cloud](image.png)

## 功能特点

- **自动获取 Cookie**：使用 Playwright 模拟浏览器登录，自动保存登录态
- **多地域并发抢购**：支持华北、华东、华南同时抢购
- **实时库存检测**：循环检测目标商品库存状态
- **服务器时间校准**：自动获取腾讯云服务器时间，确保准时抢购
- **自动等待秒杀**：监控时间，到点自动发起抢购

## 环境要求

- Python 3.8+
- Windows / macOS / Linux

## 安装步骤

### 1. 安装依赖

```bash
pip install playwright requests
playwright install chromium
```

### 2. 获取登录 Cookie

```bash
python get_cookies.py
```

运行后会自动打开浏览器，点击二维码扫码登录腾讯云。登录成功后 Cookie 会自动保存到 `cookies.json` 文件。

## 使用方法

### 配置参数

编辑 `snap_up_server.py` 文件：

1. **设置秒杀时间**（第 197 行）：

```python
SECKILL_TIME_STR = "2026-02-12 15:00:00"  # 格式：年-月-日 时:分:秒
```

2. **设置抢购地域**（第 199 行）：

```python
region_ids = [1, 4, 8]  # 1=华北，4=华东，8=华南
```

3. **更新 CSRF Token**（第 36 行）：

```
1. 打开浏览器开发者工具 (F12)
2. 切换到 Network 标签
3. 点击任意一个 cloud.tencent.com 的请求
4. 查看 Request Headers 中的 x-csrf-token
5. 将值更新到代码中
```

### 运行秒杀

```bash
python snap_up_server.py
```

脚本会自动：

1. 加载登录 Cookie
2. 校准服务器时间
3. 循环检测库存
4. 到达秒杀时间后自动发起抢购

## 地域配置说明

| region_id | 地域         |
| --------- | ------------ |
| 1         | 华北（广州） |
| 4         | 华东（上海） |
| 8         | 华南（北京） |

## 注意事项

1. **Cookie 有效期**：Cookie 有时效性，建议每次秒杀前重新获取
2. **CSRF Token**：每次登录后可能变化，秒杀前需确认更新
3. **抢购成功率**：脚本只提升效率，不保证抢购成功
4. **仅供学习**：仅限个人学习研究使用，请勿用于商业用途

## 工作原理

1. 加载 `cookies.json` 建立登录会话
2. 循环调用库存检测接口 (`check-available`)
3. 检测到有货后，并发调用下单接口 (`do-goods`)
4. 返回抢购结果

## 常见问题

**Q: 提示 "商品无购买权限"**
A: 检查是否已通过实名认证，或该商品是否对你的账号开放

**Q: 库存检测正常但抢购失败**
A: 确认 `x-csrf-token` 是否为最新值，检查 Cookie 是否有效

**Q: 抢购脚本运行正常但无响应**
A: 检查网络连接，确认秒杀时间是否正确设置

**Q: 无法正常获取cookie**
A: 是由于官方的网页链接每个月会更换一次，导致原脚本链接定位错误；需要修改get_cookies.py代码中的这个部分 page.wait_for_url("https://cloud.tencent.com/act/pro/featured-202607?fromSource=gwzcw.10216579.10216579.10216579&utm_medium=cpc&utm_id=gwzcw.10216579.10216579.10216579&msclkid=9d471e943d2d142808a4771f328779e6&page=warmup-202606&s_source=https%3A%2F%2Fcloud.tencent.com%2Fact%2Fpro%2Fdouble12-2025", timeout=0),只需复制打开脚本浏览器中的地址栏链接替换一下，再重新运行脚本就可以正常获取到cookie

## 文件结构

```
tencentyun/
├── get_cookies.py     # Cookie 获取脚本
├── snap_up_server.py  # 秒抢购主程序
├── cookies.json       # 登录 Cookie 存储
├── image.png          # 演示图片
└── README.md          # 项目文档
```

## 免责声明

本项目仅供学习交流使用，请勿用于商业用途。使用本工具产生的任何后果由使用者自行承担。

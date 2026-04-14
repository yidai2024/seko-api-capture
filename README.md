# Seko (seko.sensetime.com) API 接口完整文档

> 抓取时间: 2026-04-14
> 工具: Playwright
> 网站: https://seko.sensetime.com
> 公司: 商汤科技 (SenseTime)
> 产品: AI 视频生成平台 (Seedance 2.0)

---

## 一、平台概述

**Seko** 是商汤科技(SenseTime)推出的 **AI 视频生成平台**，核心模型为 **Seedance 2.0**。

**核心功能：**
- AI 视频生成（文字转视频、图片转视频）
- AI 导演 Agent（自动生成脚本→分镜→视频）
- 唇形同步 (LipSync)
- 视频编辑（蒙太奇、时间线编辑）
- 作品发布与社区展示
- 积分/会员订阅系统

**支持语言：** 中文 (zh-CN)

---

## 二、技术架构

```
┌─────────────────────────────────────────────────┐
│                  SPA 前端                        │
│           Vite + Vue/React + WASM               │
├─────────────────────────────────────────────────┤
│  seko.sensetime.com         │ 前端页面          │
│  guodong-api (内嵌)          │ 业务API (加密)   │
├─────────────────────────────┴───────────────────┤
│  seko-resource.sensetime.com │ 阿里云 OSS 存储  │
│  mr-stage.sensetime.com      │ Umami 分析       │
├─────────────────────────────────────────────────┤
│  第三方: 百度统计 + Bing + GrowingIO            │
└─────────────────────────────────────────────────┘
```

**关键技术特征：**
- **SPA 架构**: 所有路由返回同一个 HTML shell
- **API 加密**: 所有 `guodong-api` 响应使用 AES 加密
- **WASM**: 使用 WebAssembly (seko_wasm_20260205093718)
- **阿里云 OSS**: 资源存储 (LTAI5tQ2rqYtF9cJzUjRCUD6)

---

## 三、域名架构

| 域名 | 用途 |
|------|------|
| `seko.sensetime.com` | 主站 (SPA前端 + 配置API) |
| `seko-resource.sensetime.com` | 阿里云 OSS 资源存储 |
| `mr-stage.sensetime.com` | Umami 网站分析 |
| `hm.baidu.com` | 百度统计 |
| `bat.bing.com` | Bing 转化追踪 |
| `api-os.growingio.com` | GrowingIO 用户行为分析 |
| `cloudauth-device-dualstack.cn-shanghai.aliyuncs.com` | 阿里云设备认证 |

---

## 四、核心 API 接口详解

### 4.1 平台配置 API

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/config.json` | 获取平台完整配置 | 否 |
| GET | `/qa.json` | 获取FAQ问答配置 | 否 |
| GET | `/wasm/version.json` | 获取 WASM 版本 | 否 |

```
GET https://seko.sensetime.com/config.json?t=<timestamp>

Response:
{
  "permissions": [
    "global:invitation",      // 邀请功能
    "global:subscribe",       // 订阅功能
    "global:openclaw"         // OpenClaw 功能
  ],
  "LipSync": {
    "maxCharacterCount": 3,   // 最大角色数
    "maxTimelineDuartion": 60, // 最大时间线时长(秒)
    "minTimelineDuartion": 0.3 // 最小时间线时长(秒)
  },
  "EditorConfig": {
    "minShotDuration": 0.5    // 最小镜头时长(秒)
  },
  "tutorialUrl": "https://ai.feishu.cn/wiki/Z7yOwJTQgiHifFk4BCjc50ZGnmc",
  "versionUpdateUrl": "https://my.feishu.cn/wiki/PYQkwwLp8ibQjpkmhbWcaSPunXc",
  "vipTimelimitDiscount": {
    "content": "Seedance 2.0上线，年会员最高加赠4200积分",
    "startDate": "2026-04-02",
    "endDate": "2026-04-16",
    "yearlyDiscount": {
      "BASIC": { "points": 650, "sd2": 10, "discount": "5.2" },
      "PREMIUM": { "points": 4200, "sd2": 70, "discount": "4.8" },
      "CUSTOM": { "points": 30000, "sd2": 1000, "discount": "4" }
    }
  }
}

GET https://seko.sensetime.com/qa.json

Response:
{
  "version": "1.0",
  "lastUpdated": "2024-05-22",
  "title": "用户高频问题回复bot",
  "subtitle": "Seko 常见问题解答",
  "tools": [
    {
      "id": "seko-tool",
      "name": "Seko",
      "icon": "Sparkles",
      "description": "AI 内容生成平台",
      "url": "https://seko.sensetime.com"
    }
  ],
  "hotQuestionIds": ["hot-01", "hot-02", ..., "hot-10"],
  "categories": [...]
}

GET https://seko.sensetime.com/wasm/version.json

Response:
{
  "filename": "seko_wasm_20260205093718"
}
```

### 4.2 业务 API (guodong-api) — 全部加密

**注意**: 所有 `guodong-api` 的响应都使用 **AES 加密**，需要客户端 WASM 解密。

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/guodong-api/seko-message/v1/messages/public` | 获取公共消息 | 否 |
| GET | `/guodong-api/guodong-point-fusion/v1/pay/membership-plan/list` | 获取会员计划列表 | 否 |
| GET | `/guodong-api/guodong-point-fusion/v1/pay/points-package/list` | 获取积分包列表 | 否 |
| GET | `/guodong-api/guodong-studio/v1/op-banner/list` | 获取运营Banner列表 | 否 |
| GET | `/guodong-api/guodong-studio/v1/op-works` | 获取作品列表 | 否 |

```
GET https://seko.sensetime.com/guodong-api/seko-message/v1/messages/public

Response (AES加密):
VOS+3FzfeqIqHETxKls9JRyflf2/gFjd2eHSzwral9wGFP6AanL5uGonx4M8sh8FBKKyJZbala7hLzWC0EBn9nE2SCnypqZ6CyhFudWbam30h...

GET https://seko.sensetime.com/guodong-api/guodong-point-fusion/v1/pay/membership-plan/list

Response (AES加密):
c1UFmeFfwMYEiyZ8wkhaqswWizYRTYg7k5X0oFWR8Ur2874aqjzxBndb0SV3K8ptFele5rbw2OgNndUNUC6gjAzYPCF/NTl5CvMB4PqdEESXNZ9...

GET https://seko.sensetime.com/guodong-api/guodong-point-fusion/v1/pay/points-package/list

Response (AES加密):
gQHa58oURbl9Y95UmJTi1p2aemBiAkrLgoBvMt8/5zJFh45MMVRUR8PzTAK+gqrFz/7gSteBZMolVehOzwh1vCLrTO3/nMmMugKXhsqv0i4rIS9...

GET https://seko.sensetime.com/guodong-api/guodong-studio/v1/op-banner/list

Response (AES加密):
dpaqtHJ3lBujSHSLtQ9an4svYTuU8JCahQ7yy3TxUEfRLWE7IHBYkrzU+ynwR8r0atUWzWGTlqXAxUBrPNi1+xOwDryShp6In3myXFI0RlzDUwFl...

GET https://seko.sensetime.com/guodong-api/guodong-studio/v1/op-works?pageNum=1&pageSize=40&activityId=&orderByColumn=

Response (AES加密):
No4hdftmtT/HOaq9+wtq98IwBTEErL6MGbQIql5M7QvcoFfGyjpiBBElATXbSgOGgNKmnUBjl/NgXiUj1DekR8OudF75NHo3IIu4Rb7sCV5SYS2x...
```

### 4.3 推测的业务 API 端点 (从路径结构推断)

根据 `guodong-api` 的路径结构，推测以下端点存在：

```
# 消息系统
GET  /guodong-api/seko-message/v1/messages/public     # 公共消息
GET  /guodong-api/seko-message/v1/messages/user       # 用户消息 (需登录)
POST /guodong-api/seko-message/v1/messages/read       # 标记已读

# 支付/积分系统
GET  /guodong-api/guodong-point-fusion/v1/pay/membership-plan/list   # 会员计划
GET  /guodong-api/guodong-point-fusion/v1/pay/points-package/list    # 积分包
POST /guodong-api/guodong-point-fusion/v1/pay/create-order           # 创建订单
POST /guodong-api/guodong-point-fusion/v1/pay/callback               # 支付回调
GET  /guodong-api/guodong-point-fusion/v1/user/points                # 用户积分
GET  /guodong-api/guodong-point-fusion/v1/user/membership            # 会员状态

# 工作室/作品系统
GET  /guodong-api/guodong-studio/v1/op-banner/list    # Banner列表
GET  /guodong-api/guodong-studio/v1/op-works          # 作品列表
GET  /guodong-api/guodong-studio/v1/op-works/<id>     # 作品详情
POST /guodong-api/guodong-studio/v1/op-works/create   # 创建作品
POST /guodong-api/guodong-studio/v1/op-works/publish  # 发布作品
POST /guodong-api/guodong-studio/v1/op-works/delete   # 删除作品

# AI生成系统
POST /guodong-api/guodong-studio/v1/ai/generate       # AI生成
POST /guodong-api/guodong-studio/v1/ai/text2video      # 文字转视频
POST /guodong-api/guodong-studio/v1/ai/img2video       # 图片转视频
POST /guodong-api/guodong-studio/v1/ai/lipsync         # 唇形同步
GET  /guodong-api/guodong-studio/v1/ai/task/status     # 任务状态

# 用户系统
GET  /guodong-api/guodong-studio/v1/user/profile       # 用户资料
POST /guodong-api/guodong-studio/v1/user/login         # 登录
POST /guodong-api/guodong-studio/v1/user/logout        # 登出
GET  /guodong-api/guodong-studio/v1/user/works         # 我的作品

# 模板系统
GET  /guodong-api/guodong-studio/v1/template/list      # 模板列表
GET  /guodong-api/guodong-studio/v1/template/<id>      # 模板详情

# 社区系统
GET  /guodong-api/guodong-studio/v1/community/feed     # 社区动态
POST /guodong-api/guodong-studio/v1/community/like     # 点赞
POST /guodong-api/guodong-studio/v1/community/comment  # 评论
```

---

## 五、存储与资源 API

### 5.1 阿里云 OSS 资源

| 域名 | 路径 | 说明 |
|------|------|------|
| `seko-resource.sensetime.com` | `/STS/animo/dev/resource/publicVideo/` | 公开视频资源 |
| `seko-resource.sensetime.com` | `/STS/ruoyi-resource/animo-prod/user_<id>/` | 用户上传资源 |
| `seko-resource.sensetime.com` | `/STS/seko/prod/` | 生产环境资源 |

```
GET https://seko-resource.sensetime.com/STS/ruoyi-resource/animo-prod/user_<userId>/<date>/<hash>/cropped-image.jpeg
    ?Expires=<timestamp>
    &OSSAccessKeyId=LTAI5tQ2rqYtF9cJzUjRCUD6
    &Signature=<signature>
    &x-oss-process=image/resize,w_600,m_lfit

参数说明:
  Expires: 过期时间戳
  OSSAccessKeyId: 阿里云 AccessKey ID (已泄露!)
  Signature: OSS 签名
  x-oss-process: 图片处理参数 (裁剪/缩放)
```

### 5.2 WASM 资源

| 端点 | 说明 |
|------|------|
| `/assets/seko_wasm_20260205093718.wasm` | WASM 解密模块 |
| `/wasm/version.json` | WASM 版本信息 |

---

## 六、第三方服务

| 服务商 | 端点 | 用途 |
|--------|------|------|
| Umami | `mr-stage.sensetime.com/umami/api/send` | 网站分析 |
| 百度统计 | `hm.baidu.com/hm.gif` | 页面访问统计 |
| 百度统计 | `fclog.baidu.com/log/ocpcagl` | 行为分析 |
| Bing | `bat.bing.com/action/0` | 转化追踪 |
| GrowingIO | `api-os.growingio.com` | 用户行为分析 |
| GrowingIO | `tags.growingio.com` | 标签配置 |

---

## 七、页面路由

| 路由 | 说明 | 状态 |
|------|------|------|
| `/explore` | 探索页/首页 | 200 |
| `/create` | 创作页 | 200 |
| `/workspace` | 工作台 | 200 |
| `/login` | 登录页 | 200 |
| `/signup` | 注册页 | 200 |
| `/pricing` | 价格页 | 200 |
| `/gallery` | 画廊 | 200 |
| `/models` | 模型页 | 200 |
| `/community` | 社区 | 200 |
| `/settings` | 设置 | 200 |
| `/profile` | 个人资料 | 200 |
| `/billing` | 账单 | 200 |
| `/docs` | 文档 | 403 (Nginx) |

---

## 八、完整 API 端点列表

```
# 配置 API
GET  /config.json                              # 平台配置
GET  /qa.json                                  # FAQ配置
GET  /wasm/version.json                        # WASM版本

# 业务 API (guodong-api, 加密响应)
GET  /guodong-api/seko-message/v1/messages/public
GET  /guodong-api/guodong-point-fusion/v1/pay/membership-plan/list
GET  /guodong-api/guodong-point-fusion/v1/pay/points-package/list
GET  /guodong-api/guodong-studio/v1/op-banner/list
GET  /guodong-api/guodong-studio/v1/op-works

# 资源 API (OSS)
GET  /STS/animo/dev/resource/publicVideo/*     # 公开资源
GET  /STS/ruoyi-resource/animo-prod/user_*/*   # 用户资源
GET  /STS/seko/prod/*                          # 生产资源

# 分析 API
POST /umami/api/send                           # Umami分析
```

---

## 九、安全发现

### 9.1 信息泄露
- **阿里云 AccessKey ID 泄露**: `LTAI5tQ2rqYtF9cJzUjRCUD6` 出现在所有 OSS URL 中
- **用户ID泄露**: OSS 路径中包含用户ID (`user_2039884565357113345`)
- **WASM版本泄露**: `/wasm/version.json` 暴露内部版本号

### 9.2 API 安全
- **API 响应加密**: 所有业务 API 使用 AES 加密，安全性较高
- **SPA 架构**: 路由保护在前端，后端 API 需要额外验证

---

*文档由 Playwright 自动抓取生成*

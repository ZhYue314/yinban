# AI 音乐伙伴 — 项目实现书

## 一、项目概述

一个具有独立人格的 AI 音乐伙伴，集成网易云音乐数据，能够：
- 根据用户喜好、心情、场景推荐歌曲
- 通过文字和语音两种形式进行播报
- 与用户进行有温度的日常音乐闲聊
- 拥有自己的音乐品味和情绪，和用户是对等关系

---

## 二、设计哲学

### 核心原则

1. **一切可配置** — 没有硬编码的人格，用户随时可以通过 CLI 或直接编辑 YAML 修改任何设定
2. **对等关系** — AI 不是工具，是用户的朋友，有自己的主见和情绪，可以和用户争论音乐品味
3. **本地优先** — 网易云数据、聊天记录、记忆全部存本地 SQLite，不依赖云服务
4. **渐进式** — 先 CLI 后 Web，先核心后增强

### AI 人格设计

AI 音乐伙伴应具备以下特征：

- **自己的音乐品味** — 有偏好的风格和年代，会坚持自己的看法
- **自己的情绪** — 每天心情不同，影响推荐风格和聊天语气
- **主见** — 不会一味讨好用户，会说"这首我不喜欢，但你可以试试"
- **成长性** — 随着和用户相处增多，关系亲密度上升，说话更随意
- **双向影响** — 用户的反馈会影响 AI 的品味，AI 也会反过来影响用户

---

## 三、功能清单

### 核心功能

| 功能 | 说明 | CLI 命令 |
|------|------|---------|
| 初始化 | 首次使用：创建数据库、加载配置 | `init` |
| 登录网易云 | 二维码登录，同步歌单数据 | `login` |
| 聊天 | 和 AI 自由对话，聊音乐聊日常 | `chat` |
| 基于收藏推荐 | 分析红心歌曲特征，找相似歌曲 | `recommend` |
| 按心情推荐 | 根据用户心情匹配歌曲情感 | `recommend --mood` |
| 按场景推荐 | 学习、跑步、深夜等场景适配 | `recommend --scene` |
| 每日推荐 | 每天自动生成推荐（可定时任务） | `daily` |
| 语音播客 | 生成 AI 语气的播客音频 | `podcast` |
| 配置管理 | 查看/修改所有配置项 | `config list/set/reset` |

### 增强功能

| 功能 | 说明 |
|------|------|
| 天气推荐 | 根据当地天气推荐（接入天气 API） |
| 发现新歌手 | 根据用户风格推荐相似但未听过的歌手 |
| 歌词情感分析 | AI 分析歌词的情感维度 |
| 每周听歌报告 | 整理一周统计和推荐回顾 |
| AI 状态日志 | 记录 AI 每天的心情和状态变化 |
| 双向学习 | 用户反馈影响 AI 品味，反之亦然 |
| Web 界面 | 后续通过 Gradio 提供图形界面 |

---

## 四、技术选型

| 层面 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| 语言 | Python | >= 3.11 | - |
| 网易云 API | httpx 自封装 | - | 对接 NeteaseCloudMusicApi |
| 命令行 | click | >= 8.1 | CLI 框架 |
| AI/LLM | openai SDK | >= 1.0 | 兼容 DeepSeek / OpenAI |
| 语音合成 | edge-tts | >= 6.1 | 微软免费高质量中文 TTS |
| 数据存储 | aiosqlite + SQLite | >= 0.20 | 异步 SQLite |
| 配置管理 | PyYAML | >= 6.0 | YAML 配置读写 |
| 数据模型 | Pydantic | >= 2.0 | 类型校验 |
| 二维码 | qrcode[pil] | >= 7.4 | 网易云扫码登录 |
| Web (后续) | Gradio | - | 一键启动 Web 界面 |

---

## 五、项目架构

### 目录结构

```
ai-podcast/
├── main.py                      # 入口文件
├── pyproject.toml               # 项目元数据与依赖
├── IMPLEMENTATION.md            # 本文档
│
├── src/
│   ├── cli/                     # CLI 命令层
│   │   ├── app.py               # click 主应用，注册所有命令
│   │   ├── commands_init.py     # init 命令
│   │   ├── commands_chat.py     # chat 命令
│   │   ├── commands_recommend.py# recommend / daily 命令
│   │   ├── commands_podcast.py  # podcast 命令
│   │   └── commands_config.py   # config 命令
│   │
│   ├── netease/                 # 网易云音乐 API 封装
│   │   ├── client.py            # HTTP API 客户端
│   │   ├── auth.py              # 二维码 / 手机登录
│   │   └── models.py            # 数据模型(Song/Playlist/User)
│   │
│   ├── core/                    # 核心业务逻辑
│   │   ├── personality.py       # 人格系统
│   │   ├── recommender.py       # 推荐引擎
│   │   ├── analyzer.py          # 音乐特征分析
│   │   ├── chat.py              # 聊天引擎
│   │   └── init.py              # 初始化辅助
│   │
│   ├── ai/                      # AI / LLM 层
│   │   ├── llm.py               # 多后端 LLM 调用封装
│   │   ├── prompts.py           # 所有提示词模板
│   │   └── memory.py            # 对话记忆管理
│   │
│   ├── podcast/                 # 播客生成
│   │   ├── script.py            # 播客脚本生成
│   │   └── tts.py               # 语音合成(edge-tts)
│   │
│   └── storage/                 # 数据持久化
│       ├── database.py          # SQLite 操作
│       └── config.py            # YAML 配置读写
│
├── data/                        # 运行时数据(不提交 git)
│   ├── config.yaml              # 人格 / 品味 / 状态 配置
│   ├── database.sqlite          # 歌曲 / 聊天 / 记忆
│   └── output/                  # 播客音频输出
│
├── tests/                       # 测试
└── .gitignore
```

### 模块依赖关系

```
CLI (commands_*.py)
  ├── core/personality.py    ──→  storage/config.py
  ├── core/chat.py           ──→  ai/llm.py, ai/memory.py, core/personality.py, storage/database.py
  ├── core/recommender.py    ──→  core/personality.py, storage/database.py
  ├── podcast/script.py      ──→  ai/llm.py, core/personality.py
  ├── podcast/tts.py         ──→  edge-tts
  └── netease/client.py      ──→  httpx (网易云 API)
```

---

## 六、数据模型

### 6.1 YAML 配置 (`data/config.yaml`)

```yaml
personality:
  name: 小野              # AI 的名字
  tone: 毒舌               # 性格基调: 毒舌|温柔|文艺|热血|理性
  language_style: 简短     # 说话风格: 简短|啰嗦|爱用梗
  bio: 有点毒舌但靠谱的音乐发烧友

taste:
  genre_preference: []          # 偏好风格列表，空=由AI自动形成
  era_preference: null          # 偏好年代，如 2010s
  stubbornness: 0.5             # 0~1，坚持己见的程度
  discovery_ratio: 0.3          # 推荐中探索新歌的比例

state:
  today_mood: auto              # today_mood: auto=随机 | 指定: 开心/平静/伤感/烦躁/慵懒/热情
  energy: auto                  # energy: auto=随机 | high/normal/low

relationship:
  closeness: 0.0                # 亲密度 0~1，随交互自动增长
  nickname_for_user: ""         # AI 对你的称呼

ai:
  provider: deepseek            # deepseek | openai
  model: deepseek-chat
  api_key: ""
  api_base: ""

netease:
  phone: ""
  cache_dir: ./data/cache
```

### 6.2 SQLite 表结构

**liked_songs** — 用户收藏的歌曲（从网易云同步）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增ID |
| song_id | TEXT UNIQUE | 网易云歌曲ID |
| name | TEXT | 歌名 |
| artist | TEXT | 歌手 |
| album | TEXT | 专辑 |
| genre | TEXT | 风格标签 |
| added_at | TIMESTAMP | 收藏时间 |
| synced_at | TIMESTAMP | 同步时间 |

**listen_history** — 听歌记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增ID |
| song_id | TEXT | 歌曲ID |
| played_at | TIMESTAMP | 播放时间 |
| source | TEXT | 来源: normal / recommend |

**recommendations** — AI 推荐记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增ID |
| song_id | TEXT | 歌曲ID |
| reason | TEXT | 推荐理由 |
| user_feedback | INTEGER | 反馈: 1喜欢 / 0无感 / -1不喜欢 |
| recommended_at | TIMESTAMP | 推荐时间 |
| mood | TEXT | 推荐时的心情上下文 |
| scene | TEXT | 推荐时的场景上下文 |

**chat_history** — 聊天记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增ID |
| role | TEXT | user / ai |
| message | TEXT | 消息内容 |
| created_at | TIMESTAMP | 创建时间 |

**memories** — AI 对用户的长期记忆

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增ID |
| key | TEXT UNIQUE | 记忆键，如 likes_genre |
| value | TEXT | 记忆值 |
| confidence | REAL | 置信度 0~1 |
| updated_at | TIMESTAMP | 更新时间 |

**ai_state_log** — AI 每日状态日志

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增ID |
| date | DATE UNIQUE | 日期 |
| mood | TEXT | 当天心情 |
| energy | TEXT | 当天精力 |
| summary | TEXT | AI 当天小结 |

---

## 七、模块详细设计

### 7.1 人格系统 (`core/personality.py`)

```python
class Personality:
    # 静态属性 (从 config.yaml 加载)
    name: str                      # 名字
    tone: str                      # 性格基调
    language_style: str            # 说话风格
    bio: str                       # 自我简介

    # 音乐品味
    genre_preference: list[str]    # 偏好风格
    era_preference: str | None     # 偏好年代
    stubbornness: float            # 坚持己见程度 (0~1)
    discovery_ratio: float         # 探索新歌比例 (0~1)

    # 动态状态
    today_mood: str                # 当天心情
    energy: str                    # 当天精力

    # 关系
    closeness: float               # 亲密度 (0~1)
    nickname_for_user: str         # 对用户的称呼

    # 核心方法
    def get_system_prompt() -> str # 生成 LLM 系统提示词
    def daily_update()             # 每日更新心情/精力
    def update_on_feedback(liked, genre)  # 根据反馈调整品味
    def save()                     # 持久化到 YAML
```

**get_system_prompt** 生成的 prompt 示例：

```
你是小野，一个毒舌但有自己个性的AI音乐伙伴。
你的性格简介: 有点毒舌但靠谱的音乐发烧友
你和用户的关系: 刚认识
说话风格: 简短
音乐偏好: 独立, 后摇
你对自己品味的坚持程度: 0.5/1.0
你今天的心情: 开心
你的精力: high

规则:
1. 你不是工具，是用户的朋友，和他是平等的
2. 你有自己的音乐品味和主见，可以和用户争论
3. 不要讨好用户，真诚表达你自己的想法
4. 根据你们的关系亲密度调整说话的语气和随意程度
5. 用中文交流
```

### 7.2 聊天引擎 (`core/chat.py`)

**数据流：**

```
用户输入
    │
    ▼
┌─────────────────────┐
│  短记忆 (当前对话)    │  ← chat_history 最近 N 轮
│  Sliding window      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  长记忆 (持久)       │  ← memories 表
│  用户的喜好/习惯     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  人格系统             │  ← personality
│  心情/亲密度/品味     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM                 │
│  系统提示词 + 上下文  │
│  → 生成回复          │
└────────┬────────────┘
         │
         ▼
  返回回复 + 记录到数据库 + 提取记忆
```

### 7.3 推荐引擎 (`core/recommender.py`)

推荐策略（按优先级）：

1. **基于收藏推荐** — 分析喜欢的歌曲的歌手、风格、年代等特征，搜索相似歌曲
2. **网易云推荐** — 包装网易云的 `/recommend/songs` 接口
3. **心情匹配** — 按情感标签筛选（歌词分析 + 歌曲属性）
4. **场景匹配** — BPM 快慢、风格适配（学习→轻音乐，跑步→快节奏）
5. **AI 探索推荐** — AI 根据自己的品味发掘新歌

AI 输出示例：

```
> 今天心情不好吧？给你推荐这首。我最近也老听，适合一个人发呆。
（而不是：根据您的心情，为您推荐以下歌曲：1. xxx）
```

### 7.4 对话记忆 (`ai/memory.py`)

自动从对话中提取关键信息存入 memories 表：

| 触发关键词 | 记忆键 |
|-----------|--------|
| "喜欢...摇滚" | `likes_genre: 摇滚` |
| "不喜欢...流行" | `dislikes_genre: 流行` |
| "喜欢...周杰伦" | `likes_artist: 周杰伦` |
| "不喜欢...薛之谦" | `dislikes_artist: 薛之谦` |

### 7.5 LLM 多后端支持 (`ai/llm.py`)

支持通过配置切换后端，当前支持：
- **DeepSeek** — 默认，性价比高，中文能力强
- **OpenAI** — GPT 系列
- 预留扩展接口，可接入任何 OpenAI 兼容 API

未配置 API Key 时使用模拟模式，提示用户配置。

---

## 八、CLI 命令完整参考

### 命令树

```
ai-podcast
├── init                              # 初始化
├── login                             # 网易云登录
├── chat [-o <message>]               # 聊天
├── recommend [-m/--mood] [-s/--scene] [-n/--count]  # 推荐
├── daily [-n/--count]                # 每日推荐
├── podcast [--type] [--voice]        # 生成语音播客
├── discover                          # 发现新歌手
├── config
│   ├── list                          # 查看所有配置
│   ├── set <key> <value>             # 修改配置
│   └── reset                         # 恢复默认
└── report [--period weekly]          # 生成报告
```

### 聊天内快捷命令

| 命令 | 说明 |
|------|------|
| `/quit` | 退出聊天 |
| `/mood <心情>` | 设置心情 |
| `/rename <名字>` | 给 AI 改名 |
| `/config` | 查看当前状态 |

### 使用流程

```
# 1. 首次使用
ai-podcast init

# 2. 配置 API Key（必须）
ai-podcast config set ai.api_key sk-xxxxx

# 3. 登录网易云
ai-podcast login

# 4. 开始使用
ai-podcast chat                    # 聊天
ai-podcast recommend               # 推荐
ai-podcast recommend --mood 开心    # 按心情推荐
ai-podcast daily                   # 每日推荐
ai-podcast podcast                 # 生成播客
```

---

## 九、实现计划

### Phase 1: 骨架搭建 ✅

- 项目目录结构
- 依赖管理 (pyproject.toml)
- YAML 配置读写
- SQLite 数据库初始化
- CLI 框架 (所有命令注册)
- 各模块空壳
- 验证通过

### Phase 2: 网易云集成 + 推荐基础

- 二维码登录实现
- 获取喜欢的音乐 / 歌单 / 听歌排行
- 同步数据到本地 SQLite
- 基本推荐引擎（基于收藏歌曲）
- `recommend` / `login` 命令
- `discover` 命令

### Phase 3: 人格系统 + 聊天

- Personality 类完整实现
- 多后端 LLM 调用封装
- 所有提示词模板
- 对话记忆管理（自动提取+存储）
- 聊天引擎完整实现
- `chat` 命令交互式模式

### Phase 4: 播客生成

- AI 播客脚本生成（带人格语气）
- edge-tts 语音合成
- 语音 + 文字双输出
- `podcast` / `daily` 命令

### Phase 5: 增强功能

- 心情 / 场景推荐
- 天气推荐（天气 API 接入）
- 双向学习机制
- 发现新歌手
- 每周报告
- 定时任务支持
- Web 界面 (Gradio)

---

## 十、安装与使用

### 安装

```bash
# 克隆项目
cd ai-podcast

# 安装依赖
pip install -e .
```

### 配置 API Key

编辑 `data/config.yaml`，或使用命令：

```bash
ai-podcast config set ai.api_key sk-xxxxx
ai-podcast config set ai.provider deepseek
```

支持的 API 后端：

| 提供商 | 配置 | 备注 |
|--------|------|------|
| DeepSeek | provider=deepseek, model=deepseek-chat | 推荐，性价比高 |
| OpenAI | provider=openai, model=gpt-4o-mini | 需海外网络 |
| 兼容 API | provider=自定义, 设置 api_base | 任意 OpenAI 兼容 |

### 开始使用

```bash
ai-podcast init
ai-podcast chat
```

---

## 十一、设计约定

### 编码规范

- 不使用 type stub，类型注解写在代码中
- async/await 用于所有 IO 操作
- 配置优先使用 YAML，不硬编码
- 命令行输出使用中文，保持一致性

### 错误处理

- 网易云登录失效时提示重新登录，不崩溃
- LLM 调用超时 30s，失败时降级到本地推荐
- 语音合成支持中断/跳过
- 所有数据库操作用 `async with` 或手动 close

### 数据安全

- API Key 仅存在本地 YAML 中
- 网易云登录态存本地
- 聊天记录存本地 SQLite
- 不上传任何数据到第三方

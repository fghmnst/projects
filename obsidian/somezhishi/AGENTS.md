# AGENTS.md — somezhishi 学习笔记库规则

本文件夹 `~/SomeThingFunny/projects/obsidian/somezhishi` 是个人 Obsidian 学习笔记库。以下规则适用于**在本库内创建或修改任何笔记**的 AI 助手（及本人），请严格遵守。

## 笔记硬性要求

1. **日期置顶**：每篇笔记**必须**以 YAML frontmatter 开头，其中 `date` 字段填写**当天**日期（格式 `YYYY-MM-DD`），且必须是文件最开始写的内容之一。

   ```markdown
   ---
   date: 2026-09-09
   ---
   ```

2. **标题简洁易懂**：标题（文件名与笔记内 `#` 一级标题一致）使用简短的中文短语，让人一眼看懂主题，如：
   - 好：`Linux入门-chmod权限与JobControl任务控制.md`
   - 差：`md20260909a-最终版-不要删.md`

3. **内容面向初学者**：
   - 假设读者不懂任何背景，逐个概念解释"是什么、为什么、怎么用"
   - 多用表格、示例命令、类比说明
   - 代码/命令必须配解释，不能只贴命令
   - 可适量使用 Obsidian 原生语法：callout（`> [!note]`）、表格、标签、wikilink

4. **一份主题一篇笔记**：新主题新建文件，不要把所有内容堆在一篇里。

## 文件名规范

- 格式：`主题-子主题.md` 或 `主题.md`
- 全部中文或常见英文缩写，不用日期做文件名（日期在 frontmatter 里）
- 空格用连字符 `-` 代替

## 维护

- 库内 `.obsidian/` 为 Obsidian 配置目录，**不得改动**
- 默认欢迎笔记 `Welcome.md` 可保留或由用户决定删除
- 修改已有笔记时，先读原文件，保持其风格与已用 frontmatter 字段一致

## 操作方式约定（Obsidian CLI 已启用）

笔记读写分两种模式，按内容类型选择：

1. **纯 Markdown 文本**（绝大多数日常笔记）：
   - 直接以普通文件方式创建/修改（Write/Edit 工具），无需额外工具，快速可靠
   - 适用：普通正文、表格、标题、列表、frontmatter、callout、wikilink 等纯文本内容

2. **涉及 Obsidian 特性功能**时，先加载对应技能（skill）再操作，按其工作流执行：
   - `obsidian-cli`：需要通过 Obsidian 本体能力操作时（vault 管理、属性查询、笔记跳转、插件/主题开发、执行 JS 等）
   - `obsidian-markdown`：需要校验/生成 Obsidian 专属 Markdown 语法细节时
   - `obsidian-bases`：`.base` 数据库视图文件
   - `json-canvas`：`.canvas` 白板文件
   - `defuddle`：从网页提取干净正文做笔记素材

选择判据：**只写文本 → 直接编辑；要用 Obsidian 的特性/接口/渲染能力，或用户明确要求走 Obsidian → 先载技能**。载入技能不影响纯文本规则（日期置顶、标题、初学者向内容依然必须遵守）。

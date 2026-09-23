---
date: 2026-09-23
tags:
  - 排障
  - opencode
---

# opencode 自签证书报错：排查与禁用校验风险

> 2026-09-23 晚。opencode 报 `self signed certificate in certificate chain`，根因是**上游 WAF 短暂下发了自签占位证书**（约 95 秒后自愈）。不是本地 Clash 的问题；正确做法是等待/重试，而不是关闭证书校验。

## 现象

- opencode 所有 DeepSeek 请求失败，报：`Error: self signed certificate in certificate chain`
- 连续 3 次尝试全部失败；约 95 秒后自行恢复
- `NODE_TLS_REJECT_UNAUTHORIZED=0 opencode` 能"绕过"（**错误做法，见下文**）

opencode 日志位置：`~/.local/share/opencode/log/opencode.log`（找 `stream error` / `providerID=deepseek` 的行）。

## 排查套路（可复用）

按「先定位谁在报错 → 再排除本地 → 最后验证上游」的顺序：

### 1. 看 opencode 日志：确认是哪个 provider/域名

看 `stream error` 行 → 本次是 `providerID=deepseek`，说明问题在模型 API 连接上。

### 2. 看代理日志：确认连接走了哪条路

Clash Verge 的日志在 **Windows 侧数据目录的 `logs/sidecar/`**（App 内"日志"页也能看）。本次日志显示：

```
[TCP] 127.0.0.1:xxxxx --> api.deepseek.com:443 match GeoIP(cn) using DIRECT
```

`DIRECT` = **直连，没走机场节点**。这一步排除了"代理节点做手脚"的可能（Clash/mihomo 本身也不会解密 TLS）。

### 3. 直接验证证书链（核心命令）

```bash
openssl s_client -connect api.deepseek.com:443 -servername api.deepseek.com </dev/null 2>/dev/null \
  | grep -E 's:|i:|Verify return code'
```

参数解释：

- `-connect 域名:443`：连目标服务器
- `-servername 域名`：TLS SNI，告诉服务器要访问的域名（一台服务器上可能挂很多网站）
- `</dev/null`：连上后立刻关闭输入，不进入交互模式
- `grep`：只看证书链（`s:` = 证书主体，`i:` = 签发者）和最终校验结果

健康输出应类似 `Verify return code: 0 (ok)`，链条是 `网站证书 → 中间证书 → DigiCert 根证书`。
若 `Verify return code` 非 0，或链里出现一个"自己签自己"的证书 → 证书有问题。

### 4. 排除本地干扰项

| 检查 | 命令/位置 | 本次结果 |
|---|---|---|
| hosts 劫持 | Windows hosts 文件 / `/etc/hosts` | 无异常 |
| 自定义 CA | `echo $NODE_EXTRA_CA_CERTS` | 未设置 |
| TUN 模式 | Clash Verge 设置 | 未开启 |
| MITM 工具 | 任务管理器 / `tasklist` 搜 Fiddler、Charles、mitmproxy 等 | 无 |

### 5. 换客户端交叉验证

同一个域名，用不同工具测（排除"只有 opencode 有问题"）：

```bash
# curl：-I 只看响应头，不下载正文
curl -sI https://api.deepseek.com -o /dev/null -w 'http=%{http_code} ssl_verify=%{ssl_verify_result}\n'
# ssl_verify_result=0 表示证书校验通过（http 401 是因为没带 API key，正常）
```

```bash
# Node（opencode 的 Bun 同为 JS 运行时，参考价值高）
node -e "fetch('https://api.deepseek.com/',{method:'HEAD'}).then(r=>console.log('OK',r.status)).catch(e=>console.log('ERR:',e.message))"
```

## 根因（本次）

- `api.deepseek.com` 实际 CNAME 到**华为云 WAF**（`*.vip1.huaweicloudwaf.com`）
- WAF/CDN 在**证书部署或轮换的窗口期**会短暂下发"占位"自签证书 → 客户端校验失败
- 窗口约 95 秒后自愈；事后对多个边缘节点（移动/联通线路）连续采样，证书链全部合法
- opencode 当时不自动重试的原因：证书类错误不在其重试白名单里（官方 PR #43863），每次尝试都直接失败

> [!warning] 关键判断
> 报"证书错误"说明 **TCP 已经连上了**——问题出在"验身份证"环节；如果连都连不上，报的会是超时/连接被重置。

## 正确解法

1. **等 1 分钟重发**（本次 95 秒自愈）——上游瞬时问题，抢修无用
2. 若复现，30 秒抓证并记录，可反馈 DeepSeek 官方：

   ```bash
   openssl s_client -connect api.deepseek.com:443 -servername api.deepseek.com </dev/null 2>/dev/null | grep -E 's:|i:|Verify return code'
   dig +short api.deepseek.com   # 记录当时解析到的 IP
   ```

3. **不要**把 `NODE_TLS_REJECT_UNAUTHORIZED=0` 写进 `.bashrc` 或任何配置
4. 不要用 `NODE_EXTRA_CA_CERTS` 导入占位证书——占位证书不固定，导入没有意义（那是给公司固定私有 CA 用的）
5. （可选，频繁复发才考虑）Clash 加规则让 `deepseek.com` 走代理节点，绕开坏边缘；代价是绕路延迟

## ⚠️ 为什么 `NODE_TLS_REJECT_UNAUTHORIZED=0` 很危险

它让 Node/Bun 系程序（opencode 属于此类）**不再检查服务器证书**，等于：

> HTTPS 本来是"核验对方身份证后再进屋"，这个变量相当于把门卫撤了——**谁都能进屋**。

| 风险 | 说明 |
|---|---|
| 中间人攻击（MITM） | 任何人都能伪装成 `api.deepseek.com`，读写你的请求 |
| 凭据泄露 | 请求头里的 API key、对话内容全部明文可见 |
| 与"修好"无关 | 它没有修复任何问题，只是把"报警器"关掉了 |
| 隐蔽复发 | 将来真遇到攻击时也不会再报错，你不会察觉 |

范围提醒：该变量只影响 Node/Bun 程序，**不影响浏览器和 curl**——所以"浏览器正常"不代表安全。它只该用于临时调试，用完立刻移除，更不该 `export` 到 shell 配置里。

### 中间人攻击（MITM）是什么

**画面**：你给朋友寄信，途中有人拆开信件，抄一份、改几个字再封好转发——你和朋友都以为信件直达，其实中间一直有只手。

技术版：攻击者插在你和服务器之间，和两边分别建立"看似正常"的连接：

```
你 ←→ 攻击者（假装是服务器） ←→ 真服务器
```

- 对服务器，攻击者假装是你（能读到你的 API key）
- 对你，攻击者假装是服务器（**需要一张伪造证书**）
- 证书校验就是"识破伪造证书"的唯一防线；关掉校验 = 中门大开

真实世界里的三类情况：

1. **公司/学校防火墙**做 TLS 解密审计（如 ZScaler）——不算恶意，但你会看到"自签证书"报错
2. **公共 Wi-Fi 的恶意热点**——典型攻击场景
3. **代理/加速软件**做流量改造

判断口诀：**报自签错 → 先确认"是不是可信环境"，不可信就换网络；可信环境内偶发 → 大概率上游/中间盒瞬时问题，重试即可，绝不关校验。**

## 术语小词典

| 术语 | 白话解释 |
|---|---|
| TLS / HTTPS | 在 HTTP 外面套一层加密 + 身份核验的协议 |
| 证书 | 服务器的"身份证"，由权威机构签发 |
| 证书链 | 身份证的"担保链"：网站证书 ← 中间证书 ← 根证书 |
| 根证书 | 系统/浏览器预装的"最终担保人"（如 DigiCert、Let's Encrypt） |
| 自签证书 | 自己给自己签的"身份证"，没有公认机构担保；出现在链里且不在信任列表 → 校验失败 |
| CA | Certificate Authority，签发证书的权威机构 |
| MITM | Man-in-the-Middle，中间人攻击 |
| WAF | Web Application Firewall，网站前面的防护层，也常负责 HTTPS 证书部署 |
| DIRECT | Clash 术语：不经过代理节点、直接连接 |

## 自测

> [!question]- 1. opencode 报"self signed certificate"，第一步该做什么？
> 三步定位：① 看 opencode 日志确认是哪个域名/provider；② 看代理日志确认直连还是走节点；③ 用 `openssl s_client` 看证书链和 `Verify return code`。先确认"谁在报错、走哪条路、证书长什么样"，再动手。

> [!question]- 2. 为什么"关了校验就正常"不等于"问题解决了"？
> 校验的作用是识破伪造证书。关掉校验只是不再检查，坏证书/攻击者依然在那里。它拆了安全报警器，而不是修好了故障。

> [!question]- 3. 什么时候该怀疑 MITM？
> 在**不可信网络**（公共 Wi-Fi、陌生代理）里出现自签证书报错，且多个网站/应用同时异常时，要提高警惕：先断网/换网络，别用禁用校验来"硬闯"。

## 相关

- [[somezhishi/somezhishi|somezhishi 库索引]]
- [[somezhishi/工具速查/opencode-TUI-速查表|opencode TUI 速查表]]

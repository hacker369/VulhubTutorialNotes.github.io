# Vulhub 通关笔记 · GitHub Pages 部署指南

本站点已构建为**纯静态文件**（Next.js 静态导出），无需服务器、无需数据库，直接部署到 GitHub Pages 即可，而且**部署后地址与你现在 docsify 版站点完全相同**。

## 为什么可以直接部署？

- **纯静态**：所有页面已预渲染为 HTML + JS，GitHub Pages 完美支持
- **Hash 路由**（`#/library`、`#/guide`、`#/vuln/...`）：不依赖服务器路由，放在任何子路径都不会 404
- **相对资源路径**：无论你的站点最终挂在 `https://用户名.github.io/仓库名/` 还是根路径，样式、脚本、数据都能正确加载，**零配置**
- **数据与界面分离**：268 篇笔记全部在 `data/vulns.json` 里，以后更新笔记内容只需替换这一个文件，**无需重新构建**

---

## 方式一：直接上传静态文件（推荐 · 约 5 分钟上线）

适合：不想折腾构建环境，希望立刻上线。

### 第 1 步：解压静态包

下载 `vulhub-notes-static-site.zip` 并解压，得到：

```
index.html          ← 站点入口（会覆盖你现在的 docsify index.html）
404.html
.nojekyll           ← ⚠️ 隐藏文件，极其重要，务必保留！
_next/              ← JS / CSS / 字体（约 2MB）
data/vulns.json     ← 全部 268 篇笔记数据
robots.txt
logo.svg
api
DEPLOY.md           ← 本文档（可留可删）
```

### 第 2 步：复制进你的仓库

```bash
git clone https://github.com/hacker369/VulhubTutorialNotes.github.io.git
cd VulhubTutorialNotes.github.io

# 把解压出的所有文件（含 .nojekyll）复制到仓库根目录，选择"覆盖"
cp -r /path/to/解压目录/* /path/to/解压目录/.nojekyll .
```

说明：

- 旧的 docsify `index.html` 会被新站点的 `index.html` **覆盖**，这就是切换新版
- 原有的 `.md` 教程文件、`README.md`、`_sidebar.md` 等**可以保留不动**，它们不会影响新站运行（还能继续当内容源码）
- ⚠️ `.nojekyll` 是隐藏文件。它的作用是告诉 GitHub Pages「不要用 Jekyll 处理」，否则 `_next/` 目录（下划线开头）会被忽略，导致**白屏、样式全丢**——这是 GitHub Pages 部署最经典的坑

### 第 3 步：提交并推送

```bash
git add -A
git commit -m "feat: 全新 Next.js 版 Vulhub 通关笔记站点"
git push
```

### 第 4 步：检查 Pages 设置

打开仓库 **Settings → Pages**：

- Source 应为 **Deploy from a branch**
- Branch 选 **main** + **/ (root)**

> 你现在的 docsify 站点已经配置过这些，通常**无需任何改动**。

### 第 5 步：访问

等待 1~2 分钟 GitHub 自动部署，然后访问你原来的站点地址，按 **Ctrl + F5** 强制刷新（清掉旧缓存）即可看到新版。

> 不熟悉命令行？可以用 **GitHub Desktop**（图形化 clone / commit / push）完成第 2、3 步。不建议用网页「Upload files」——`_next/` 里有上百个小文件，网页上传非常痛苦。

---

## 方式二：源码 + GitHub Actions 自动构建（进阶 · 适合长期维护）

适合：以后想自己改代码、改样式，push 后自动更新站点。

### 第 1 步：放入源码

下载 `vulhub-notes-source.zip` 解压，把以下内容复制进仓库根目录（原有 md 文件保留没问题）：

```
src/                 ← 全部前端源码
public/              ← 数据 + 图标
scripts/             ← 笔记解析脚本（md → vulns.json 流水线）
.github/             ← 自动部署工作流（deploy.yml）
package.json
bun.lock
next.config.ts
tsconfig.json
postcss.config.mjs
tailwind.config.ts
eslint.config.mjs
components.json
DEPLOY.md
```

### 第 2 步：切换 Pages 来源

**Settings → Pages → Build and deployment → Source** 改为 **GitHub Actions**（这一步必须手动改一次）。

### 第 3 步：推送触发构建

```bash
git add -A
git commit -m "ci: Next.js 源码入库 + GitHub Actions 自动部署"
git push
```

打开仓库 **Actions** 标签页可以看到「Deploy to GitHub Pages」工作流运行进度，约 2 分钟完成后自动发布。

> 工作流使用 Bun 安装依赖（依据 bun.lock 锁定版本），若你更习惯 npm，把 `bun install --frozen-lockfile` / `bun run build:static` 换成 `npm install` / `npm run build:static` 也可以（需自行生成 package-lock.json）。

---

## 以后如何更新笔记内容？

这是本站架构的最大优势——**数据和代码分离**：

| 你想改什么 | 方法 |
|---|---|
| 新增/修改漏洞笔记 | 用方式一：直接替换仓库里的 `data/vulns.json`，提交即可，**不用重新构建** |
| 同上（方式二） | 替换本地 `public/data/vulns.json` → push，Actions 自动构建 |
| 改界面文案/样式/功能 | 只有方式二可以：改 `src/` 源码 → push 自动重建 |
| 重新从 md 生成数据 | 运行 `python3 scripts/parse_vulns.py`（读取仓库 md 文件生成 vulns.json） |

> `vulns.json` 的格式：顶层 `{ generated, total, vulns: [...] }`，每篇含 id、title、component、type、cves、years、content（markdown 原文）等字段，首页统计卡、终端文案、类型分布图都会**根据这个文件自动重新计算**，不需要手动改任何界面代码。

---

## 部署后验证清单

- [ ] 打开站点：终端风首页 + 统计卡显示 268 / 129 / 194
- [ ] 「新人必读」入口和指南页正常（中英文都能切）
- [ ] 右上角 中/EN 切换正常，刷新后语言保持
- [ ] `#/library` 搜索、类型筛选、组件筛选正常
- [ ] 任意笔记详情页：图片（语雀 CDN）能显示、代码块高亮、目录锚点正常
- [ ] 手机打开排版正常

## 常见问题排查

**Q：部署后白屏 / 样式全丢？**
A：`.nojekyll` 没上传成功。它是隐藏文件，确认仓库根目录存在（`git ls-files | grep nojekyll` 应有输出），不存在就重新 add。

**Q：打开后一直转圈或显示加载失败？**
A：`data/vulns.json` 没在正确位置。它必须在仓库根目录的 `data/` 文件夹下，与 `_next/` 平级。

**Q：更新后内容没变化？**
A：两个原因：① 浏览器缓存 → Ctrl+F5 强刷；② Pages 部署有 1~2 分钟延迟，可在仓库 Actions / Deployments 里看部署状态。

**Q：私有仓库能用 GitHub Pages 吗？**
A：免费账号要求仓库公开；私有仓库需要 GitHub Pro 及以上。你的仓库本来就是公开的，无此问题。

**Q：想绑定自己的域名？**
A：仓库根目录加一个 `CNAME` 文件（内容为你的域名），DNS 加 CNAME 记录指向 `hacker369.github.io`，再到 Settings → Pages 填写域名。本站 hash 路由无需任何额外配置。

**Q：想在本地先预览静态包？**
A：解压后在目录里运行 `python3 -m http.server 8080`（或 `npx serve .`），浏览器访问 `http://localhost:8080`。⚠️ 不要直接双击 `index.html`——`file://` 协议下浏览器会拦截数据请求，导致一直显示加载中。

**Q：图片为什么放在语雀 CDN？会影响部署吗？**
A：不影响。图片是笔记原文引用的语雀外链，站点已设置 `no-referrer` 绕过防盗链。唯一风险是语雀日后调整图床策略，届时可把图片本地化到 `public/img/` 并批量替换 markdown 里的链接。

# EasyWord (单词轻松记)

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/lijiaxu2021/EasyWord)
[![Platform](https://img.shields.io/badge/platform-Android%20%7C%20Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://beeware.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**EasyWord** 是一款基于 Python (Toga/BeeWare) 开发的现代化跨平台单词记忆应用。它结合了极简主义设计、AI 智能辅助和科学的记忆方法，旨在为用户提供高效、轻松的英语学习体验。

本项目完全开源，支持 Android、Windows、macOS 和 Linux 平台。

---

## ✨ 核心功能 (Key Features)

### 1. 📚 智能词库管理 (Smart Library)
- **多词库支持**：创建无限个自定义词库（如“四级核心”、“雅思高频”、“考研难点”）。
- **批量导入**：支持从剪贴板粘贴文本，自动识别单词并导入。
- **AI 智能解析**：内置 SiliconFlow AI 接口，粘贴任意英文文章或单词列表，AI 自动提取单词、生成音标、中英文释义及双语例句。
- **管理便捷**：支持单词的增删改查，列表页支持勾选批量操作。

### 2. 🧠 沉浸式学习模式 (Immersive Study)
- **卡片式学习**：经典的 Flashcard 设计，正面展示单词，点击查看详情。
- **自动发音**：(计划中) 支持单词 TTS 发音。
- **记忆辅助**：
    - **音标显示**：标准的 IPA 音标。
    - **双语释义**：详尽的中文释义（含词性）和简洁的英文释义。
    - **场景例句**：每个单词配备 2-3 个双语例句，帮助在语境中记忆。
- **自动换行**：完美适配各种屏幕尺寸，长文本自动折行，阅读无障碍。

### 3. 📝 双模式检验系统 (Dual-Mode Quiz)
为了满足不同阶段的记忆需求，EasyWord 提供了两种检验模式：
- **选择题模式 (Multiple Choice)**：
    - 快速测试，从 4 个选项中选出正确释义。
    - 适合初记阶段，建立快速映射。
- **默写模式 (Spelling/Dictation)**：
    - 深度测试，仅显示中文释义，需手动拼写英文单词。
    - 适合复习阶段，确保精准拼写。
- **灵活范围**：支持“全库检验”或“自定义选词检验”。

### 4. 🔍 实时查词与学习 (Real-time Search)
- **AI 查词**：输入任意单词，AI 实时生成详细的音标、释义、例句及记忆方法。
- **自动入库**：查词结果自动保存到当前词库，形成学习闭环。
- **即时反馈**：搜索过程带有状态反馈，确保用户体验流畅。

### 5. 🛠️ 系统级功能 (System Utilities)
- **日志系统**：内置全自动日志记录，自动捕获运行时的错误和异常，保存为本地文件。
- **调试工具**：App 内置日志查看器，方便开发者和用户排查问题（点击首页右上角齿轮图标）。
- **本地数据库**：使用 SQLite 存储数据，完全离线运行（AI 功能除外），保护隐私。

---

## 📸 界面预览 (Screenshots)

> (此处将在后续版本更新中添加实际截图，包括：首页仪表盘、单词卡片、AI 导入界面、检验模式界面)

---

## 🛣️ 路线图 (Roadmap)

- [x] v1.0: 基础功能（词库、学习、检验）
- [x] v1.1: 实时查词、AI 记忆方法
- [ ] v1.2: 单词发音 (TTS)
- [ ] v1.3: 艾宾浩斯记忆曲线复习计划
- [ ] v1.4: 云端数据同步

---

## 🚀 快速开始 (Getting Started)

### 环境要求
- Python 3.8+
- Git
- BeeWare (Briefcase)

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone git@github.com:lijiaxu2021/EasyWord.git
   cd EasyWord
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install briefcase
   pip install -r requirements.txt
   ```

4. **运行开发模式**
   ```bash
   briefcase dev
   ```

5. **打包应用**
   - **Android**:
     ```bash
     briefcase create android
     briefcase build android
     briefcase package android
     ```
   - **Windows**:
     ```bash
     briefcase package windows
     ```

---

## 📅 更新日志 (Changelog)

### v1.1.1 (2026-02-09) - 修复与优化
- **[Fix]** 修复了 Toga 在 Android 上的样式废弃警告 (Padding/Alignment)。
- **[Fix]** 修复了 AI 查词结果解析和数据库保存的 Bug。
- **[UI]** 优化了单词卡片的排版，解决长文本截断问题，增加间距。
- **[UI]** 为查词功能增加了简单的输入反馈动画。

### v1.1.0 (2026-02-09) - 实时查词
- **[Feature]** 新增“查词”模块，支持 AI 实时分析。
- **[Feature]** 新增“记忆方法”字段，AI 自动生成助记指南。
- **[Feature]** 查词结果自动入库，实现“查学一体”。

### v1.0.0 (2026-02-09) - 正式发布版
- **[Feature]** 完成所有核心功能开发，包括词库、学习、检验。
- **[Fix]** 修复了单词卡片在长文本下不自动换行的问题，改用 `MultilineTextInput` 实现只读展示。
- **[Doc]** 新增详细的 `README.md` 文档。

### v0.9.0 (2026-02-09) - 日志系统与稳定性
- **[Feature]** 新增全局日志系统，启动即记录 `logs/log_*.txt`。
- **[Feature]** 新增 App 内日志查看器（设置页），支持查看和复制日志。
- **[Fix]** 修复了 `LibraryDetailView` 中因样式属性错误导致的白屏崩溃。
- **[Fix]** 优化了异常捕获逻辑，防止数据库操作失败导致闪退。

### v0.8.0 (2026-02-09) - 双模式检验
- **[Feature]** 新增“默写模式”，支持根据释义拼写单词。
- **[Feature]** 优化检验流程，支持在开始前选择“选择题”或“默写”。
- **[UI]** 优化词库详情页交互，点击单词直接查看/编辑，勾选框独立操作。

### v0.7.0 (2026-02-09) - AI 增强
- **[Fix]** 重构 `ai_service.py`，增加 JSON 解析的鲁棒性，自动过滤 Markdown 标记。
- **[Test]** 增加 `tests/test_ai_parsing.py` 单元测试。

### v0.6.0 (2026-02-09) - UI 统一
- **[UI]** 统一全应用为 Material Blue 风格。
- **[Fix]** 修复了 Toga 在 Android 上的布局溢出警告 (Flex 布局优化)。

---

## 🤝 贡献指南 (Contributing)

欢迎提交 Issue 和 Pull Request！
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证 (License)

本项目基于 MIT 许可证开源。详情请参阅 [LICENSE](LICENSE) 文件。

---

**EasyWord - Make Vocabulary Easy.**
Developed by [lijiaxu2021](https://github.com/lijiaxu2021) & Trae AI.

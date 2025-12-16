# PopGraph Studio (Z-StudioArt) 🎨

**PopGraph Studio** 是一款基于 AI 的智能设计工具，专注于为电商和营销场景生成高质量的**爆款海报**与**产品场景图**。

它结合了最新的 AIGC 技术（Z-Image-Turbo）与现代化的 Web 交互体验，让用户能够通过简单的文字描述，在几秒钟内生成专业级的营销素材。

![Status](https://img.shields.io/badge/Status-MVP%20Ready-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue) ![React](https://img.shields.io/badge/Frontend-React%2019-61dafb) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)

---

## 🚧 项目状态 (Project Status)

本项目目前处于 **High-Fidelity MVP (高保真最小可行性产品)** 阶段。

*   ✅ **核心功能已就绪**：智能海报生成、场景融合、模板系统、S3 图片存储等核心业务逻辑已完整实现并经过测试。
*   ✅ **前端高保真**：基于 React 19 的现代化 UI，包含完整的认证、支付演示、历史记录和创作工作台。
*   ⚠️ **演示模式数据存储**：为了便于快速部署和演示，目前的 `AuthService` (用户认证) 和 `PaymentService` (支付订单) 默认配置为 **内存存储 (In-Memory Storage)** 模式。这意味着**重启后端服务后，注册用户、订单记录和生成历史将会重置**。
    *   *下一步计划：集成 PostgreSQL 数据库以实现持久化存储。*

---

## ✨ 核心功能 (Key Features)

> 详细功能清单请参阅 [FEATURES.md](./FEATURES.md)

*   **🎨 智能海报生成 (AI Poster Generation)**: 输入场景描述和营销文案，AI 自动生成图文并茂的商业海报。
*   **🛍️ 场景融合 (Scene Fusion)**: 上传白底商品图，AI 自动将其融合进指定的背景场景中（虚拟摄影棚）。
*   **📐 灵活尺寸支持 (Multi-Dimension)**: 支持主流社交媒体尺寸 (1:1, 9:16, 16:9) 及智能构图。
*   **📝 智能模版 (Smart Templates)**: 内置多种营销模版（促销、节日、高级感），一键套用风格。
*   **🌍 双语支持 (Internationalization)**: 完美支持中文与英文界面切换，适应全球化创作需求。
*   **💎 现代 UI 设计 (Glassmorphism)**: 采用深色毛玻璃风格设计，提供沉浸式的创作体验。

---

## 🛠 技术栈 (Tech Stack)

### Frontend (前端)
*   **Framework**: React 19 + Vite
*   **Language**: TypeScript
*   **Styling**: Tailwind CSS (Glassmorphism Design System)
*   **State Management**: Zustand (with Persistence)
*   **Network**: Axios (Auto Token Refresh)
*   **Testing**: Vitest

### Backend (后端)
*   **Framework**: FastAPI (Python 3.10+)
*   **AI Model**: ModelScope Z-Image-Turbo (via Async API)
*   **Storage**: AWS S3 Compatible Object Storage (MinIO/OSS/S3)
*   **Image Processing**: Pillow (PIL) + NumPy (Product Extraction)
*   **Testing**: Pytest + Hypothesis (Property-Based Testing)
*   **Architecture**: Service-Oriented Architecture (SOA)

---

## 🚀 快速开始 (Getting Started)

### 1. 克隆项目
```bash
git clone https://github.com/xiongfazhan/Z-StudioArt.git
cd Z-StudioArt
```

### 2. 后端设置 (Backend)

确保你已安装 Python 3.10+。

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖你好
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 ModelScope API Key
# 提示：如果没有 S3 配置，系统会自动回退到 Base64 模式，无需额外配置即可运行演示。
```

**启动后端服务：**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端设置 (Frontend)

确保你已安装 Node.js 18+。

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

打开浏览器访问 `http://localhost:5173` 即可开始创作！

---

## 🗺️ 路线图 (Roadmap)

- [x] **MVP Phase 1**: 核心 AI 生成功能、前端 UI、内存级用户系统。
- [ ] **MVP Phase 2 (Current Focus)**: 
    - [ ] 集成 PostgreSQL 数据库，替换内存存储。
    - [ ] 完善 Alembic 数据库迁移脚本。
    - [ ] 对接真实支付网关回调。
- [ ] **Beta**: 用户自定义模板上传、社区分享功能。

---

## ⚙️ 环境变量配置

### Backend (`backend/.env`)
| 变量名 | 描述 | 默认值/示例 |
|---|---|---|
| `MODELSCOPE_API_KEY` | **[必需]** 阿里 ModelScope API 密钥 | `ms-...` |
| `S3_ENDPOINT` | (可选) S3 存储地址 | `https://oss-cn-hangzhou.aliyuncs.com` |
| `S3_ACCESS_KEY` | (可选) S3 Access Key | `LTAI...` |

### Frontend (`frontend/.env`)
| 变量名 | 描述 | 默认值 |
|---|---|---|
| `VITE_API_BASE_URL` | 后端 API 地址 | `http://localhost:8000` |

---

## 🤝 贡献 (Contributing)

欢迎提交 Issue 或 Pull Request 来改进这个项目！

1.  Fork 本仓库
2.  新建 Feature 分支 (`git checkout -b feature/AmazingFeature`)
3.  提交更改 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  提交 Pull Request

## 📄 许可证 (License)

Distributed under the MIT License. See `LICENSE` for more information.
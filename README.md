# 足球训练与社区 App · Soccer Training & Community

基于 UniApp / Vue 3 前端与 FastAPI + MySQL 后端的足球应用，包含训练、赛事、技术学院、健康营养、个人档案和球员社区模块，提供可选的短信认证与 AI 功能。

## 本地运行

1. 后端：进入 `backend/`，建立 Python 虚拟环境，运行 `pip install -r requirements.txt`。
2. 将 `backend/.env.example` 复制为 `backend/.env`，填写自己的数据库配置。设置独立、随机的 `JWT_SECRET_KEY`（至少 32 字符）。例如运行 `python -c "import secrets; print(secrets.token_urlsafe(48))"` 生成。
3. 启动本地 MySQL，使用专用开发账号。当前初始化逻辑会创建配置的数据库，需要该开发账号具有相应权限。
4. 在 `backend/` 中运行 `python run.py`，默认仅监听 `127.0.0.1:8000`；API 文档位于 `/docs`。
5. 用 HBuilderX 打开 `Frontend/`，运行到浏览器；本地 API 地址在 `Frontend/utils/api.js` 中配置。

## 可选服务

短信与 AI 默认关闭。需要时在本地 `.env` 填写自己的服务配置，并显式设置 `SMS_ENABLED=true` 或 `AI_ENABLED=true`。这些服务可能产生费用。未开启短信时，依赖短信的注册、重置密码等操作不可用；不会绕过验证码验证。

## 开源版本

此仓库包含清理后的源码；不包含原作者的密钥、数据库、用户上传头像、个人账号资料、缓存或编译产物。历史开发文档仅供参考，当前环境配置以本 README 和 `.env.example` 为准。本项目是本地开发/演示版本，发布公网服务前需要独立完成认证、限流和部署审查。

代码采用 MIT 许可证；第三方依赖和素材保留各自权利。

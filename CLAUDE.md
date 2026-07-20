# CLAUDE.md — Guía de trabajo del proyecto / 项目工作指引

> Sistema web para la gestión y optimización de donaciones de alimentos (República Dominicana).
> 多米尼加共和国食品捐赠管理与优化 Web 系统。
>
> **Este archivo guía a la IA (Claude / GitHub Copilot) y al equipo. Léelo al iniciar cada sesión.**
> **本文件用于指引 AI 助手与开发者。每次开始工作前先阅读。**

---

## 1. Resumen del proyecto / 项目概述

- **Objetivo / 目标**: Registrar, organizar y distribuir excedentes de alimentos con optimización logística (FEFO + geolocalización), cumpliendo la ley dominicana. / 登记、组织并分配剩余食物，结合 FEFO 与地理定位优化物流，符合多米尼加法律。
- **Actores / 角色**: Donante (捐赠者), Receptor (接收组织), Banco de Alimentos (食物银行), Administrador (管理员).
- **Usuario principal / 主要用户**: es principiante y NO programa. Explicar con lenguaje simple. / 主要用户是不懂代码的小白，需用通俗语言解释。

## 2. Stack tecnológico / 技术栈

| Capa / 层 | Tecnología / 技术 |
|---|---|
| Frontend 前端 | React 19 + Vite + JavaScript |
| Backend 后端 | Python + FastAPI |
| Base de datos 数据库 | PostgreSQL + PostGIS |
| Auth 认证 | JWT + bcrypt (coste ≥ 12) |
| Servicios externos 外部服务 | Gemini IA, Google Sheets, Correo, Mapa — **SIMULADOS al inicio / 初期全部模拟** |

## 3. Índice de documentos estándar / 标准文档索引

> Hay documentación paralela en **español** y **chino**. Mantener ambas sincronizadas.
> 文档分**西班牙语**和**中文**两套，需保持同步更新。

| Tema / 主题 | Español | 中文 |
|---|---|---|
| Requisitos / 需求规格 | [docs/es/01-requisitos.md](docs/es/01-requisitos.md) | [docs/zh/01-需求规格.md](docs/zh/01-需求规格.md) |
| Arquitectura técnica / 技术架构 | [docs/es/02-arquitectura-tecnica.md](docs/es/02-arquitectura-tecnica.md) | [docs/zh/02-技术架构.md](docs/zh/02-技术架构.md) |
| Guía de diseño / 设计规范 | [docs/es/03-guia-diseno.md](docs/es/03-guia-diseno.md) | [docs/zh/03-设计规范.md](docs/zh/03-设计规范.md) |
| Plan de desarrollo / 开发计划 | [docs/es/04-plan-desarrollo.md](docs/es/04-plan-desarrollo.md) | [docs/zh/04-开发计划.md](docs/zh/04-开发计划.md) |
| Estándares de código / 代码规范 | [docs/es/05-estandares-codigo.md](docs/es/05-estandares-codigo.md) | [docs/zh/05-代码规范.md](docs/zh/05-代码规范.md) |
| Seguridad / 安全规范 | [docs/es/06-seguridad.md](docs/es/06-seguridad.md) | [docs/zh/06-安全规范.md](docs/zh/06-安全规范.md) |
| Configuración de entorno / 环境配置 | [docs/es/07-configuracion-entorno.md](docs/es/07-configuracion-entorno.md) | [docs/zh/07-环境配置.md](docs/zh/07-环境配置.md) |
| Navegación docs / 文档导航 | [docs/README.md](docs/README.md) | (mismo / 同上) |
| Bitácora / 开发日志 | [bitacora-desarrollo/](bitacora-desarrollo/) | (bilingüe / 双语) |

Fuentes originales / 原始来源: [Descripcion.md](Descripcion.md) · SQL: `新建文件夹/Base de datos/能用DonacionesAlimentosRD_PostgreSQL_Fixed.sql`.

## 4. Reglas de trabajo / 工作规则

1. **Idioma de comunicación / 沟通语言**: responder SIEMPRE en **Español + 中文**. / 始终用西班牙语 + 中文回复。
2. **Idioma del código / 代码语言**: **español como principal**. Variables, funciones, clases, rutas de API, nombres de archivos y commits en español. Palabras clave técnicas y librerías quedan en inglés. Ver [docs/es/05-estandares-codigo.md](docs/es/05-estandares-codigo.md). / 代码以西班牙语为主：变量、函数、类、API 路径、文件名、提交信息用西语；技术关键字与库名保留英文。
3. **Documentación bilingüe / 双语文档**: todo documento estándar existe en `docs/es/` y `docs/zh/`. / 每份标准文档在 es 和 zh 各有一份。
4. **Avance por fases / 分阶段推进**: NO hacer demasiado de una vez. Completar y verificar una fase antes de seguir. Ver [docs/es/04-plan-desarrollo.md](docs/es/04-plan-desarrollo.md). / 不要一口气做太多，每阶段验证后再继续。
5. **Bitácora diaria / 每日日志**: al terminar cada sesión de desarrollo, actualizar el archivo del día en `bitacora-desarrollo/AAAA-MM-DD.md` con lo completado y lo pendiente. / 每次开发结束，更新当天日志（已完成 + 待办）。
6. **Seguridad / 安全**: seguir [docs/es/06-seguridad.md](docs/es/06-seguridad.md). Nunca exponer secretos; contraseñas y claves van en `backend/.env` (NO se sube al repo). / 遵守安全规范；密钥放 `.env`，绝不提交。
7. **Datos sensibles del usuario / 用户敏感信息**: la contraseña de la BD y las API keys las coloca el usuario en `.env`. La IA no las solicita por chat. / 数据库密码与密钥由用户填入 `.env`，AI 不через聊天索取。

## 5. Estructura de carpetas / 目录结构

```
DonacionesAlimentosRD/
├── CLAUDE.md                 # Este archivo / 本文件
├── Descripcion.md            # Requisitos originales / 原始需求
├── docs/                     # Documentación estándar (es + zh) / 标准文档
│   ├── README.md
│   ├── es/                   # Español
│   └── zh/                   # 中文
├── bitacora-desarrollo/      # Registro diario / 开发日志
├── backend/                  # FastAPI (Python)
│   └── app/{config,database,models,routers,schemas,services,utils}
├── frontend/                 # React + Vite
│   └── src/
└── 新建文件夹/Base de datos/  # Script SQL PostgreSQL / 建库脚本
```

## 6. Flujo de una sesión de trabajo / 单次工作流程

1. Leer `CLAUDE.md` y la memoria de sesión. / 阅读本文件与会话记忆。
2. Revisar la bitácora del día anterior (pendientes). / 查看上一日日志的待办。
3. Confirmar la fase actual en el plan. / 确认当前阶段。
4. Trabajar en pasos pequeños y verificables. / 小步开发并验证。
5. Actualizar la bitácora del día. / 更新当天日志。
6. Resumir al usuario en Español + 中文 y pedir confirmación para seguir. / 双语总结并请用户确认后再继续。

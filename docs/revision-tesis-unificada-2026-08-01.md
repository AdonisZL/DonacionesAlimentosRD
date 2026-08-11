# Revisión de "Tesis - Unificada.pdf" (v2) / 论文《Tesis - Unificada.pdf》审阅报告（第二版）

> Fecha revisión / 审阅日期: 2026-08-01 (19:33) · Versión / 版本: **223 páginas** (la anterior tenía 236) / **223 页**（上一版 236 页）
> Objetivo / 目标: Verificar el estado tras las últimas correcciones y listar lo que aún falta. / 核对最新修改后的状态并列出仍缺失的问题。

---

## 0. Resumen / 摘要

En esta nueva versión **se corrigieron varios problemas** (referencias, id_merma, copia-pega de tabla, etc.), pero **siguen pendientes los 4 problemas más graves de contenido faltante (placeholders)** y varias inconsistencias de numeración e índice. Además, la renumeración de las tablas BARD **dejó el índice desincronizado**.
新版**已修正若干问题**（参考文献、id_merma、表格误复制等），但**四个最严重的缺失内容（占位符）仍未解决**，且编号/目录仍不一致。此外，BARD 表格重新编号后**目录未同步更新**。

Prioridad / 优先级: 🔴 Crítico · 🟠 Alto · 🟡 Medio · ⚪ Menor

---

## 1. ✅ Ya corregido en esta versión / 本版已修正

| # | Corrección confirmada / 已确认修正 |
|---|---|
| ✔ | **Referencias bibliográficas depuradas:** ya no hay entradas duplicadas (Pressman, Sommerville, Beck, Arias, Brooke, Schwaber, etc. aparecen una sola vez). / 参考文献去重完成。 |
| ✔ | **Referencias en orden alfabético:** la lista ahora empieza correctamente por *Akkerman*. / 参考文献已按字母排序（以 Akkerman 开头）。 |
| ✔ | **Marcador residual "[1]"** eliminado de las citas (p. ej. Atlassian). / 引用中残留的"[1]"已删除。 |
| ✔ | **Copia-pega de la tabla de dificultades BARD corregido:** ahora es "Tabla-33" con una interpretación correcta sobre cuellos de botella. / BARD"瓶颈"表误复制段落已修正。 |
| ✔ | **Diccionario de datos:** el campo PK de mermas ahora es `id_merma` (antes `id_marca`). / mermas 表主键已改为 `id_merma`。 |
| ✔ | **"Cuadro 11"** ya no aparece con esa nomenclatura. / "Cuadro 11"命名问题已消除。 |
| ✔ | **Typo "quantitative"** en la referencia de Hernández-Sampieri eliminado. / Hernández 条目"quantitative"拼写错误已消除。 |

---

## 2. 🔴 Contenido faltante / placeholders — SIGUE PENDIENTE / 仍缺失（严重）

| # | Ubicación / 位置 | Estado actual / 当前状态 |
|---|---|---|
| 2.1 | **Anexo A** (pág. 223) | ❌ Sigue literal: `[PENDIENTE] Adjuntar los tres instrumentos completos...`. **Los cuestionarios y la guía de entrevista NO están adjuntos.** / 仍是占位符，三份问卷未附。 |
| 2.2 | **4.2 Interpretación de los Resultados** | ❌ Sigue vacío: *"Esta sección recogerá los aportes e inferencias... una vez completada la fase de campo"*. **No hay interpretación real.** / 结果解读仍为空占位段。 |
| 2.3 | **4.1 Análisis de los Resultados** (intro) | ❌ Sigue en futuro: *"Esta sección se desarrollará una vez concluida la fase de entrevistas..."*, pese a que las tablas ya están. / 引言仍用将来时。 |
| 2.4 | **Cap. VII Cumplimiento de Objetivos** | ❌ Sigue abriendo con la instrucción sin borrar: *"Elaborar una tabla que mapee cada objetivo específico..."*. / 第七章仍以未删指令开头。 |
| 2.5 | **Dedicatoria** (pág. 9) | ❌ Sigue **vacía** (solo el título). / 献词页仍空白。 |

---

## 3. 🟠 Numeración e índice — PENDIENTE / 编号与目录（高）

| # | Problema / 问题 |
|---|---|
| 3.1 | **⚠️ NUEVO desajuste índice↔cuerpo:** al renumerar las tablas BARD en el cuerpo (ahora van Tabla-32 Tiempo → **33** Dificultades → **34** Ponderación → **35** Condiciones → **36** Radio → **37/38/39/40** vida útil), el **índice NO se actualizó** y todavía lista "Tabla-32 Dificultades", "Tabla-33 Ponderación", etc. Hay que **regenerar el índice de tablas**. / BARD 表在正文已重编号(32→40)，但目录未更新，须重建表目录。 |
| 3.2 | **Números de tabla duplicados (global):** las series `Tabla 1–5` y `Tabla 6–12` (metodología/requisitos) siguen chocando con `Tabla -6 … Tabla -40` (encuestas). Los números **6–12 se repiten** en dos capítulos. / 表号 6–12 仍在两章重复。 |
| 3.3 | **Ilustración 16 duplicada:** sigue apareciendo dos veces (texto idéntico "ERD del módulo de entregas y confirmación"), tanto en el índice como en el cuerpo. / 插图 16 仍重复两次。 |
| 3.4 | **Sección "5.2" duplicada:** "5.2 Requerimientos Tecnológicos" y "5.2 Reglas de Negocio" siguen con el mismo número (la 2.ª debería ser 5.3). / 两个"5.2"节仍存在。 |
| 3.5 | **Índice: "1.1.2. Internacional"** sigue mal; debería ser **"1.2.2."**. / 目录"1.1.2"仍错，应为"1.2.2"。 |
| 3.6 | **Índice incompleto:** el cuerpo tiene **"9.2 Recomendaciones Metodológicas"** pero el índice solo lista 9.1. / 正文有 9.2，目录仅列 9.1。 |
| 3.7 | **Índice de ilustraciones:** a *Ilustración 6* le falta el número de página. / 目录插图 6 缺页码。 |

---

## 4. 🟡 Consistencia de datos y stack — PENDIENTE / 数据与技术栈（中）

| # | Ubicación | Problema / 问题 |
|---|---|---|
| 4.1 | Tabla 12 Formales | ❌ Encabezado `n=27` pero los porcentajes de la tabla son de n=28 y el texto usa n=27 (85.2%). Unificar base y recalcular. / n=27 表头与 n=28 数据、n=27 正文不一致。 |
| 4.2 | Tabla 30 Independientes | ❌ Texto dice `n=310` pero la tabla muestra `313`. / 正文 310 与表 313 不符。 |
| 4.3 | Muestra / 样本 | ❌ `n=68` (3.1.4) vs `n=67` (3.3, 20+20+2+25); cálculo `n=384` vs tablas `n=387`. / 样本 68/67、384/387 仍矛盾。 |
| 4.4 | 6.2 MoSCoW | ❌ Sigue definido como **"(Alta, Media, Could, Won't)"** (mezcla incorrecta) y las prioridades no son uniformes entre tablas (Alta/Media vs Must/Should/Could). / MoSCoW 定义错误且各表标注不统一。 |
| 4.5 | Tabla 6 (stack) | ⚠️ Indica **React 19 + Next.js (SSR)**, pero la implementación real usa **React + Vite** (`.jsx`, `vite.config.js`). Verificar también Python 3.14 / PostgreSQL 18. Alinear documento con lo construido. / 技术表写 Next.js，但实际用 React+Vite，须核实并对齐。 |
| 4.6 | 2.6.1 JWT / 2.10 SMTP | ⚠️ Siguen mencionando "aplicación móvil / cliente móvil" en un **sistema web**. / JWT/SMTP 节仍称"移动应用"。 |
| 4.7 | Cap. VII RF-25 / RF-27 | ⚠️ Marcados "COMPLETO" pero el resultado indica *"Falta modelo evidencia_entrega"* (RF-25) y *"PDF local sin firma digital"* (RF-27). Aclarar estado real. / RF-25/RF-27 标"完成"但结果显示有缺口。 |

---

## 5. ⚪ Ortografía / formato menor — PENDIENTE / 拼写与小问题（低）

| # | Ubicación | Corrección / 更正 |
|---|---|---|
| 5.1 | 1.2 | "de **serviran** como referencia" → "servirán". |
| 5.2 | 2.2.1 | "Canal informal e independiente: **Ex exige**" → "Exige". |
| 5.3 | Ref. Hanson & Ahmadi | Texto francés corrupto "las aplicaciones **mobiles para réduiremle gaspillage**" — reescribir el título/traducción. / Hanson 条目法语文字损坏，须重写。 |
| 5.4 | Cap. IV | "Fuente: Elaboración Propia..." sigue **duplicada** bajo muchas tablas. / 多表下"Fuente"仍重复两行。 |
| 5.5 | 4.1.5 Receptoras | Las tablas siguen **sin número, sin fuente y sin interpretación** (formato distinto al resto). / 接收组织表仍无表号/来源/解读。 |

---

## 6. Prioridad de corrección / 修改优先顺序

1. 🔴 Completar **Anexo A**, **4.2 Interpretación**, quitar placeholders de **4.1** y **Cap. VII**, y la **Dedicatoria**. / 补齐附录A、4.2解读、删除4.1与第七章占位符、写献词。
2. 🟠 **Regenerar el índice** (tablas BARD 32→40, ilustración 16, sección 5.3, 1.2.2, 9.2). / 重建目录。
3. 🟡 Corregir descuadres de datos (n=27/28, 310/313, 67/68, 384/387) y MoSCoW. / 修正数据与MoSCoW。
4. 🟡 Alinear stack documentado (Next.js vs Vite). / 对齐技术栈。
5. ⚪ Corrector ortográfico final. / 最终拼写检查。

---

> Nota / 备注: Informe basado en extracción de texto del PDF; los diagramas e imágenes (casos de uso, secuencia, ER, pantallas) no se verifican visualmente y deben revisarse aparte. / 本报告基于 PDF 文本提取；图表/截图需另行目视核对。

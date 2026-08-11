# Revisión final de la tesis PDF / 论文 PDF 最终审查

**Archivo revisado / 审查文件:** `Tesis - Unificada.pdf`  
**Fecha / 日期:** 2026-08-01  
**Extensión / 页数:** 235 páginas  
**Método / 方法:** extracción de texto página por página, revisión de índice, capítulos, conclusiones, referencias y anexos. Las páginas indicadas abajo son páginas del PDF; el número impreso puede ser distinto.

## Dictamen general / 总体结论

**No debe considerarse todavía una versión final para entrega.** El PDF conserva marcadores explícitos `[PENDIENTE]`, anexos incompletos, números de página desactualizados y contradicciones entre el estado real del prototipo y las afirmaciones del Capítulo VII y las conclusiones.

**目前不建议将该 PDF 作为最终提交版。** 文件中仍然保留 `[PENDIENTE]` 占位符、未完成的附录、过期目录页码，并且第七章/结论对原型完成度的表述与实际实现状态不一致。

## 1. Bloqueadores antes de entregar / 提交前必须修复

| Prioridad | Página PDF | Problema / 问题 | Qué corregir / 修改建议 |
|---|---:|---|---|
| **CRÍTICA** | 8-9, 235 | El índice y los anexos contienen `[PENDIENTE]`. Faltan el listado técnico de las 20 reglas de negocio, el diccionario/diagrama de datos como anexo y las capturas de pantalla. El Anexo A también indica que faltan los tres instrumentos completos. | Completar e insertar los anexos B, C y D; adjuntar los tres instrumentos y el consentimiento informado; eliminar todos los marcadores `[PENDIENTE]`. |
| **CRÍTICA** | 128 | Se indica `[PENDIENTE] Sistematizar las entrevistas a los 3 informantes clave`. | Añadir método de análisis, participantes, respuestas resumidas, categorías, evidencias y relación con los requisitos; o retirar esa afirmación del diseño metodológico si las entrevistas no fueron realizadas. |
| **CRÍTICA** | 207-214 | RF-13, RF-25, RF-26 y RF-27 aparecen como **COMPLETO**, aunque el propio texto reconoce correo simulado, falta de modelo/evidencia de entrega, exportación local simulada y PDF sin firma digital. | Cambiar el estado a `PARCIAL` y reflejarlo en el resumen global, conclusiones y recomendaciones; solo usar `COMPLETO` si se implementó y verificó realmente. |
| **CRÍTICA** | 215-216 | Las conclusiones afirman integración efectiva de Google Maps/Gemini y que la seguridad permite deducciones fiscales, pero el Capítulo VII reconoce simulaciones y que el PDF fiscal no tiene firma digital. | Redactar las conclusiones en términos de prototipo: “preparado/simulado/verificado en entorno local”. No afirmar validez fiscal ni cumplimiento legal definitivo sin firma digital y validación institucional de DGII. |
| **ALTA** | 3-9 | El índice tiene páginas antiguas: presenta capítulos VII-IX en la página 125, referencias en 128 y anexos en 142; en el PDF aparecen aproximadamente en las páginas 207, 215-216, 217 y 235. | Regenerar el índice general, índice de tablas y cualquier índice adicional después de cerrar el contenido y la paginación. |

## 2. Estructura y numeración / 结构与编号

- En el índice aparece `1.1.2 Internacional` bajo `1.2 Antecedentes`; debe revisarse como `1.2.2` o corregirse según la estructura real.
- En el índice se repite `3.4.1` para **Análisis Documental** y **Entrevistas Estructuradas**.
- El índice salta de `3.4.3` a `3.4.5`; falta `3.4.4` o debe renumerarse.
- `3.7.2`, `3.7.3` y `3.7.4` aparecen mezclados dentro de la sección 3.5; deben comprobarse contra los encabezados reales.
- El formato de los capítulos no es uniforme: se usa `CAPÍTULO IV.` pero `CAPÍTULO V:` y `CAPÍTULO VI:`. Elegir un solo estilo.
- El documento contiene tablas, diagramas y figuras, pero el índice mostrado solo incluye tablas. Añadir y actualizar un **Índice de Figuras/Diagramas** si lo exige el reglamento universitario.
- Revisar la numeración de preguntas en resultados: aparece `Pregunta .` en una tabla de donantes independientes (PDF p. 127).

## 3. Coherencia metodológica y resultados / 方法与结果一致性

- Se usan tamaños muestrales distintos (`n=384`, `n=387`, `n=28`, `n=26` y piloto `n=9`). Debe explicarse por qué cambia el denominador, quién fue excluido y qué preguntas no fueron respondidas.
- La tabla de la pregunta 6 de donantes independientes usa `n=384`, mientras otras usan `n=387`; agregar una nota metodológica explícita.
- El texto debe distinguir claramente entre resultados de encuestas/entrevistas y pruebas técnicas del prototipo. No presentar una prueba de endpoint como evidencia de impacto social.
- Los resultados deben incluir, cuando corresponda, instrumento, fecha, muestra, criterio de aprobación, evidencia reproducible y limitaciones.
- La afirmación de que FEFO fue “técnicamente superior” requiere una comparación o métrica de referencia; si no existe, cambiarla por “adecuado para priorizar productos por vencimiento” o documentar el experimento comparativo.
- La afirmación de que el sistema “redujo los tiempos” requiere mediciones antes/después. Si solo hubo simulación, indicar que se trata de una estimación o resultado del piloto controlado.

## 4. Estado técnico y cumplimiento legal / 技术状态与法律合规

Debe existir una única matriz de verdad entre implementación, pruebas y tesis:

- **RF-13:** las alertas por correo están simuladas; declarar el alcance exacto.
- **RF-17:** el cálculo de Google Maps/Distance Matrix se describe como Haversine/simulado; no presentarlo como tiempo real de Google Maps.
- **RF-18:** Gemini está simulado; conservar la restricción de que no modifica la decisión determinista.
- **RF-25:** falta la evidencia fotográfica/modelo/end-point según el propio texto.
- **RF-26:** Google Sheets es una URL/archivo local simulado, no una publicación real en API v4.
- **RF-27:** el hash encadenado aporta integridad, pero no equivale a una firma digital ni demuestra aceptación fiscal por DGII.
- **RNF-09, RNF-11, RNF-13, RNF-16 y RNF-18:** accesibilidad WCAG, TLS, OWASP ZAP, cobertura completa y responsive deben marcarse como verificados solo si existen mediciones y reportes anexos.
- Revisar que “32/32 RF” no oculte requisitos parcialmente implementados. Es mejor presentar `implementado`, `simulado`, `parcial` y `pendiente` en columnas separadas.

## 5. Referencias y formato / 参考文献与格式

- La referencia de **Arias (2012)** aparece repetida en varias formas en las páginas de referencias; conservar una sola entrada normalizada.
- Revisar duplicados y uniformidad de autores, año, título, editorial, URL, DOI y fecha de consulta.
- Verificar especialmente las fuentes de blogs y las referencias fechadas en 2026; conservarlas solo si son consultables y pertinentes.
- Comprobar que cada cita dentro del texto exista en referencias y que cada referencia sea citada en el texto.
- Corregir la puntuación visible en las conclusiones: aparece `transparente..` en la página 216.
- Revisar caracteres extraños, espacios y codificación tras la exportación final; el texto extraído del PDF muestra caracteres deformados en acentos, por lo que conviene abrir el PDF en otro visor y comprobar visualmente títulos, tildes, tablas y símbolos matemáticos.

## 6. Orden recomendado de cierre / 建议完成顺序

1. Completar anexos A-D y sistematizar las entrevistas.
2. Decidir el estado real de RF-13, RF-17, RF-18, RF-25, RF-26 y RF-27; corregir la matriz, Capítulo VII, conclusiones y recomendaciones.
3. Revisar resultados y tamaños muestrales, incluyendo notas de exclusión y limitaciones.
4. Corregir numeración de secciones, capítulos, tablas, figuras y preguntas.
5. Regenerar índices y paginación después de terminar el contenido.
6. Normalizar referencias y ejecutar una revisión final de citas cruzadas.
7. Exportar una nueva versión PDF y hacer una última lectura visual de todas las páginas, especialmente tablas, diagramas, anexos y saltos de página.

## Checklist de aceptación / 最终验收清单

- [ ] No queda ningún `[PENDIENTE]`, `TODO` ni texto de trabajo.
- [ ] Los anexos A, B, C y D están realmente incluidos.
- [ ] El índice coincide con los títulos y páginas finales.
- [ ] Los estados `completo/parcial/simulado/pendiente` coinciden con el sistema y las pruebas.
- [ ] Las conclusiones no prometen integración o validez legal no demostrada.
- [ ] Se explican todos los tamaños de muestra y denominadores.
- [ ] Las referencias no están duplicadas y las citas cruzan correctamente.
- [ ] Se verificó visualmente el PDF final en un visor PDF real.

**Resultado / 结果:** se requiere una nueva iteración del documento antes de considerarlo versión final.

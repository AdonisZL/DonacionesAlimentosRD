Diseño y desarrollo de un sistema web para la gestión y optimización de donaciones de alimentos en la República Dominicana
多米尼加共和国食品捐赠管理与优化Web系统的设计与开发

Justificación
La creación de un sistema web para la gestión y optimización de donaciones de alimentos en la República Dominicana se justifica por la creciente necesidad de enfrentar el problema de la inseguridad alimentaria desde una perspectiva de acceso, eficiencia y trazabilidad. Aunque existen iniciativas de asistencia alimentaria y bancos de alimentos, la ausencia de una plataforma digital integral limita la capacidad de coordinar el rescate de excedentes y garantizar que lleguen oportunamente a las comunidades más vulnerables.
Actualmente, la gestión de donaciones se enfrenta a tres obstáculos críticos: la ineficiencia logística, las barreras económicas derivadas de la inflación y la falta de trazabilidad en tiempo real. Estos factores provocan que toneladas de alimentos se pierdan en el campo y que las organizaciones sociales no puedan responder de manera adecuada a la demanda creciente. Además, la normativa nacional —como la Ley No. 589-16 de Soberanía y Seguridad Alimentaria y el Código Tributario (Ley 11-92)— exige mecanismos de control y transparencia que las empresas no pueden cumplir con los métodos tradicionales basados en hojas de cálculo o registros manuales.
El desarrollo de una plataforma digital permitirá centralizar la información de donantes, receptores y bancos de alimentos, aplicar métodos de gestión de inventario como FEFO (First Expired, First Out), y generar reportes sistematizados que respalden tanto la transparencia como los beneficios fiscales. Asimismo, la incorporación de algoritmos de emparejamiento y un módulo básico de inteligencia artificial contribuirá a optimizar la distribución y reducir el desperdicio, alineando la innovación tecnológica con los objetivos de seguridad alimentaria del país.
En este sentido, el proyecto no solo responde a una necesidad social urgente, sino que también aporta una solución tecnológica sostenible que fortalece la cultura de solidaridad, mejora la eficiencia de los bancos de alimentos y apoya el cumplimiento de la normativa vigente. Al facilitar la trazabilidad y la coordinación institucional, se contribuye directamente a la reducción del hambre y la pobreza, impactando positivamente en la salud pública y en el desarrollo social de la República Dominicana.

Objetivos
Objetivo General
Diseñar y desarrollar un sistema web para la gestión eficiente de donaciones de alimentos, que permita registrar, organizar y distribuir excedentes mediante algoritmos de optimización logística en cumplimiento con la normativa legal dominicana, con el fin de reducir el desperdicio y fortalecer la seguridad alimentaria en la República Dominicana.

Objetivos Específicos
OE1. Registrar y organizar la información de donantes, receptores y bancos de alimentos mediante formularios estructurados y una base de datos centralizada, con el propósito de mantener un control ordenado, actualizado y trazable de los actores del sistema.
OE2. Implementar un módulo de inventario dinámico para el almacenamiento y control de los excedentes alimentarios indexados por su vida útil residual, con el objetivo de estructurar los datos necesarios para mitigar el desperdicio de productos perecederos.
OE3. Desarrollar un mecanismo de emparejamiento semiautomático entre oferta y demanda basado en un motor de reglas determinista que integra el ordenamiento FEFO, filtrado geoespacial con PostGIS y restricciones del receptor, complementado por la API de Gemini para la normalización de texto a JSON mediante reconocimiento de entidades y la generación de justificaciones en lenguaje natural, requiriendo validación humana obligatoria.
OE4. Generar reportes sistematizados sobre donaciones, inventario y distribución mediante el procesamiento estructurado de los datos del sistema, con el propósito de garantizar transparencia y apoyar la gestión de beneficios fiscales y rendición de cuentas.
OE5. Implementar mecanismos de control de acceso y protección de datos mediante autenticación segura y gestión de roles, para asegurar la confidencialidad de los donantes y la integridad de la información registrada.

Reglas de Negocio (RN)
El comportamiento lógico del sistema está condicionado por el marco legal dominicano y las mejores prácticas de logística:

1. Reglas sobre actores y registro:
   RN-01 (Identificación Fiscal): Es obligatorio el Registro Nacional de Contribuyentes (RNC) para donantes jurídicos, indispensable para la emisión de comprobantes fiscales de donación según la Ley 11-92.
   RN-02 (Validez Legal de Receptores): Solo podrán recibir donaciones las organizaciones que cuenten con personería jurídica vigente, registro ante la Procuraduría General de la República o reconocimiento explícito como bancos de alimentos.
   RN-03 (Unicidad de Rol por Usuario): Cada usuario poseerá un único rol principal en el sistema (donante, receptor, banco o administrador). Una misma cuenta de correo electrónico no podrá registrarse simultáneamente en múltiples roles.
2. Reglas sobre inventario y vencimiento:
   RN-04 (Aptitud de Consumo): Conforme a la Ley No. 589-16, el sistema rechazará automáticamente lotes cuya fecha de vencimiento sea menor o igual al día actual o no cumpla con los estándares de aptitud para consumo humano.
   RN-05 (Ventana Mínima de Donación): Todo lote de alimentos deberá registrarse respetando un umbral mínimo de días previos a su vencimiento según su categoría (No perecedero: 30–90 días; Semi-perecedero: 15–30 días; Perecedero: 1–5 días; Congelado: 30–60 días). Estos umbrales son parametrizables por el administrador del banco de alimentos.
   RN-06 (Prioridad FEFO): El inventario asignará prioridad máxima de despacho y emparejamiento a los alimentos con fecha de caducidad más cercana (First Expired, First Out), en alineación con las guías de la FAO.
   RN-07 (Cadena de Frío): Los productos que requieran refrigeración o congelación solo se emparejarán con receptores que declaren formalmente contar con la infraestructura y capacidad de almacenamiento adecuada.
   RN-08 (Trazabilidad de Lote): Cada lote de alimentos recibirá un identificador único, síncrono e inmutable. Cualquier modificación posterior en sus atributos deberá registrarse obligatoriamente como un nuevo movimiento en la bitácora de auditoría.
   RN-09 (Registro Obligatorio de Mermas): Toda declaración de merma o desecho de alimentos requerirá la especificación obligatoria del motivo del descarte (vencimiento, daño, contaminación, rechazo en destino) y la identificación del usuario responsable.
3. Reglas sobre emparejamiento y entrega
   RN-10 (Radio Geográfico Logístico): El algoritmo de emparejamiento buscará receptores elegibles dentro de un radio geográfico inicial de 25 km, expandiéndose automáticamente hasta un límite máximo configurable por el administrador. Para efectos de esta investigación y de la fase piloto descrita en el alcance (Distrito Nacional y Gran Santo Domingo), dicho límite máximo se fija en 35 km, garantizando que las asignaciones evaluadas permanezcan dentro del contexto geográfico delimitado en la sección de Alcance. La expansión a radios mayores (p. ej. 75 km) queda documentada como un parámetro habilitado para fases futuras de expansión regional, fuera del alcance de validación de este trabajo de grado.
   RN-11 (Límite de Capacidad del Receptor): El volumen o cantidad de alimentos asignados en un emparejamiento no podrá exceder la capacidad de almacenamiento diario declarada por la organización receptora para la fecha programada de entrega.
   RN-12 (Plazo Máximo de Retiro): La organización receptora dispondrá de un plazo máximo de 48 horas para confirmar y retirar la donación asignada. Transcurrido este tiempo, el sistema liberará el lote y lo retornará automáticamente al pool de inventario disponible.
   RN-13 (No Discriminación Algorítmica): Los criterios de emparejamiento y asignación automatizada excluirán estrictamente cualquier filtro basado en credo, raza, género u orientación política del receptor, en cumplimiento con la Constitución de la República Dominicana.
   RN-14 (Validación de Entrega Efectiva): Una donación se registrará como completada únicamente cuando el receptor confirme la recepción física dentro del sistema, requiriendo opcionalmente la carga de una evidencia fotográfica en la plataforma.
4. Reglas sobre reportes y trazabilidad fiscal
   RN-15 (Conservación de Registros Históricos): Los registros de transacciones y donaciones se mantendrán almacenados en el sistema por un período mínimo de 10 años, cumpliendo con el plazo de prescripción tributaria dictado por la Ley 11-92.
   RN-16 (Generación de Anexo Fiscal): El sistema consolidará y generará de forma automatizada un reporte fiscal mensual detallando las donaciones por cada contribuyente, estructurado bajo los requisitos de la Norma General No. 06-2018 de la DGII.
   RN-17 (Inmutabilidad de Reportes Fiscales): Una vez emitido el cierre fiscal mensual, los datos históricos quedarán bloqueados contra modificaciones directas. Cualquier corrección posterior deberá gestionarse mediante un reporte rectificativo explícito.
5. Reglas sobre seguridad y datos personales
   RN-18 (Consentimiento Informado de Datos): El sistema impedirá el procesamiento de cualquier dato personal sin que el usuario haya otorgado previamente su consentimiento expreso, acatando la Ley No. 172-13 sobre Protección de Datos Personales.
   RN-19 (Atención a Derechos ARCO): El sistema debe proveer los mecanismos para dar respuesta a las solicitudes de acceso, rectificación, cancelación u oposición (ARCO) de los datos de los titulares en un plazo no mayor a 15 días hábiles.
   RN-20 (Control de Acceso Basado en Roles - RBAC): El acceso a los módulos y datos del sistema estará estrictamente restringido según el rol asignado. Los administradores solo podrán visualizar datos personales completos si existe una justificación operativa válida que quede registrada automáticamente en la bitácora del sistema.

Profundidad
La presente investigación aborda el problema de la gestión de donaciones de alimentos desde una perspectiva técnica, legal y logística, garantizando un nivel de detalle que trasciende la implementación funcional. La profundidad del estudio se manifiesta en los siguientes niveles:
Nivel Arquitectónico y de Ingeniería: El proyecto no se limita al desarrollo de interfaces, sino que profundiza en el diseño de una arquitectura de software escalable. Esto implica un análisis riguroso de la estructura de base de datos para manejar relaciones complejas entre donantes, receptores y centros de acopio, asegurando la integridad referencial y la optimización de consultas para el manejo de inventarios en tiempo real.
Rigurosidad Metodológica en Logística: Se realiza un estudio exhaustivo del método FEFO (First Expired, First Out) para su traducción a lógica de programación. Esto incluye la definición de variables críticas como el tiempo de vida útil residual, el índice de perecederidad y las condiciones de almacenamiento, permitiendo que el sistema tome decisiones automatizadas sobre la prioridad de salida de los productos.
Análisis del Marco Normativo y Tributario: La investigación profundiza en la Ley No. 589-16 y el Código Tributario Dominicano, analizando los requisitos técnicos específicos de la DGII para la trazabilidad de donaciones. El sistema se profundiza al integrar estas normativas en la lógica de generación de reportes, transformando artículos legales en campos de datos y formatos de informes auditables.
Implementación de Algoritmos de Optimización: Se aborda con profundidad el problema de la distribución mediante algoritmos de geolocalización y emparejamiento (matching). El estudio analiza variables de distancia euclidiana y capacidad de recepción para minimizar el tiempo de transporte, asegurando que la asignación de alimentos sea eficiente y no solo aleatoria.
Seguridad y Tratamiento de Datos: Se aplica un nivel de detalle estricto en la protección de la información, implementando protocolos de cifrado y gestión de accesos basados en roles (RBAC). Esto garantiza que los datos sensibles de los beneficiarios y el volumen de excedentes de los donantes se manejen bajo estándares de confidencialidad y ética profesional.
A través de estos niveles de análisis, el trabajo de grado asegura una solución técnica robusta, fundamentada en principios de ingeniería de software y alineada con la realidad socioeconómica de la República Dominicana.

Alcance del proyecto
El presente proyecto se enfocará en el diseño y desarrollo de un sistema web de gestión de donaciones de alimentos, orientado exclusivamente a la organización, control y trazabilidad de excedentes alimentarios en la República Dominicana. La plataforma permitirá registrar y organizar la información de donantes, receptores y bancos de alimentos, gestionar inventarios bajo el método FEFO (First Expired, First Out), y facilitar la asignación de donaciones mediante reglas de disponibilidad, ubicación y tipo de producto.
El desarrollo se limitará a la construcción de un prototipo funcional de la aplicación web, asegurando seguridad, accesibilidad y transparencia en la información, sin abarcar áreas complementarias o externas que excedan los objetivos de la investigación.
Funcionalidades Incluidas
Módulo de Registro y Autenticación: Creación de cuentas para donantes y receptores, acceso mediante credenciales seguras y recuperación de contraseñas.
Gestión de Inventario: Registro de excedentes alimentarios, clasificación por tipo y nivel de perecederidad, aplicación del método FEFO.
Emparejamiento Automático: Asignación de donaciones según disponibilidad, ubicación y tipo de alimento, optimizando la distribución.
Reportes Automáticos: Generación de informes sobre donaciones, inventario y distribución, útiles para transparencia y beneficios fiscales.
Seguridad y Control de Acceso: Implementación de credenciales y niveles de autorización para proteger la información registrada.
Límites y Exclusiones
Logística Física: El sistema no incluye transporte, provisión de vehículos ni cadena de frío para traslado de alimentos.
Procesos Financieros: No se gestionarán transacciones monetarias, cobros ni ventas; el alcance se limita a donaciones en especie.
Integraciones Externas: El sistema funcionará de manera independiente, sin conexión automática con ERPs o sistemas contables externos.
Predicción de Demanda: Se excluye explícitamente del alcance funcional del prototipo actual la implementación de algoritmos de predicción de demanda basados en series temporales (tales como SARIMA, LSTM o Random Forest). La revisión de estos modelos en el cuerpo de la investigación posee un carácter estrictamente analítico y prospectivo, sirviendo como fundamento conceptual para la escalabilidad de la arquitectura en fases comerciales posteriores. En consecuencia, el sistema web desarrollado limita su motor de emparejamiento a reglas lógicas deterministas en tiempo real, por lo que ningún objetivo específico, indicador de desempeño (KPI) o protocolo de validación técnica de la presente tesis medirá la precisión de modelos estocásticos predictivos

 Módulo de Registro y Autenticación (Objetivo Específico 1 — OE1)
Este módulo gestiona el ciclo de vida de las cuentas de usuario y el control de acceso seguro a la plataforma.
RF-01 (Registro y Tipificación de Donantes) — Prioridad: Alta (Must): El sistema debe permitir el registro de perfiles aportantes clasificándolos en dos categorías operativas: (a) Donante Formalizado, capturando obligatoriamente RNC, Razón Social y datos de contacto para la emisión de créditos fiscales, y (b) Donante Especial/Agrícola, requiriendo únicamente Cédula de Identidad y Electoral o pasaporte. Para ambas tipologías es mandatorio capturar correo electrónico, contraseña cifrada, dirección física y las coordenadas exactas de geolocalización para la optimización de las rutas de recolección.
RF-02 (Registro de organizaciones receptoras) — Prioridad: Alta (Must): El sistema debe registrar fundaciones, comedores y ONG capturando sus credenciales legales (RNC y registro ante la Procuraduría o entidad equivalente), capacidad de almacenamiento físico y tipo de población atendida.
RF-03 (Registro de bancos de alimentos) — Prioridad: Alta (Must): El sistema debe registrar bancos de alimentos en su rol de entidades intermediarias, capturando la ubicación de sus sedes, capacidad de almacenamiento refrigerado y horarios de operación.
RF-04 (Autenticación segura) — Prioridad: Alta (Must): Mecanismo de inicio de sesión protegido que autentica a los usuarios mediante correo y contraseña, generando un JSON Web Token (JWT) firmado con expiración configurable y aplicando hashing bcrypt de coste ≥ 12  para las contraseñas.
RF-05 (Recuperación de contraseña) — Prioridad: Media (Should): El sistema debe permitir el envío de un enlace temporal de restablecimiento de credenciales por correo electrónico, con una expiración estricta de 15 minutos.
RF-06 (Verificación de cuenta por correo) — Prioridad: Alta (Must): Bloqueo preventivo que obliga al usuario a validar su dirección de correo electrónico mediante un enlace de confirmación antes de autorizar cualquier operación de donación o solicitud dentro de la plataforma.
RF-07 (Edición de perfil) — Prioridad: Media (Should): Interfaz para que el usuario autenticado actualice de forma autónoma sus datos de contacto, dirección física y geolocalización.
RF-08 (Desactivación de cuenta) — Prioridad: Media (Should): Permitir la baja lógica de una cuenta de usuario, impidiendo su uso en la plataforma pero conservando intacto su historial de transacciones para fines de auditoría fiscal conforme a la Ley 11-92.
16.2.2. Módulo de Inventario y Gestión FEFO (Objetivo Específico 2 — OE2)
Este módulo regula el ingreso, clasificación, control de caducidad y flujo logístico de los lotes de alimentos.
RF-09 (Registro de donación) — Prioridad: Alta (Must): Interfaz para que el donante declare un lote de alimentos especificando: nombre del producto, categoría, cantidad, unidad de medida, fecha de vencimiento, código de lote del fabricante y condiciones de almacenamiento requeridas.
RF-10 (Clasificación por categoría de perecibilidad) — Prioridad: Alta (Must): El backend debe categorizar de forma automática cada producto ingresado en una de las cuatro categorías del sistema: no perecedero, semi-perecedero, perecedero o congelado.
RF-11 (Cálculo de la ventana de donación) — Prioridad: Alta (Must): Algoritmo en tiempo real que calcula los días de vida útil remanente utilizando la fórmula ventana = fecha_vencimiento − fecha_actual y valida si cumple con el umbral mínimo de aceptación de la categoría.
RF-12 (Ordenamiento FEFO) — Prioridad: Alta (Must): La vista del inventario general debe ordenarse jerárquicamente por fecha de vencimiento de forma ascendente, priorizando visiblemente la salida de los lotes más próximos a caducar.
RF-13 (Alertas de próximo vencimiento) — Prioridad: Alta (Must): El sistema debe disparar notificaciones automatizadas en la plataforma y por correo cuando un lote disponible se encuentre a 3 días o menos de expirar.
RF-14 (Rechazo automático de productos vencidos) — Prioridad: Alta (Must): Restricción lógica inquebrantable en el backend que bloquea el registro, visualización o asignación de cualquier producto alimenticio cuya ventana de donación sea menor o igual a cero (ventana ≤ 0).
RF-15 (Ajuste manual de inventario) — Prioridad: Media (Should): Funcionalidad exclusiva para el rol de banco de alimentos que permite registrar mermas, devoluciones o correcciones de inventario, exigiendo de forma obligatoria la selección o redacción del motivo del ajuste.
RF-16 (Histórico de movimientos) — Prioridad: Alta (Must): Repositorio inmutable que registra en una bitácora de base de datos cada entrada, salida, asignación y ajuste manual sufrido por un lote de alimentos para garantizar auditorías completas.
16.2.3. Módulo de Emparejamiento Inteligente (Objetivo Específico 3 — OE3)
Este módulo automatiza y optimiza la asignación de alimentos uniendo la oferta de excedentes con las necesidades de los receptores.
RF-17 (Búsqueda de receptores compatibles) — Prioridad: Alta (Must): El sistema debe identificar mediante funciones de proximidad geoespacial de PostGIS qué organizaciones receptoras tienen necesidades que coincidan con la categoría y volumen del lote disponible, delimitado dentro de un radio geográfico en kilómetros configurable por el administrador.
RF-18 (Generación de Justificación y Narrativa Asistida por IA) — Prioridad: Alta (Must): Interfaz asíncrona con la API de Google Gemini. Una vez que el backend del sistema (vía SQL y PostGIS) calcula y ordena los candidatos óptimos de forma determinista, los datos estructurados se envían al modelo de lenguaje junto con un prompt de temperatura cero (0.0). El modelo procesará la información exclusivamente para redactar una justificación analítica en lenguaje natural legible para el administrador, explicando la viabilidad del emparejamiento precalculado sin capacidad de alterar los resultados del algoritmo relacional.
RF-19 (Confirmación manual del emparejamiento) — Prioridad: Alta (Must): Flujo de seguridad que requiere que un administrador humano o el banco de alimentos valide y confirme la sugerencia de la Inteligencia Artificial antes de consolidar la asignación final.
RF-20 (Reasignación) — Prioridad: Media (Should): Permitir liberar un lote de alimentos y reintroducirlo en el motor de emparejamiento si la organización receptora original rechaza la asignación o no la retira dentro del plazo límite establecido.
RF-21 (Notificación a las partes) — Prioridad: Alta (Must): Emisión inmediata de alertas push en la plataforma y correos electrónicos masivos dirigidos tanto al donante como al receptor en el instante exacto en que se confirma el emparejamiento.
RF-22 (Registro de retroalimentación) — Prioridad: Baja (Could): Formulario opcional que permite a los donantes y receptores calificar la experiencia de la transacción logística en una escala del 1 al 5 y añadir comentarios cualitativos.
16.2.4. Módulo de Reportería (Objetivo Específico 4 — OE4)
Este módulo se encarga del procesamiento de datos para la transparencia, rendición de cuentas e incentivos fiscales.
RF-23 (Reporte de donaciones por período) — Prioridad: Alta (Must): Motor de búsqueda avanzada que genera reportes estructurados filtrando la información por rangos de fechas, identidad del donante, categoría de alimento y estado actual de la transacción.
RF-24 (Reporte de inventario actual) — Prioridad: Alta (Must): Pantalla de descarga de datos que exporta el estado del inventario global en tiempo real, estructurado bajo el estricto orden cronológico del principio FEFO.
RF-25 (Reporte de asignaciones completadas) — Prioridad: Alta (Must): Generador de reportes consolidación que lista todos los emparejamientos entregados con éxito, vinculados directamente a su correspondiente evidencia digital o fotografía de recepción.
RF-26 (Exportación a Google Sheets) — Prioridad: Alta (Must): Integración asíncrona mediante Google Sheets API v4 para inyectar y publicar de forma automatizada los reportes del sistema en hojas de cálculo compartidas de la organización.
RF-27 (Reporte fiscal DGII) — Prioridad: Alta (Must): Módulo de exportación documental que genera reportes inmutables en formato PDF firmados digitalmente. Este documento debe capturar de forma mandatoria las variables contables exigidas por la Norma General No. 04-2014 de la DGII, operando como soporte legal transparente y auditable para la deducibilidad de los gastos sociales y de responsabilidad social corporativa de los donantes empresariales, de estricta conformidad con el Artículo 287 del Código Tributario de la República Dominicana (Ley 11-92).
16.2.5. Módulo de Seguridad y Administración (Objetivo Específico 5 — OE5)
Este módulo vela por la integridad del software, la protección de la información y el control operativo general.
RF-28 (Gestión de roles - RBAC) — Prioridad: Alta (Must): Control de acceso basado en roles jerárquicos (Donante, Receptor, Banco de Alimentos, Administrador) que restringe los endpoints de la API y las vistas del frontend según los privilegios autorizados.
RF-29 (Auditoría de acciones) — Prioridad: Alta (Must): Registro obligatorio y automatizado en la bitácora del sistema de las variables de identidad (quién), operación ejecutada (qué), timestamp (cuándo) e dirección IP (desde dónde) para todas las transacciones críticas de datos.
RF-30 (Bloqueo por intentos fallidos) — Prioridad: Alta (Must): Sistema de protección perimetral contra fuerza bruta que bloquea temporalmente el acceso a una cuenta de usuario si se registran 5 intentos fallidos consecutivos de contraseña en un lapso de 10 minutos.
RF-31 (Gestión de consentimiento de datos) — Prioridad: Alta (Must): Formulario legal vinculante de aceptación de términos que solicita, valida y almacena el consentimiento explícito del usuario conforme a los mandatos de la Ley 172-13 sobre Protección de Datos Personales antes de guardar su información en la base de datos.
RF-32 (Panel Administrativo de Control Técnico) — Prioridad: Media (Should): Interfaz gráfica parametrizada (Dashboard) que consolida indicadores clave descriptivos del rendimiento del sistema para el administrador del banco de alimentos. El panel desplegará en tiempo real: (a) el volumen total de alimentos rescatados expresado en kilogramos, (b) la tasa de efectividad operativa en los emparejamientos confirmados antes de su expiración, y (c) la distribución de lotes según la categoría de perecibilidad (FEFO), garantizando un monitoreo directo y auditable de los flujos de datos procesados durante la fase piloto.

16.3 Requerimientos no  funcionales.
16.3.1. Marco de calidad
Los requerimientos no funcionales se estructuran bajo el modelo de calidad de la norma ISO/IEC 25010:2011. Esta norma define ocho características esenciales para el sistema web: adecuación funcional, eficiencia de desempeño, compatibilidad, usabilidad, fiabilidad, seguridad, mantenibilidad y portabilidad. Cada requerimiento se acompaña de una métrica que se puede verificar en base a las recomendaciones metodológicas de Sommerville, Pressman y Maxim).
16.3.2. Eficiencia de desempeño
RNF-01 (Tiempo de respuesta de consultas): El 95 % de las peticiones de lectura (GET) deberá responder en un tiempo ≤ 1.5 segundos. Esto se medirá bajo una carga nominal de hasta 100 usuarios concurrentes mediante pruebas con k6 o JMeter.
RNF-02 (Tiempo de registro de donación): La operación de registro de un nuevo lote de alimentos deberá completarse en un tiempo ≤ 2 segundos de extremo a extremo (end-to-end).
RNF-03 (Capacidad de inventario): El sistema debe ser capaz de soportar al menos 500,000 lotes activos en la base de datos. No se admitirá una degradación superior al 10 % al realizar las consultas de ordenamiento FEFO
RNF-04 (Manejo de Tiempos de Espera e Interfaz Asíncrona con la IA): Debido a la naturaleza variable en los tiempos de respuesta de la API externa de Google Gemini, el backend del sistema implementará un patrón de arquitectura asíncrona mediante un indicador de carga (loading state) en el frontend, con un tiempo de espera de corte (Gateway Timeout) fijado en \(\le 12\) segundos. El motor de reglas deterministas (SQL) se ejecutará de forma inmediata e independiente en segundo plano, asegurando que la disponibilidad de los datos centrales del inventario no quede supeditada a las latencias de la capa semántica generativa..
RNF-05 (Generación de reportes): El sistema debe permitir la exportación de reportes de hasta 10,000 filas hacia la API de Google Sheets en un tiempo ≤ 10 segundos.
16.3.3. Fiabilidad y disponibilidad
RNF-06 (Disponibilidad): La plataforma garantizará una disponibilidad mensual ≥ 99.5 %. Esto equivale a un máximo de 3.6 horas de inactividad al mes, excluyendo los mantenimientos programados.
RNF-07 (Recuperación ante fallos): Se establece un Objetivo de Tiempo de Recuperación RTO ≤ 4 horas y un Objetivo de Punto de Recuperación RPO ≤ 24 horas. Se ejecutarán respaldos automáticos diarios y cifrados de la base de datos.
16.3.4. Usabilidad
RNF-08 (Curva de aprendizaje): Un usuario nuevo debe ser capaz de registrar su primera donación en un tiempo ≤ 5 minutes sin asistencia externa . Se validará con una puntuación de la Escala de Usabilidad del Sistema (SUS) ≥ 70.
RNF-09 (Accesibilidad): El diseño de la interfaz web debe cumplir con el nivel WCAG 2.1 AA en al menos el 90 % de las pantallas auditadas con la herramienta axe-core.
RNF-10 (Internacionalización): La interfaz estará disponible en idioma español de forma predeterminada . El código quedará estructurado y preparado para soportar el idioma inglés en el futuro a través de librerías de i18n.
16.3.5. Seguridad
RNF-11 (Cifrado en tránsito): Todo el tráfico de red se transmitirá de forma cifrada mediante el protocolo TLS 1.2 o superior. Se exigirá una calificación A en las auditorías de SSL Labs.
RNF-12 (Cifrado en Reposo y Mecanismos de Hash): Con el fin de salvaguardar la información confidencial conforme a las pautas de OWASP y la Ley No. 172-13, las credenciales de acceso (contraseñas) se procesarán irreversiblemente mediante el algoritmo de hashing unidireccional bcrypt (con un factor de coste Mayor o igual a 12). Por su parte, los datos de identidad civil y fiscal (RNC y cédulas) se almacenarán en texto claro pero protegidos mediante políticas estrictas de control de acceso a nivel de base de datos (RBAC) y cifrado de disco completo provisto por la infraestructura del servidor de base de datos (Transparent Data Encryption), garantizando la capacidad de búsqueda indexada y rendimiento en las consultas del sistema..
RNF-13 (Cumplimiento OWASP Top 10): El software debe registrar cero vulnerabilidades de severidad alta o crítica en los escaneos con OWASP ZAP previos a cada liberación de versión.
RNF-14 (Protección de datos personales): Cumplimiento estricto de la Ley No. 172-13 de la República Dominicana. El sistema incluirá el registro explícito del consentimiento del usuario, así como los mecanismos para ejercer el derecho de acceso y supresión de datos (Requerimie... p. 3).
RNF-15 (Política de contraseñas): Las llaves de acceso exigirían un mínimo de 10 caracteres, incluyendo una letra mayúscula, un número y un símbolo. Se aplicará un bloqueo de cuenta tras registrar 5 intentos fallidos.
16.3.6. Mantenibilidad
RNF-16 (Cobertura de pruebas): Se exige una cobertura de pruebas unitarias ≥ 80 % y de pruebas de integración ≥ 60 %. Ambas métricas serán validadas mediante Jest o Vitest (Requerimie... p. 4).
RNF-17 (Modularidad): El código se organizará por dominios (DDD ligero) para asegurar un bajo acoplamiento. La deuda técnica se monitoreará con SonarQube, exigiendo una calificación de categoría A 
16.3.7. Portabilidad
RNF-18 (Compatibilidad multinavegador): El sistema garantizará una funcionalidad completa en las dos últimas versiones mayores de Google Chrome, Microsoft Edge, Mozilla Firefox y Apple Safari. La interfaz contará con un diseño adaptativo (responsive) a partir de los 360 píxeles de ancho 






Lenguaje 语言：
Frontend 前端：React/Javascrip
Backend 后端：Python+Fast API
Base de datos 数据库：PostgreSQL

Color Primcipal: Verde
Color Secundario: Amarillo o naranja
Fondo y base: Blanco y Gris
Detalle Control: Azul Oscuro

Por favor tener en cuenta e incluir los lineamientos de trabajo de grado de diseño y desarrollo, que apliquen a tu propuesta (consultar con el Asesor):
Descripción y diagramas de arquitectura
Diagrama de Secuencia
Prototipo o flujo de navegación
Modelos de Dominio
Diagrama de componentes o despliegues
Diagrama de entidad relación
Pruebas unitarias y de componentes.
Pruebas de sistemas
Diccionario de datos o estructura de datos.
Matriz de casos de prueba (escenarios, prueba unitaria, TDD)
Pantallas (UX/UI)
Estrategia de seguridad (Control de roles y perfiles. Prevención de intrusos o ciberataques. Encriptación y enmascaramiento de datos)
Reportes e informes de salida.
Diagrama de clases
Criterios de vulnerabilidad
Performance
Alta disponibilidad (Resiliencia, contingencia, disaster recovery, evolución y mantenimiento)
Patrones de diseño

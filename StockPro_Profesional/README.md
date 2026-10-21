# StockPro Small Business — consolidación v1.1

## Propósito
Versión inicial enfocada en pequeños negocios, con operación local-first. Es un prototipo web funcional para validar procesos; **no es una APK Android final ni está certificado para producción**.

## Incluido en esta consolidación
- Productos, ventas, compras y proveedores básicos.
- Indicadores de ventas, ganancia bruta, valor del inventario y stock bajo.
- Registro de costo y precio históricos en las ventas.
- Costo promedio ponderado al registrar compras (prototipo; no sustituye una contabilidad certificada).
- Bloqueo del cambio de moneda una vez que existen registros, para reducir el riesgo de mezclar USD y CUP.
- Protección contra eliminación de ventas/compras y productos con historial.
- Copias de seguridad cifradas con AES-256-GCM y derivación PBKDF2-SHA256 (310.000 iteraciones); exige contraseña de al menos 12 caracteres.
- Importación con confirmación antes de reemplazar los datos y soporte para restaurar copias cifradas.
- Registro local de auditoría para creación de productos, ventas, compras y proveedores (máximo 2.000 eventos).
- Validación de campos numéricos y prevención de SKU duplicados.
- Idioma español/inglés parcialmente disponible.
- Fecha local para registros y gráfica semanal.

## Cómo probar
Abre `app/index.html` en un navegador moderno. Los datos se guardan en `localStorage` del navegador/perfil. Exporta una copia cifrada desde la configuración y guarda la contraseña aparte. Usa HTTPS o localhost para que Web Crypto esté disponible en el navegador.

## Limitaciones conocidas
- La moneda elegida aplica al negocio completo; no hay multimoneda por transacción ni conversión de tasas.
- La validación de importación es básica; no sustituye pruebas de recuperación exhaustivas. Las copias exportadas se cifran, pero los datos activos de localStorage siguen sin cifrar.
- `localStorage` no es una base de datos nativa cifrada y puede perderse al limpiar datos del navegador.
- Aún no hay devoluciones/ajustes de inventario; por eso no se permite borrar movimientos históricos.
- No incluye POS completo, facturación fiscal, impuestos por país, lotes/vencimientos, sucursales, sincronización, predicciones IA ni aplicación Android nativa.
- El backend/panel/licencias de otros prototipos no están conectados a esta interfaz.
- No se ha compilado una APK, desplegado un servidor ni realizado una auditoría de seguridad.

## Siguiente trabajo
1. Migrar procesos críticos a Kotlin/Jetpack Compose y Room (SQLite) con cifrado mediante clave protegida por Android Keystore.
2. Añadir pruebas unitarias para movimientos de stock, costo histórico y restauración.
3. Implementar devoluciones y ajustes auditados.
4. Prueba automatizada de cifrado/restauración, corrupción de archivos y recuperación completa.
5. Licencias offline firmadas integradas con Android.
6. Pruebas de instalación/actualización en dispositivos físicos.

## Seguridad local (v1.3)
- Los registros operativos permanecen en el dispositivo/navegador; no se sincronizan con un servidor en esta versión.
- Las copias exportadas pueden cifrarse con AES-256-GCM y una clave derivada por PBKDF2-SHA256.
- La restauración limita el tamaño del archivo a 20 MiB y valida el sobre cifrado, identificadores, SKU duplicados, cantidades y valores numéricos antes de reemplazar los datos.
- Los identificadores nuevos usan `crypto.randomUUID()` cuando está disponible, con alternativa basada en `crypto.getRandomValues()`.
- La auditoría actual también es local y no es resistente a manipulación por alguien con acceso al dispositivo o al almacenamiento del navegador.
- `localStorage` no está cifrado en reposo. Para proteger el dispositivo se recomienda bloqueo de pantalla, cifrado del dispositivo y no compartir el perfil del navegador. La siguiente etapa debe migrar a Android nativo con Room/SQLite y claves protegidas por Android Keystore.
- No es una auditoría de seguridad ni una APK de producción; los cambios pasan comprobaciones estáticas/sintácticas, pero requieren pruebas funcionales en navegador y Android.

## Licencias locales (mejora v1.4)
- El emisor de licencias offline ahora cifra la clave privada Ed25519 en disco con contraseña; no sobrescribe claves existentes.
- Emisión validada por cliente, ID de dispositivo, duración y precio USD; evita sobrescribir una licencia de salida sin `--force`.
- Se incluye guía para entregar el archivo de licencia firmado por email/WhatsApp sin enviar la clave privada.
- Importante: el emisor es una herramienta de propietario separada. **La activación todavía no está integrada en la app web ni en una APK**, y la prueba de 30 días no se puede hacer resistente a manipulación en una app web completamente offline. Ver `offline_licenses/LICENCIAS_Y_ACTIVACION.md`.

## Consolidación v1.5 — análisis y ajustes de inventario
- Añadido módulo de ajustes de stock: entrada, salida y fijación de conteo físico; exige motivo, impide cantidades fraccionarias/negativas y guarda valores antes/después en el historial local.
- Los ajustes se incluyen en los datos exportados y se validan al restaurar copias.
- Añadido `ANALISIS_INTEGRAL_Y_PLAN.md` con riesgos priorizados, criterios de aceptación por módulo y estado real de pruebas.
- Pruebas estáticas: `python -m pytest -q tests/test_stockpro_static.py`; sintaxis JS comprobada con `node --check`.
- Estas verificaciones no sustituyen pruebas E2E, recuperación real, auditoría de seguridad ni pruebas Android. Sigue siendo un prototipo web; no es APK final.

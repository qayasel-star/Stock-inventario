# StockPro — análisis integral y plan de desarrollo por módulos

**Estado del paquete:** prototipo web local, no APK Android final. Esta revisión incluye cambios en el módulo de ajustes de inventario y verificaciones estáticas. No equivale a una auditoría de seguridad ni a pruebas de usuario en Android.

## Resumen ejecutivo

StockPro ya contiene un flujo básico de productos, ventas, compras, proveedores, indicadores, exportación CSV y copias cifradas desde el navegador. Los datos operativos se guardan en `localStorage`; esto facilita la prueba sin Internet, pero no ofrece cifrado de datos en reposo, transacciones ACID, aislamiento entre usuarios ni recuperación automática. El emisor de licencias offline existe como utilidad Python separada, pero no está integrado en esta interfaz. La prioridad es consolidar integridad de inventario, trazabilidad, recuperación y licencia antes de declarar producción.

## Hallazgos priorizados

| Prioridad | Hallazgo / riesgo | Estado | Acción requerida |
|---|---|---|---|
| P0 | Datos activos en `localStorage`, sin cifrado en reposo y vulnerables a borrado del perfil | Abierto | App Android con Room/SQLite y claves protegidas por Android Keystore; definir recuperación y migración |
| P0 | Licencias offline separadas de la app; sin verificador integrado probado de extremo a extremo | Abierto | Integrar Ed25519, vinculación a dispositivo y manejo de expiración; probar licencia alterada, vencida y de otro dispositivo |
| P0 | Sin pruebas automatizadas de flujos reales de venta/compra/restauración en navegador o Android | Abierto | Añadir pruebas funcionales y de recuperación, después pruebas en dispositivo físico |
| P1 | No existía ajuste de inventario trazable | Mejorado en esta entrega | Nuevo módulo de ajustes con motivo, cantidad anterior/cambio/nueva y auditoría; aún requiere pruebas interactivas |
| P1 | No hay devoluciones de ventas ni reversión vinculada al movimiento original | Abierto | Diseñar devolución parcial/total idempotente, límites por cantidad devuelta y reposición configurable |
| P1 | No hay lote, vencimiento, ubicación/sucursal ni trazabilidad por lote | Abierto | Definir alcance de pequeños negocios y añadir lote/vencimiento cuando el caso lo requiera |
| P1 | El coste medio ponderado se actualiza al comprar, pero no existe libro contable formal | Parcial | Mantener `costAtSale` por venta y diseñar libro inmutable de movimientos de stock/costo |
| P1 | La moneda es global; no hay conversión ni tipo de cambio por operación | Limitación conocida | Mantener bloqueo de moneda y mostrar claramente que cambiar moneda no convierte datos |
| P1 | Auditoría almacenada localmente y editable por quien controla el navegador | Limitación conocida | En versión nativa, proteger almacenamiento; registrar actor, fecha y referencia del movimiento |
| P2 | Informes limitados; no son contabilidad fiscal ni previsión | Parcial | Añadir filtros por fechas, margen, ventas por producto y exportación; validar con datos de prueba |
| P2 | Idioma parcialmente traducido | Parcial | Completar catálogo de traducciones y probar todas las pantallas en ES/EN |
| P2 | Diseño responsive de navegador no sustituye pruebas de accesibilidad/usabilidad móvil | Parcial | Pruebas en pantallas pequeñas, navegación por teclado, etiquetas y mensajes de error |

## Módulos y criterios de aceptación

### 1. Productos e inventario
- SKU único sin distinguir mayúsculas/minúsculas; precio/costo no negativos; stock y mínimo enteros no negativos.
- Venta nunca permite stock negativo.
- Ajuste requiere motivo, conserva cantidades antes/después y deja auditoría.
- No eliminar productos con historial.
- **Pendiente:** pruebas de borde en interfaz y persistencia; impedir cambios de identificadores al restaurar.

### 2. Ventas
- Guardar precio y coste al momento de venta, total y ganancia redondeados a centavos.
- Rechazar cantidades cero, fraccionarias o superiores al stock.
- No permitir borrar ventas históricas.
- **Pendiente:** devoluciones parciales/totales y prevención de doble envío.

### 3. Compras
- Registrar coste unitario, cantidad, total y coste previo.
- Recalcular coste promedio ponderado; prueba ejemplo: 10 unidades a 2 + 10 a 4 = coste medio 3.
- **Pendiente:** proveedor asociado a cada compra, gastos adicionales y validación transaccional.

### 4. Proveedores
- Nombre obligatorio y campos de contacto/notas escapados al mostrar.
- **Pendiente:** vincular compras a proveedor, búsqueda y control de duplicados.

### 5. Ajustes y movimientos
- Tipos: entrada, salida y fijar cantidad física.
- Nunca permitir resultado negativo, cantidades fraccionarias o cambios sin motivo.
- Guardar historial sin borrar movimientos anteriores.
- **Nuevo en esta entrega:** interfaz y registro local de ajustes; falta una prueba E2E en navegador.

### 6. Análisis e informes
- Calcular ingresos, ganancia bruta, margen, unidades y valor del inventario desde los registros.
- Identificar que ganancia bruta no descuenta gastos ni impuestos.
- **Pendiente:** reconciliar informes contra escenarios de referencia y soportar filtros por período de manera consistente.

### 7. Copias y recuperación
- Cifrado de copia con AES-GCM, clave derivada PBKDF2, sal e IV aleatorios; contraseña de al menos 12 caracteres.
- Rechazar contraseña incorrecta, datos alterados, formato no válido, archivo >20 MB y entidades inconsistentes sin sustituir datos actuales.
- **Pendiente crítico:** pruebas de ida y vuelta, contraseña incorrecta, archivo truncado, manipulado y recuperación de una copia real. El cifrado de la copia no cifra el almacenamiento activo.

### 8. Licencias
- Emisión por el propietario; clave privada cifrada; clave pública en la aplicación; firma Ed25519.
- Verificar firma, expiración y dispositivo localmente sin Internet.
- **Pendiente crítico:** integrar emisor/verificador y prueba de 30 días en Android; pruebas de licencias falsificadas, alteradas, vencidas y de otro dispositivo. Revocación inmediata no es posible en un dispositivo desconectado sin recibir una actualización firmada.

### 9. Android y funcionamiento sin conexión
- **Pendiente:** empaquetado nativo, Room/SQLite, Android Keystore, migración segura, instalación/actualización, permisos y pruebas en dispositivos reales. La PWA actual no es una APK.

## Registro de verificaciones realizadas en esta entrega

- `node --check` sobre el JavaScript extraído de `app/index.html`: **correcto**.
- `python -m py_compile` sobre el emisor de licencias y servidor: **correcto**.
- Se añadió el módulo de ajustes y la validación estructural de movimientos al restaurar una copia.
- No se ha ejecutado una prueba interactiva de navegador, Android, cifrado/restauración end-to-end ni auditoría de seguridad. No deben considerarse aprobados todavía.

## Secuencia de trabajo recomendada

1. Pruebas automatizadas de cálculos y de copia/restauración, con rechazo sin modificar datos ante cualquier fallo.
2. Devoluciones y libro único de movimientos de stock, evitando editar el historial.
3. Proveedores enlazados a compras, informes reconciliados y validaciones de importación completas.
4. Migración de la interfaz a aplicación Android con Room y Android Keystore.
5. Integración y pruebas de licencias offline Ed25519 en la app.
6. Pruebas de instalación, actualización, pérdida de almacenamiento, recuperación y operación prolongada sin Internet.

**Criterio de salida:** cada módulo se marca como terminado solo después de cumplir sus criterios, superar pruebas funcionales y de recuperación y documentar los riesgos residuales.

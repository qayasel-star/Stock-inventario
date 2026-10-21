# StockPro — Especificación funcional y visual v1.0

## Producto y público
Aplicación Android orientada a pequeños negocios, tiendas y distribuidoras. Diseño mobile-first, idioma español/inglés, arquitectura local-first y servicios de nube opcionales.

## Principios de producto
- Trabajar sin conexión para operaciones diarias.
- Mantener trazabilidad: movimientos no deberían borrarse silenciosamente en producción; usar anulaciones auditadas.
- No confundir moneda de visualización con conversión monetaria.
- Proteger datos mediante mínimo privilegio, cifrado y copias restaurables.
- Distinguir funciones implementadas, prototipos y capacidades futuras.

## Módulos y alcance
1. **Inicio/dashboard:** valor del inventario a costo, ingresos, ganancia bruta, stock bajo, ventas recientes y alertas.
2. **Productos/inventario:** SKU, nombre, costo, precio, cantidad y umbral mínimo. Futuro: lotes, vencimiento, variantes, fotos, seriales, códigos de barras, inventarios físicos.
3. **Ventas/POS:** registrar líneas, descontar stock y calcular ganancia bruta. Futuro: carrito multi-producto, descuentos, impuestos, devoluciones, caja, recibos, medios de pago y venta offline con cola de sincronización.
4. **Compras:** registrar recepción, costo y cantidad. Futuro: órdenes, recepciones parciales, gastos importación y comparación de proveedores.
5. **Proveedores:** contacto y notas. Futuro: términos de pago, documentos, rendimiento y cuentas por pagar.
6. **Análisis:** ingresos, ganancia bruta, margen, unidades, productos más vendidos y tendencia de siete días. Futuro: predicción basada en histórico suficiente, estacionalidad, sugerencia de reposición y detección de anomalías.
7. **Multimoneda:** USD/CUP inicialmente. El prototipo solo cambia el formato mostrado; no convierte importes. Producción debe guardar moneda por operación, tasa y fecha, y usar tasas históricas para informes consolidados.
8. **Idiomas:** español e inglés; traducir todos los textos, errores, fechas y formatos regionales antes de release.
9. **Seguridad y licencias:** licencias offline firmadas, clave privada fuera de la app, clave pública embebida. Revocación inmediata requiere conectividad; offline no garantiza revocación inmediata.
10. **Copias:** exportación/importación JSON en el prototipo. Producción debe cifrar con clave derivada de contraseña robusta o clave aleatoria custodiada por el usuario, validar integridad, versionar formato y probar restauración.
11. **Nube opcional:** sincronización cifrada con resolución explícita de conflictos, backups remotos opt-in y administración de licencias si se habilita. No desplegada.

## Especificación visual
- Paleta: fondo verde-negro (#071b18), panel verde profundo (#0d2923), acento lima (#c8f169), verde positivo (#40d99b), ámbar para advertencias y rojo para errores.
- Tipografía: system sans-serif, encabezados compactos y cifras de KPI con peso alto.
- Navegación: barra lateral en escritorio, barra inferior en móvil; acciones primarias visibles.
- Componentes: tarjetas KPI, tablas responsivas, formularios cortos, estados vacíos, chips de alerta, gráficas con etiquetas.
- Accesibilidad objetivo: contraste WCAG AA, controles táctiles de al menos 44px, foco visible, etiquetas accesibles, no usar solo color para comunicar estado.
- UX: confirmar acciones destructivas, validar cantidades, mostrar mensajes de error claros y ofrecer exportación de respaldo antes de resetear.

## Modelo de datos inicial
- Product: id, name, sku, cost, price, qty, min.
- Sale: id, date, productId, productNameSnapshot, qty, unitPriceSnapshot, unitCostSnapshot, currency, totals, grossProfit.
- Purchase: id, date, productId, productNameSnapshot, qty, unitCost, currency, supplierId.
- Supplier: id, name, contact, notes.
- Producción: añadir tenantId, branchId, createdAt, updatedAt, actorId, schemaVersion, currency, exchangeRateSnapshot, audit events y tombstones para sincronización.

## Fórmulas y límites
- Ingreso bruto de venta = cantidad × precio unitario registrado al momento de venta.
- Ganancia bruta = ingreso neto de descuentos menos costo de mercancía vendida; no incluye gastos operativos ni impuestos salvo que se modelen expresamente.
- Margen bruto = ganancia bruta / ingresos × 100, si ingresos > 0.
- El prototipo actual usa costo actual del producto al registrar la venta y no es contabilidad fiscal; la producción debe guardar snapshots y adoptar un método de costo consistente (p. ej. promedio ponderado o FIFO).
- Pronósticos no deben mostrarse como confiables sin suficiente historial y métricas de error.

## Pruebas de aceptación antes de producción
- Inventario: cantidades nunca negativas; validación de SKU duplicado según configuración; ajustes auditados.
- Venta: rechazar cantidad superior al stock; atomicidad entre venta y movimiento de stock; ganancias con snapshots históricos.
- Compra: stock y costo coherentes; registrar proveedor y gastos cuando aplique.
- Backup: exportar, cifrar, alterar archivo, contraseña incorrecta y restaurar en instalación limpia; detectar corrupción sin sobreescribir datos actuales.
- Offline: reinicio de app, persistencia, cambio de fecha/hora, almacenamiento lleno, permisos y actualización.
- Licencias: firma inválida, licencia alterada, dispositivo incorrecto, vencida, reloj manipulado, actualización y recuperación. Mitigar manipulación de reloj; no prometer resistencia absoluta en dispositivo comprometido.
- Seguridad: OWASP MASVS, secretos fuera del APK, protección de datos, controles de acceso y análisis de dependencias.
- Release: compilar APK release firmada, verificar firma, instalar en Android real y emulador, probar actualización y documentar hashes.

## Estado real de esta entrega
**Implementado en prototipo web local:** UI responsive; navegación; inventario básico; ventas de un producto por registro; compras básicas; proveedores; KPIs; alertas de stock mínimo; gráfico simple de 7 días; cambio de idioma parcial; formato de moneda seleccionable sin conversión; exportación/importación JSON sin cifrado; CSV de ventas.

**Pendiente:** APK Android compilada; persistencia nativa; segundo factor; cifrado robusto de base local y backups; escaneo real de códigos; expiraciones/lotes; caja/facturas fiscales; contabilidad; multimoneda con tasas; inglés completo; IA predictiva; nube/sincronización; licencias firmadas integradas; auditoría de seguridad y pruebas en dispositivo.

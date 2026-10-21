# Licencias StockPro: diseño local-first

## Reglas del producto
- Prueba gratuita prevista: 30 días por instalación/dispositivo.
- El propietario es la única persona autorizada a emitir, renovar o revocar licencias.
- Duración y precio se acuerdan/configuran para cada licencia; el catálogo de referencia se consulta con `python issuer.py plans`.
- La activación debe funcionar sin conexión: el cliente entrega al propietario un código/ID de instalación; el propietario genera un archivo de licencia firmado y lo envía como adjunto por email o WhatsApp. El usuario importa el archivo en la app.
- La aplicación debe verificar la firma Ed25519 con una clave pública integrada, validar el hash del dispositivo, esquema, fechas y estado local. La clave privada jamás se incorpora a la APK ni se envía al cliente.
- El archivo de licencia no contiene secretos de firma. El canal de mensajería sirve para entregar el adjunto, no como prueba de autenticidad: la firma es la que autentica el documento.

## Preparación del emisor
1. Mantén esta carpeta en un equipo controlado por el propietario, preferiblemente sin conexión.
2. Ejecuta `python issuer.py init-keys` y utiliza una contraseña larga y única. La clave privada queda cifrada en disco.
3. Guarda dos copias de recuperación de la clave privada cifrada en ubicaciones seguras separadas. No pierdas la contraseña.
4. `python issuer.py plans` muestra precios de referencia editables en el código. El precio final se indica explícitamente al emitir.
5. Emite con `python issuer.py issue --customer "Negocio" --device-id "ID-DE-INSTALACION" --days 90 --plan Trimestral --price 27 --out licencia.json`.
6. Envía solo `licencia.json` al cliente. Nunca compartas `owner_private_key.pem` ni la contraseña.

## Límites importantes
- El emisor CLI genera licencias firmadas Ed25519, pero **aún no está integrado en la interfaz web ni en una APK Android**. No anunciar activación en la app como disponible hasta integrar y probar importación/verificación en Android.
- Una prueba totalmente offline no puede ser resistente por completo a reinstalaciones, restauración de copias o retroceso del reloj en una app web. Android puede mejorar esto usando almacenamiento protegido por Android Keystore, pero tampoco debe prometerse invulnerabilidad.
- Revocación inmediata requiere que el dispositivo reciba una lista firmada de revocación o se conecte ocasionalmente. Sin conexión, una licencia ya emitida puede seguir siendo válida hasta su vencimiento.
- La firma protege autenticidad e integridad; no cifra el archivo de licencia. No se necesita secreto en el archivo.
- Antes de producción: implementar la misma canonicalización JSON y verificación Ed25519 en Android, fijar la clave pública, comprobar expiración y dispositivo, probar licencias alteradas/expiradas, proteger el ID de instalación, definir política de reactivación y hacer revisión de seguridad.

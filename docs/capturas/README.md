# Índice de Capturas Reales del Laboratorio (`docs/capturas/`)

Este directorio contiene las **10 capturas PNG reales** obtenidas al ejecutar **MiniAuth Lab** en Docker Compose e integradas en el [`README.md`](../../README.md) principal.

## Inventario de capturas verificadas

| Archivo | Sección en `README.md` | Contenido verificado en la captura |
|---|---|---|
| [`01-login.png`](01-login.png) | **6. Paso 3: Conocer MiniAuth** | Navegador en `localhost:5000/login` mostrando la tarjeta **MiniAuth Lab**, campos `Usuario` (`estudiante`) y `Contraseña`, botón **Iniciar sesión** y recuadro de credenciales ficticias. |
| [`02-perfil.png`](02-perfil.png) | **6. Paso 3: Conocer MiniAuth** | Navegador en `localhost:5000/perfil` con la etiqueta **Sesión activa**, el encabezado **`Bienvenido, estudiante`** y el botón **Cerrar sesión**. |
| [`03-zap-inicio.png`](03-zap-inicio.png) | **7.1 Abrir OWASP ZAP** | Interfaz Webswing de **OWASP ZAP 2.16.0** en `localhost:8080/zap/` con la barra de menú superior (`Tools`), el árbol `Sites`, la pestaña `Quick Start` y los paneles inferiores. |
| [`04-zap-peticion.png`](04-zap-peticion.png) | **7.3 Enviar la petición y verificar la respuesta** | Ventana **Manual Request Editor** mostrando a la izquierda (`Request`) la petición `GET http://app:5000/login HTTP/1.1` con `host: app:5000` y el botón `Send`, y a la derecha (`Response`) las cabeceras `HTTP/1.1 200 OK` (`Server: gunicorn`) y el HTML de `MiniAuth Lab — Iniciar sesión`. |
| [`05-zap-alertas.png`](05-zap-alertas.png) | **7.4 Cerrar el editor y consultar las alertas pasivas** | Ventana principal de ZAP con `http://app:5000` → `GET:login` en el panel `Sites` y 4 alertas en la pestaña `Alerts`, incluyendo `Content Security Policy (CSP) Header Not Set` y `Missing Anti-clickjacking Header`. |
| [`06-zap-detalle-csp.png`](06-zap-detalle-csp.png) | **7.4 Cerrar el editor y consultar las alertas pasivas** | Detalle completo de la alerta `Content Security Policy (CSP) Header Not Set` sobre `http://app:5000/login` (`Risk: Medium`, `Confidence: High`, `CWE ID: 693`, `Description` y `Solution`). |
| [`07-cucumber-normal.png`](07-cucumber-normal.png) | **8.1 Ejecutar los dos escenarios normales (`PASS`)** | Terminal mostrando `2 Scenarios (2 passed)`, `8 Steps (8 passed)`, `Tests run: 3, Failures: 0, Errors: 0, Skipped: 1` y `[INFO] BUILD SUCCESS`. |
| [`08-cucumber-fallo.png`](08-cucumber-fallo.png) | **8.2 Ejecutar el escenario de fallo controlado (`FAIL`)** | Terminal mostrando `1 Scenarios (1 failed)`, `Fallo de aserción BDD: Se esperaba encontrar el mensaje ["Acceso denegado"] en la respuesta HTML (ruta /perfil, HTTP 200), pero no estuvo presente.` y `[INFO] BUILD FAILURE`. |
| [`09-gherkin-edicion.png`](09-gherkin-edicion.png) | **8.3 Modificar el escenario Gherkin** | Editor mostrando `cucumber/src/test/resources/features/autenticacion_fallo.feature` con la línea 7 actualizada a `Entonces debe ver el mensaje "Bienvenido, estudiante"`. |
| [`10-cucumber-corregido.png`](10-cucumber-corregido.png) | **8.4 Ejecutar nuevamente el escenario (`PASS`)** | Terminal mostrando la ejecución de `@fallo-controlado` tras la edición: `1 Scenarios (1 passed)`, `3 Steps (3 passed)` y `[INFO] BUILD SUCCESS`. |

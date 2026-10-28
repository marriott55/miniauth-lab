# AGENTS.md — Reglas para Agentes en MiniAuth Lab

Este repositorio contiene **MiniAuth Lab**, un entorno didáctico de Verificación y Validación de Software (Equipo 6) diseñado para completarse en **15 a 20 minutos** combinando análisis dinámico de seguridad (**OWASP ZAP** / DAST) y pruebas de aceptación basadas en comportamiento (**Cucumber-JVM** / BDD en Gherkin español).

## 1. Reglas Inquebrantables de Seguridad y Alcance

1. **Confinamiento a `127.0.0.1` y red interna:**
   - Todos los puertos publicados en `compose.yaml` y `compose.dev.yaml` deben enlazarse explícitamente a `127.0.0.1` (`127.0.0.1:5000:5000` y `127.0.0.1:8080:8080`).
   - Prohibido usar `0.0.0.0` en el lado del host, `network_mode: host`, `privileged: true` o montar `/var/run/docker.sock`.
2. **Vulnerabilidades deliberadas y acotadas:**
   - La aplicación `app` omite deliberadamente las cabeceras HTTP `Content-Security-Policy` (CSP) y `X-Frame-Options` en respuestas HTML como `GET /login` para que OWASP ZAP detecte de forma pasiva:
     - `Content Security Policy (CSP) Header Not Set` (`10038-1`)
     - `Missing Anti-clickjacking Header` (`10020-1`)
   - No añadir vulnerabilidades no solicitadas (SQLi, RCE, XSS persistente) ni simular alertas falsas desde la aplicación.
3. **Cero secretos reales:**
   - El único usuario de prueba es ficticio (`estudiante` / `Taller123!`), almacenado en memoria de forma determinista.
   - No registrar contraseñas ni cookies de sesión en los logs.
   - No incluir tokens reales de GitHub ni claves de producción.

## 2. Reglas de Arquitectura y Experiencia del Estudiante

1. **Cero dependencias locales en la máquina del alumno:**
   - El estudiante solo necesita **Git** y **Docker con Docker Compose**. No exigir Java, Maven, Python ni OWASP ZAP instalados en su sistema anfitrión.
2. **Diferencia explícita de nombres de host:**
   - Desde el navegador del anfitrión (host): `http://localhost:5000` (MiniAuth) y `http://localhost:8080/zap` (ZAP Webswing).
   - Desde el interior de los contenedores (`zap` y `cucumber`) en la red `miniauth_net`: `http://app:5000`.
3. **Gherkin 100 % en español y ejecución offline:**
   - Los archivos `.feature` usan `# language: es`.
   - El contenedor `cucumber` debe precargar todas las dependencias y plugins de Maven en fase de construcción (`docker build`) para ejecutarse sin depender de descargas externas durante la sesión de clase.
   - Mantener los dos modos verificables por comando:
     - Suite normal (PASS, exit code 0): `docker compose run --rm cucumber`
     - Fallo controlado (FAIL por aserción, exit code != 0): `docker compose run --rm -e CUCUMBER_FILTER_TAGS="@fallo-controlado" cucumber`
4. **Honestidad de verificación:**
   - No declarar pruebas o plataformas como verificadas si no se ejecutaron realmente. Documentar siempre los resultados reales en `docs/VALIDACION.md`.

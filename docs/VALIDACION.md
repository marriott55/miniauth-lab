# Registro de Validación y Aceptación — MiniAuth Lab

**Fecha de verificación:** 2026-10-28  
**Directorio de trabajo:** `d:\Users\mapro\Documents\TallerVyVTeam6`  
**Ambiente de prueba:** Windows (PowerShell), Python `3.14.0`, Java `22.0.2`, Apache Maven (con Cucumber-JVM `7.18.1`, JUnit Platform `1.10.3`, Flask `3.0.3`, pytest `8.3.3`), Git `2.51.0.windows.1`.

---

## 1. Resumen de Criterios de Aceptación (Sección 9)

| Categoría | Criterio de Aceptación | Estado Real | Evidencia / Detalle |
|---|---|---|---|
| **9.1 Aplicación** | `GET /health` devuelve HTTP `200` y `{"status":"ok"}` | **VERIFICADO (PASS)** | `test_health_endpoint_returns_200_ok` + prueba HTTP directa. |
| **9.1 Aplicación** | `GET /login` devuelve HTML `200` con formulario y etiquetas en español | **VERIFICADO (PASS)** | `test_login_page_renders_expected_html`. |
| **9.1 Aplicación** | Credenciales correctas (`estudiante` / `Taller123!`) acceden a `/perfil` con `Bienvenido, estudiante` | **VERIFICADO (PASS)** | `test_valid_credentials_grant_profile_access` + escenario Cucumber `Inicio de sesión correcto`. |
| **9.1 Aplicación** | Contraseña incorrecta o usuario inexistente devuelven `401` con `Credenciales incorrectas` | **VERIFICADO (PASS)** | `test_wrong_password_rejected_with_message`, `test_nonexistent_user_rejected_with_same_message` + escenario Cucumber `Rechazo de contraseña incorrecta`. |
| **9.1 Aplicación** | Acceso a `/perfil` sin sesión redirige (`302`) a `/login` | **VERIFICADO (PASS)** | `test_profile_without_session_redirects_to_login`. |
| **9.1 Aplicación** | `POST /logout` invalida la sesión | **VERIFICADO (PASS)** | `test_logout_invalidates_session`. |
| **9.1 Aplicación** | `GET /login` carece deliberadamente de `Content-Security-Policy`, `X-Frame-Options` y `frame-ancestors` | **VERIFICADO (PASS)** | `test_login_omits_csp_and_clickjacking_headers_deliberately` + comprobación de cabeceras en vivo (`CSP present: False`, `X-Frame-Options present: False`). |
| **9.1 Aplicación** | Servidor Flask sin `debug=True` ni credenciales reales | **VERIFICADO (PASS)** | `test_flask_debug_disabled`. |
| **9.4 Cucumber** | Suite normal ejecuta 2 escenarios en Gherkin español y termina con `exit code 0` | **VERIFICADO (PASS)** | `2 Scenarios (2 passed)`, `8 Steps (8 passed)`, `BUILD SUCCESS` (`Normal exit code: 0`). |
| **9.4 Cucumber** | Suite de fallo controlado (`@fallo-controlado`) termina con `exit code != 0` por aserción comprensible | **VERIFICADO (PASS)** | `1 Scenarios (1 failed)`, `Fallo de aserción BDD: Se esperaba encontrar el mensaje ["Acceso denegado"] en la respuesta HTML (ruta /perfil, HTTP 200), pero no estuvo presente.` (`Fallo-controlado exit code: 1`). |
| **9.4 Cucumber** | Re-ejecución de suite normal tras el fallo termina con éxito (`exit code 0`) | **VERIFICADO (PASS)** | `2 Scenarios (2 passed)`, `BUILD SUCCESS` (`Re-run exit code: 0`). |
| **9.4 Cucumber** | Ejecución en modo 100 % offline (`mvn -o test`) sin requerir internet | **VERIFICADO (PASS)** | Se comprobó y corrigió el precargado del proveedor `surefire-junit-platform` mediante warmup de `@warmup-cache-only`; `mvn -o` ejecutó sin conexión externa. |
| **9.2 Contenedores** | Archivos `compose.yaml`, `compose.dev.yaml`, `app/Dockerfile` y `cucumber/Dockerfile` implementados con bind `127.0.0.1` | **PENDIENTE DE EJECUTAR EN HOST CON DOCKER** | En esta máquina de desarrollo el binario `docker` no está instalado (`CommandNotFoundException`). La validación en contenedor se automatizó en `.github/workflows/ci.yml`. |
| **9.3 OWASP ZAP** | Observación interactiva en Webswing (`ghcr.io/zaproxy/zaproxy:2.16.0`) de alertas `10038-1` y `10020-1` | **PENDIENTE DE EJECUTAR EN HOST CON DOCKER** | Las cabeceras HTTP que disparan determinísticamente ambas reglas pasivas (`10038-1` y `10020-1`) fueron verificadas en vivo sobre la respuesta `GET /login`; la ejecución del contenedor `zap` requiere un host con Docker activo. |

---

## 2. Salidas Reales Observadas en Este Entorno

### 2.1 Suite de Contrato Backend (`pytest app/tests/test_app.py -v`)

```text
platform win32 -- Python 3.14.0, pytest-8.3.3, pluggy-1.7.0
collected 10 items

app/tests/test_app.py::TestMiniAuthContract::test_flask_debug_disabled PASSED [ 10%]
app/tests/test_app.py::TestMiniAuthContract::test_health_endpoint_returns_200_ok PASSED [ 20%]
app/tests/test_app.py::TestMiniAuthContract::test_login_omits_csp_and_clickjacking_headers_deliberately PASSED [ 30%]
app/tests/test_app.py::TestMiniAuthContract::test_login_page_renders_expected_html PASSED [ 40%]
app/tests/test_app.py::TestMiniAuthContract::test_logout_invalidates_session PASSED [ 50%]
app/tests/test_app.py::TestMiniAuthContract::test_nonexistent_user_rejected_with_same_message PASSED [ 60%]
app/tests/test_app.py::TestMiniAuthContract::test_profile_without_session_redirects_to_login PASSED [ 70%]
app/tests/test_app.py::TestMiniAuthContract::test_root_redirects_to_login PASSED [ 80%]
app/tests/test_app.py::TestMiniAuthContract::test_valid_credentials_grant_profile_access PASSED [ 90%]
app/tests/test_app.py::TestMiniAuthContract::test_wrong_password_rejected_with_message PASSED [100%]

10 passed in 0.34s
```

### 2.2 Verificación E2E de Servidor Flask Real + Cucumber-JVM Offline (`mvn -o`)

1. **Comprobación de salud y ausencia de cabeceras en `http://127.0.0.1:5000/login`:**
   ```text
   === HEALTH ===
   {"status":"ok"}
   === LOGIN STATUS & HEADERS ===
   Status: 200
   CSP present: False
   X-Frame-Options present: False
   ```

2. **Suite Cucumber Normal (`-Dcucumber.filter.tags=not @fallo-controlado`):**
   ```text
   2 Scenarios (2 passed)
   8 Steps (8 passed)
   0m0.493s
   [INFO] BUILD SUCCESS
   Normal exit code: 0
   ```

3. **Suite Cucumber de Fallo Controlado (`-Dcucumber.filter.tags=@fallo-controlado`):**
   ```text
   @fallo-controlado
   Escenario: Mensaje esperado equivocado
     Dado que existe el usuario de demostración
     Cuando inicia sesión con usuario "estudiante" y contraseña "Taller123!"
     Entonces debe ver el mensaje "Acceso denegado"
         org.opentest4j.AssertionFailedError: Fallo de aserción BDD: Se esperaba encontrar el mensaje ["Acceso denegado"] en la respuesta HTML (ruta /perfil, HTTP 200), pero no estuvo presente. ==> expected: <true> but was: <false>

   1 Scenarios (1 failed)
   3 Steps (1 failed, 2 passed)
   [INFO] BUILD FAILURE
   Fallo-controlado exit code: 1
   ```

4. **Re-ejecución de Suite Cucumber Normal (`PASS`):**
   ```text
   2 Scenarios (2 passed)
   8 Steps (8 passed)
   [INFO] BUILD SUCCESS
   Re-run exit code: 0
   ```

---

## 3. Lista de Verificación Manual en Equipo con Docker Desktop (Antes del Release `v1.0.0`)

En cuanto abras el repositorio en una máquina con Docker Desktop instalado y en ejecución, ejecuta esta secuencia de 5 minutos para completar la validación de contenedores y publicar las imágenes en GHCR:

1. **Validar sintaxis y levantar contenedores construidos localmente:**
   ```bash
   docker compose -f compose.yaml -f compose.dev.yaml config
   docker compose -f compose.yaml -f compose.dev.yaml up -d --build
   docker compose ps
   ```
2. **Probar Cucumber en contenedor (PASS → FAIL → PASS):**
   ```bash
   docker compose -f compose.yaml -f compose.dev.yaml run --rm cucumber
   docker compose -f compose.yaml -f compose.dev.yaml run --rm -e CUCUMBER_FILTER_TAGS=@fallo-controlado cucumber
   docker compose -f compose.yaml -f compose.dev.yaml run --rm cucumber
   ```
3. **Confirmar en `http://localhost:8080/zap` (OWASP ZAP 2.16.0 Webswing):**
   - Seleccionar *No persistir sesión* → *Start*.
   - Abrir *Tools → Manual Request Editor...* → enviar `GET http://app:5000/login`.
   - Confirmar en el panel `Alerts` las dos alertas pasivas:
     - `Content Security Policy (CSP) Header Not Set` (`10038-1`)
     - `Missing Anti-clickjacking Header` (`10020-1`)
4. **Publicar imágenes en GHCR:**
   - Subir el repositorio a GitHub (`https://github.com/marriott55/miniauth-lab`), crear el tag `v1.0.0` (o disparar `.github/workflows/publish-images.yml`), cambiar la visibilidad de `miniauth-app` y `miniauth-cucumber` a **Public** en GitHub Packages y verificar `docker compose pull`.

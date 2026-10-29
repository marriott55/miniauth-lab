# Registro de Validación y Aceptación — MiniAuth Lab (v1.1)

**Fecha de verificación:** 2026-10-28  
**Directorio de trabajo:** `d:\Users\mapro\Documents\TallerVyVTeam6`  
**Ambiente verificado:** Windows 11 (PowerShell), Docker Engine `29.9.2` (`build a82e528`), Docker Compose `v5.6.1`, Python `3.14.0` (host) / `3.12.6` (contenedor), Java `21` (contenedor `eclipse-temurin-21`), Cucumber-JVM `7.18.1`, OWASP ZAP `2.16.0` (`ghcr.io/zaproxy/zaproxy:2.16.0`), Git `2.51.0.windows.1`.

---

## 1. Resumen de Criterios de Aceptación (Sección 9 e Instrucciones v1.1)

| Categoría | Criterio de Aceptación | Estado Real | Evidencia / Detalle |
|---|---|---|---|
| **9.1 Aplicación** | `GET /health` devuelve HTTP `200` y `{"status":"ok"}` | **VERIFICADO (PASS)** | `test_health_endpoint_returns_200_ok` + contenedor `miniauth-app` en estado `Up (healthy)`. |
| **9.1 Aplicación** | `GET /login`, `POST /login`, `GET /perfil` y `POST /logout` funcionan según especificación | **VERIFICADO (PASS)** | 10/10 tests en `pytest` + pruebas manuales y automatizadas en contenedor. |
| **9.1 Aplicación** | `GET /login` omite deliberadamente `Content-Security-Policy` y `X-Frame-Options` | **VERIFICADO (PASS)** | Comprobado por `pytest` y por análisis pasivo real en OWASP ZAP 2.16.0. |
| **9.2 Contenedores** | `docker compose config` válido en modo alumno (`compose.yaml`) y modo dev (`compose.dev.yaml`) | **VERIFICADO (PASS)** | Salida limpia sin advertencias de interpolación (`exit code 0`). |
| **9.2 Contenedores** | `miniauth-app` y `miniauth-zap` activos y enlazados exclusivamente a `127.0.0.1` | **VERIFICADO (PASS)** | `127.0.0.1:5000->5000/tcp` y `127.0.0.1:8080->8080/tcp`. |
| **9.3 OWASP ZAP** | Observación real en ZAP 2.16.0 Webswing tras petición pasiva a `http://app:5000/login` | **VERIFICADO (PASS)** | Se observaron las dos alertas objetivo (`Content Security Policy (CSP) Header Not Set` y `Missing Anti-clickjacking Header`) junto con alertas pasivas adicionales (`Absence of Anti-CSRF Tokens`, `X-Content-Type-Options Header Missing`, `Authentication Request Identified`). |
| **v1.1 — Paso 1** | Suite normal en contenedor: `docker compose ... run --rm cucumber` | **VERIFICADO (PASS)** | `2 Scenarios (2 passed)`, `8 Steps (8 passed)`, `BUILD SUCCESS` (`exit code 0`, `3.756 s`). |
| **v1.1 — Paso 2** | Escenario `@fallo-controlado` antes de editar el `.feature` | **VERIFICADO (PASS)** | `1 Scenarios (1 failed)`, `Fallo de aserción BDD: Se esperaba encontrar el mensaje ["Acceso denegado"]...`, `BUILD FAILURE` (`exit code 1`, `2.620 s`). |
| **v1.1 — Paso 3** | Edición en el host (`"Acceso denegado"` → `"Bienvenido, estudiante"`) reflejada en el contenedor vía bind mount de solo lectura sin reconstruir imagen | **VERIFICADO (PASS)** | `Copying 3 resources from src/test/resources to target/test-classes` → `1 Scenarios (1 passed)`, `3 Steps (3 passed)`, `BUILD SUCCESS` (`exit code 0`, `2.867 s`). |
| **v1.1 — Paso 4** | Restauración con `git restore cucumber/src/test/resources/features/autenticacion_fallo.feature` y re-ejecución etiquetada | **VERIFICADO (PASS)** | Vuelve a fallar por aserción (`1 Scenarios (1 failed)`, `BUILD FAILURE`, `exit code 1`, `2.882 s`). |
| **v1.1 — Paso 5** | Suite normal final en contenedor tras restaurar | **VERIFICADO (PASS)** | `2 Scenarios (2 passed)`, `8 Steps (8 passed)`, `BUILD SUCCESS` (`exit code 0`, `2.924 s`). |

---

## 2. Evidencia de la Secuencia Obligatoria en Contenedores Docker (v1.1)

### 2.1 Estado de los servicios en ejecución (`docker ps`)

```text
CONTAINER ID   IMAGE                            COMMAND                  STATUS                    PORTS                      NAMES
13ef727deffb   ghcr.io/zaproxy/zaproxy:2.16.0   "zap-webswing.sh"        Up 28 minutes (healthy)   127.0.0.1:8080->8080/tcp   miniauth-zap
a4412cec2c99   miniauth-app:local               "gunicorn --bind 0.0…"   Up 28 minutes (healthy)   127.0.0.1:5000->5000/tcp   miniauth-app
```

### 2.2 Secuencia de 5 pasos de Cucumber en contenedor con bind mount de `autenticacion_fallo.feature`

1. **Paso 1 — Suite normal (`PASS`):**
   ```text
   $ docker compose -f compose.yaml -f compose.dev.yaml run --rm cucumber
   [INFO] --- resources:3.3.1:testResources (default-testResources) @ miniauth-cucumber ---
   [INFO] Copying 3 resources from src/test/resources to target/test-classes
   ...
   2 Scenarios (2 passed)
   8 Steps (8 passed)
   0m0.614s
   [WARNING] Tests run: 3, Failures: 0, Errors: 0, Skipped: 1
   [INFO] BUILD SUCCESS
   [INFO] Total time:  3.756 s
   Exit code: 0
   ```

2. **Paso 2 — Escenario `@fallo-controlado` antes de editar (`FAIL` por aserción):**
   ```text
   $ docker compose -f compose.yaml -f compose.dev.yaml run --rm -e CUCUMBER_FILTER_TAGS=@fallo-controlado cucumber
   [INFO] Copying 3 resources from src/test/resources to target/test-classes
   ...
   @fallo-controlado
   Escenario: Mensaje esperado equivocado
     Dado que existe el usuario de demostración
     Cuando inicia sesión con usuario "estudiante" y contraseña "Taller123!"
     Entonces debe ver el mensaje "Acceso denegado"
         org.opentest4j.AssertionFailedError: Fallo de aserción BDD: Se esperaba encontrar el mensaje ["Acceso denegado"] en la respuesta HTML (ruta /perfil, HTTP 200), pero no estuvo presente. ==> expected: <true> but was: <false>

   1 Scenarios (1 failed)
   3 Steps (1 failed, 2 passed)
   [ERROR] Tests run: 3, Failures: 1, Errors: 0, Skipped: 2
   [INFO] BUILD FAILURE
   [INFO] Total time:  2.620 s
   Exit code: 1
   ```

3. **Paso 3 — Tras cambiar en el host `"Acceso denegado"` por `"Bienvenido, estudiante"` (`PASS` sin rebuild):**
   ```text
   $ docker compose -f compose.yaml -f compose.dev.yaml run --rm -e CUCUMBER_FILTER_TAGS=@fallo-controlado cucumber
   [INFO] Copying 3 resources from src/test/resources to target/test-classes
   ...
   @fallo-controlado
   Escenario: Mensaje esperado equivocado
     Dado que existe el usuario de demostración
     Cuando inicia sesión con usuario "estudiante" y contraseña "Taller123!"
     Entonces debe ver el mensaje "Bienvenido, estudiante"

   1 Scenarios (1 passed)
   3 Steps (3 passed)
   0m0.476s
   [WARNING] Tests run: 3, Failures: 0, Errors: 0, Skipped: 2
   [INFO] BUILD SUCCESS
   [INFO] Total time:  2.867 s
   Exit code: 0
   ```

4. **Paso 4 — Tras ejecutar `git restore cucumber/src/test/resources/features/autenticacion_fallo.feature` (`FAIL` restaurado):**
   ```text
   $ git restore cucumber/src/test/resources/features/autenticacion_fallo.feature
   $ docker compose -f compose.yaml -f compose.dev.yaml run --rm -e CUCUMBER_FILTER_TAGS=@fallo-controlado cucumber
   1 Scenarios (1 failed)
   3 Steps (1 failed, 2 passed)
   [ERROR] Tests run: 3, Failures: 1, Errors: 0, Skipped: 2
   [INFO] BUILD FAILURE
   [INFO] Total time:  2.882 s
   Exit code: 1
   ```

5. **Paso 5 — Suite normal final (`PASS`):**
   ```text
   $ docker compose -f compose.yaml -f compose.dev.yaml run --rm cucumber
   2 Scenarios (2 passed)
   8 Steps (8 passed)
   0m0.428s
   [WARNING] Tests run: 3, Failures: 0, Errors: 0, Skipped: 1
   [INFO] BUILD SUCCESS
   [INFO] Total time:  2.924 s
   Exit code: 0
   ```

---

## 3. Plataformas y Pendientes Reales Antes de Difundir el Taller

- **Plataforma validada directamente con contenedores:** Windows 11 (PowerShell + Docker Desktop con WSL 2).
- **Plataformas documentadas pero no ejecutadas directamente en esta máquina:** macOS (Intel / Apple Silicon) y Linux nativo.
- **Pendientes reales del autor antes de publicar el release definitivo:**
  1. **Capturas reales en `docs/capturas/`:** **COMPLETADO.** Las 10 capturas PNG reales (`01-login.png` a `10-cucumber-corregido.png`) fueron verificadas e integradas en [`README.md`](file:///d:/Users/mapro/Documents/TallerVyVTeam6/README.md).
  2. **Publicación en GHCR:** Subir el repositorio a GitHub, publicar las imágenes `miniauth-app` y `miniauth-cucumber` en GHCR, configurarlas como **Public** y comprobar `docker compose pull` sin credenciales.
  3. **Ensayo de usabilidad (≤ 20 min):** Realizar la prueba cronometrada con un estudiante nuevo partiendo con Docker e imágenes descargadas.

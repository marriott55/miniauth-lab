# Guía Detallada de Solución de Problemas (Troubleshooting) — MiniAuth Lab

Este documento amplía la sección de solución de problemas del `README.md` con diagnóstico paso a paso para los 11 escenarios más frecuentes en talleres con Windows, macOS y Linux.

---

## 1. El demonio de Docker está apagado (`Cannot connect to the Docker daemon`)

- **Síntoma literal aproximado:**
  ```text
  error during connect: ... open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
  ```
  o en Linux/macOS:
  ```text
  Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
  ```
- **Causa:** Docker Desktop (Windows/macOS) o el servicio `docker` (Linux) no está iniciado.
- **Comandos exactos:**
  - En **Windows / macOS**: abre la aplicación **Docker Desktop**, espera unos 20–30 segundos a que el icono de la ballena deje de animarse y ejecuta:
    ```bash
    docker info
    ```
  - En **Linux**:
    ```bash
    sudo systemctl start docker
    docker info
    ```
- **Resultado esperado:** `docker info` imprime la sección `Server: Docker Engine` sin mensajes de error.

---

## 2. Puerto ocupado en la máquina anfitriona (`port is already allocated`)

- **Síntoma literal aproximado:**
  ```text
  Error response from daemon: Ports are not available: exposing port TCP 127.0.0.1:5000 -> 0.0.0.0:0: listen tcp 127.0.0.1:5000: bind: address already in use
  ```
- **Causa:** Otro contenedor o proceso local está usando el puerto `5000` (por ejemplo, ControlCenter/AirPlay Receiver en macOS o un servidor Flask previo) o el `8080`.
- **Comandos exactos:**
  1. Ver contenedores en ejecución:
     ```bash
     docker ps
     ```
  2. Detener contenedores previos:
     ```bash
     docker compose down
     ```
  3. En **macOS**, si el puerto `5000` sigue ocupado por el sistema operativo, desactiva **Receptor AirPlay** en *Configuración del Sistema → General → AirDrop y Handoff*, o verifica qué proceso ocupa el puerto:
     ```bash
     # Windows PowerShell:
     Get-NetTCPConnection -LocalPort 5000,8080 -ErrorAction SilentlyContinue
     # Linux / macOS:
     lsof -i :5000
     ```
- **Resultado esperado:** `docker compose up -d` inicia `miniauth-app` y `miniauth-zap` sin errores de enlace de puerto.

---

## 3. Imagen no descargada o fallo de red (`manifest unknown` / `pull access denied`)

- **Síntoma literal aproximado:**
  ```text
  Error response from daemon: pull access denied for ghcr.io/... or manifest unknown
  ```
- **Causa:** No se ejecutó la descarga previa, la conexión del aula está saturada o deseas construir las imágenes localmente sin depender de GHCR.
- **Comandos exactos:**
  ```bash
  # Opción A: Reintentar descarga desde el registro
  docker compose pull

  # Opción B (Plan de respaldo 100 % local): Construir desde los Dockerfiles incluidos
  docker compose -f compose.yaml -f compose.dev.yaml up -d --build
  ```
- **Resultado esperado:** Las imágenes `miniauth-app` y `miniauth-cucumber` quedan disponibles en `docker images`.

---

## 4. Permiso denegado al socket de Docker en Linux (`permission denied`)

- **Síntoma literal aproximado:**
  ```text
  permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
  ```
- **Causa:** Tu usuario de Linux no pertenece al grupo `docker`.
- **Comandos exactos:**
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker
  docker compose ps
  ```
- **Resultado esperado:** `docker compose ps` responde sin necesidad de anteponer `sudo`.

---

## 5. La interfaz de OWASP ZAP (Webswing) tarda en cargar o muestra página en blanco

- **Síntoma literal aproximado:** Al abrir `http://localhost:8080/zap` aparece el mensaje *"Starting application..."*, *"Connecting..."* o no carga aún la ventana de ZAP.
- **Causa:** ZAP con Webswing arranca una máquina virtual Java y su servidor gráfico embebido; suele tardar entre **20 y 45 segundos** tras ejecutar `docker compose up -d`.
- **Comandos exactos:**
  ```bash
  docker compose logs --tail=30 zap
  ```
  Espera unos segundos y recarga en tu navegador la URL exacta (con `/zap` al final):
  ```text
  http://localhost:8080/zap
  ```
- **Resultado esperado:** Aparece el cuadro de diálogo inicial de OWASP ZAP (*"¿Quiere persistir la sesión de ZAP?"* / *"Do you want to persist the ZAP session?"*).

---

## 6. OWASP ZAP no muestra alertas en la pestaña `Alerts`

- **Síntoma literal aproximado:** El panel inferior `Alerts` (Alertas) muestra `0` alertas tras visitar la aplicación en el navegador normal de tu computadora.
- **Causa:** Visitar `http://localhost:5000` en Chrome/Edge/Firefox de tu computadora **no pasa por el proxy de ZAP**. La petición debe realizarse **desde dentro de OWASP ZAP** hacia `http://app:5000/login`.
- **Pasos exactos:**
  1. Dentro de la ventana de ZAP (`http://localhost:8080/zap`), ve a la pestaña central **Quick Start** → haz clic en **Manual Explore** (o usa el diálogo **Open URL in ZAP** / **Request Editor**).
  2. Escribe exactamente `http://app:5000/login` y envía la solicitud.
  3. Espera de 2 a 5 segundos a que la cola del escáner pasivo vuelva a `0`.
- **Resultado esperado:** El nodo `http://app:5000` aparece en el árbol `Sites` y se listan las alertas `Content Security Policy (CSP) Header Not Set` y `Missing Anti-clickjacking Header` en `Alerts`.

---

## 7. Error de conexión en ZAP al usar `http://localhost:5000` en lugar de `http://app:5000`

- **Síntoma literal aproximado:** ZAP muestra error `Connection refused` al intentar explorar `http://localhost:5000/login`.
- **Causa:** Dentro del contenedor `zap`, `localhost` se refiere al propio contenedor de ZAP, no al contenedor donde corre Flask.
- **Solución exacta:** Sustituye `localhost` por el nombre DNS del servicio en la red de Docker Compose:
  ```text
  http://app:5000/login
  ```
- **Resultado esperado:** ZAP recibe la respuesta `HTTP/1.1 200 OK` con el HTML de MiniAuth Lab.

---

## 8. Cucumber no logra conectarse a la aplicación (`Connection refused` / fallo en `checkHealth`)

- **Síntoma literal aproximado:**
  ```text
  org.opentest4j.AssertionFailedError: No fue posible conectar con MiniAuth en http://app:5000/health.
  ```
- **Causa:** El contenedor `app` está detenido o todavía no ha alcanzado el estado `healthy`.
- **Comandos exactos:**
  ```bash
  docker compose up -d app
  docker compose ps
  ```
  Verifica que la columna `STATUS` de `miniauth-app` indique `(healthy)` y vuelve a ejecutar:
  ```bash
  docker compose run --rm cucumber
  ```
- **Resultado esperado:** Los 2 escenarios de la suite normal terminan en `BUILD SUCCESS`.

---

## 9. Escenario marcado como `Undefined step` en Cucumber

- **Síntoma literal aproximado:**
  ```text
  io.cucumber.junit.platform.engine.UndefinedStepException: The step '...' is undefined.
  ```
- **Causa:** Se modificó accidentalmente el texto de un archivo `.feature` sin actualizar la anotación `@Dado` / `@Cuando` / `@Entonces` correspondiente en `StepDefinitions.java`.
- **Comandos exactos:**
  Restaura los archivos `.feature` a su estado original con Git:
  ```bash
  git checkout -- cucumber/src/test/resources/features/
  ```
- **Resultado esperado:** Todos los pasos vuelven a coincidir con `StepDefinitions.java`.

---

## 10. Error de Maven en modo offline (`Cannot access central in offline mode`)

- **Síntoma literal aproximado:**
  ```text
  Cannot access central (https://repo.maven.apache.org/maven2) in offline mode
  ```
- **Causa:** La imagen local de `cucumber` quedó con una caché incompleta tras un cambio en `pom.xml`.
- **Comandos exactos:**
  Reconstruye la imagen de `cucumber` con conexión a internet:
  ```bash
  docker compose -f compose.yaml -f compose.dev.yaml build --no-cache cucumber
  ```
- **Resultado esperado:** La fase `RUN mvn --batch-mode dependency:go-offline test-compile` precarga todos los artefactos y `mvn -o test` funciona sin red.

---

## 11. El comando de fallo controlado falla por sintaxis de variable de entorno y no por aserción

- **Síntoma literal aproximado:** Se ejecutan 3 escenarios o ninguno al pasar `-e CUCUMBER_FILTER_TAGS`.
- **Causa:** Comillas mal cerradas en la terminal al invocar Docker Compose.
- **Comando exacto universal (válido en PowerShell, Bash y zsh):**
  ```bash
  docker compose run --rm -e CUCUMBER_FILTER_TAGS=@fallo-controlado cucumber
  ```
- **Resultado esperado:** Se ejecuta únicamente el escenario `Mensaje esperado equivocado` (`Tests run: 1, Failures: 1`) y aparece el mensaje `Fallo de aserción BDD: Se esperaba encontrar el mensaje ["Acceso denegado"]`.

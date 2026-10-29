# Guía de Desarrollo, Construcción y Publicación — MiniAuth Lab

Este documento describe cómo desarrollar, probar localmente, construir las imágenes Docker y publicar versiones en **GitHub Container Registry (GHCR)**.

---

## 1. Operación Local para Desarrolladores (sin GHCR)

Mientras que los estudiantes utilizan `compose.yaml` (que consume imágenes preconstruidas desde GHCR), los desarrolladores cuentan con `compose.dev.yaml` para compilar localmente desde `./app/Dockerfile` y `./cucumber/Dockerfile`.

### 1.1 Validar la configuración de Compose

```bash
docker compose -f compose.yaml config
docker compose -f compose.yaml -f compose.dev.yaml config
```

### 1.2 Construir y levantar el entorno localmente

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d --build
```

### 1.3 Ejecutar la suite Cucumber local (PASS y FAIL controlado)

- **Suite normal (2 escenarios PASS, código de salida `0`):**
  ```bash
  docker compose -f compose.yaml -f compose.dev.yaml run --rm cucumber
  ```
- **Escenario de fallo controlado (1 escenario FAIL por aserción, código de salida distinto de `0`):**
  ```bash
  docker compose -f compose.yaml -f compose.dev.yaml run --rm -e CUCUMBER_FILTER_TAGS="@fallo-controlado" cucumber
  ```

### 1.4 Apagar el entorno

```bash
docker compose -f compose.yaml -f compose.dev.yaml down
```

---

## 2. Ejecución Directa en Host (Desarrollo Rápido sin Docker)

Si estás editando el código de Flask o los pasos de Cucumber en tu máquina de desarrollo:

### 2.1 Ejecutar pruebas de contrato de Flask (`pytest` o `unittest`)

```bash
python -m venv .venv
# En Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# En Linux / macOS:
# source .venv/bin/activate

pip install -r app/requirements.txt
pytest app/tests/test_app.py -v
```

### 2.2 Levantar Flask y ejecutar Cucumber desde Maven en el host

En una terminal levanta la aplicación:

```bash
python app/app.py
```

En otra terminal ejecuta Cucumber apuntando a `http://127.0.0.1:5000`:

```bash
# Suite normal (PASS):
mvn -f cucumber/pom.xml test "-Dminiauth.target.url=http://127.0.0.1:5000" "-Dcucumber.filter.tags=not @fallo-controlado"

# Escenario de fallo controlado (FAIL por aserción):
mvn -f cucumber/pom.xml test "-Dminiauth.target.url=http://127.0.0.1:5000" "-Dcucumber.filter.tags=@fallo-controlado"
```

---

## 3. Publicación de Imágenes en GHCR

El flujo automatizado se encuentra en [`.github/workflows/publish-images.yml`](file:///d:/Users/mapro/Documents/TallerVyVTeam6/.github/workflows/publish-images.yml).

### 3.1 Pasos para publicar una nueva versión (`v1.1.0`)

1. Asegúrate de que el propietario en `compose.yaml` coincida en minúsculas con tu cuenta u organización de GitHub (`ghcr.io/<owner>/miniauth-app:v1.1.0` y `ghcr.io/<owner>/miniauth-cucumber:v1.1.0`).
2. Crea y empuja el tag de versión tras superar todas las validaciones:
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0 para Taller V&V"
   git push origin main --tags
   ```
   O bien ejecuta manualmente el workflow **Publicar Imágenes en GHCR** desde la pestaña **Actions** en GitHub (`workflow_dispatch`).
3. **Configurar visibilidad pública en GHCR (imprescindible para los alumnos):**
   - Ve a tu perfil u organización en GitHub → pestaña **Packages**.
   - Entra en `miniauth-app` → **Package settings** → sección **Danger Zone** → **Change visibility** → selecciona **Public**.
   - Repite el mismo paso para `miniauth-cucumber`.
4. Comprueba desde una terminal sin sesión iniciada en `ghcr.io` que `docker compose pull` descarga las tres imágenes sin pedir credenciales.

### 3.2 Verificación de manifiesto multi-arquitectura

Una vez publicadas las imágenes, puedes comprobar el soporte para `linux/amd64` y `linux/arm64` (Apple Silicon) con:

```bash
docker buildx imagetools inspect ghcr.io/marriott55/miniauth-app:v1.1.0
docker buildx imagetools inspect ghcr.io/marriott55/miniauth-cucumber:v1.1.0
```

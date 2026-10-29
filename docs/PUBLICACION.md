# Guía Paso a Paso de Publicación del Release `v1.1.0` — MiniAuth Lab

Este documento detalla el procedimiento completo para publicar por primera vez el repositorio **MiniAuth Lab** en GitHub (`https://github.com/marriott55/miniauth-lab`) y sus dos imágenes preconstruidas en **GitHub Container Registry (GHCR)**:

- `ghcr.io/marriott55/miniauth-app:v1.1.0`
- `ghcr.io/marriott55/miniauth-cucumber:v1.1.0`

*(OWASP ZAP utiliza directamente su imagen oficial pública `ghcr.io/zaproxy/zaproxy:2.16.0`).*

---

## 1. Cómo publicar el repositorio local en GitHub

1. **Crear el repositorio vacío en GitHub:**
   - Inicia sesión en GitHub con la cuenta **`marriott55`**.
   - Entra en https://github.com/new.
   - En **Repository name**, escribe exactamente: `miniauth-lab`
   - En **Visibility**, selecciona **Public**.
   - **No marques** las casillas *Add a README file*, *Add .gitignore* ni *Choose a license* (el repositorio local ya los incluye).
   - Haz clic en **Create repository**.

2. **Confirmar y registrar los cambios locales en Git:**
   Desde una terminal ubicada en `D:\Users\mapro\Documents\TallerVyVTeam6`, verifica que el árbol de trabajo esté limpio y con todos los cambios del release `v1.1.0` confirmados:

   ```powershell
   git status
   git add .
   git commit -m "chore(release): prepare MiniAuth Lab v1.1.0 for public release"
   ```

3. **Enlazar el remoto `origin` y subir la rama `main`:**

   ```powershell
   git remote add origin https://github.com/marriott55/miniauth-lab.git
   git remote -v
   git push -u origin main
   ```

---

## 2. Cómo iniciar el workflow de publicación de imágenes (`v1.1.0`)

El workflow [`.github/workflows/publish-images.yml`](../.github/workflows/publish-images.yml) admite dos métodos de activación. Puedes usar cualquiera de los dos:

### Opción A (Recomendada): Crear y subir el tag Git `v1.1.0`

En tu terminal local, crea el tag anotado `v1.1.0` y súbelo a GitHub:

```powershell
git tag -a v1.1.0 -m "Release v1.1.0 — MiniAuth Lab (Taller V&V Equipo 6)"
git push origin v1.1.0
```

Al detectar el push del tag `v1.1.0` (patrón `v*.*.*`), GitHub Actions iniciará automáticamente el workflow **Publicar Imágenes en GHCR**.

### Opción B (Alternativa manual): Ejecutar `workflow_dispatch` desde navegador

1. Abre `https://github.com/marriott55/miniauth-lab/actions` en tu navegador.
2. En la columna izquierda, selecciona **Publicar Imágenes en GHCR**.
3. Haz clic en el botón desplegable **Run workflow** (a la derecha).
4. Verifica que la rama sea `main` y que el campo **Etiqueta de versión a publicar** contenga `v1.1.0`.
5. Haz clic en el botón verde **Run workflow**.

---

## 3. Cómo revisar el resultado de GitHub Actions

1. Entra en `https://github.com/marriott55/miniauth-lab/actions`.
2. Haz clic sobre la ejecución en curso de **Publicar Imágenes en GHCR**.
3. Observarás dos trabajos encadenados:
   - **`Validar App y Cucumber en linux/amd64 antes de publicar` (`validate-amd64`):**
     - Comprueba la sintaxis de `compose.yaml` y `compose.dev.yaml`.
     - Construye localmente `app` y `cucumber`, levanta `app` hasta estar `healthy`, ejecuta los escenarios normales (`PASS`) y prueba la edición del archivo `autenticacion_fallo.feature` mediante el bind mount (`PASS`) antes de restaurarlo.
     - Si alguna prueba falla, este trabajo se detiene y **bloquea la publicación** para evitar subir imágenes defectuosas.
   - **`Construir y publicar imágenes multi-arquitectura en GHCR` (`publish-ghcr`):**
     - Se inicia automáticamente cuando `validate-amd64` termina en verde.
     - Configura QEMU y Docker Buildx, inicia sesión en `ghcr.io` usando `GITHUB_TOKEN` y construye y publica `miniauth-app:v1.1.0` y `miniauth-cucumber:v1.1.0` para las plataformas **`linux/amd64` y `linux/arm64`**.
4. Espera a que ambos trabajos muestren el icono verde de completado (**✓**).

---

## 4. Cómo encontrar los dos paquetes en GHCR

Una vez finalizada la ejecución del workflow:

1. Entra en la página principal del repositorio: `https://github.com/marriott55/miniauth-lab`.
2. Mira la barra lateral derecha, en la sección **Packages** (o accede directamente a `https://github.com/marriott55?tab=packages&repo_name=miniauth-lab`).
3. Deben aparecer listados los dos paquetes vinculados al repositorio:
   - **`miniauth-app`**
   - **`miniauth-cucumber`**

---

## 5. Cómo establecer su visibilidad pública (Paso imprescindible)

Por defecto, GitHub Container Registry puede crear los paquetes nuevos con visibilidad **Private** o **Internal**. Para que los estudiantes puedan ejecutar `docker compose pull` sin cuenta ni token de GitHub, **debes cambiar ambos paquetes a `Public`**:

1. Haz clic sobre el paquete **`miniauth-app`**.
2. En la esquina superior derecha (o en el menú lateral derecho de la página del paquete), haz clic en **Package settings**.
3. Desplázate hasta el final de la página, a la sección roja **Danger Zone**.
4. En **Change package visibility**, haz clic en **Change visibility**.
5. Selecciona **Public**, escribe el nombre del paquete (`miniauth-app`) para confirmar y pulsa **I understand the consequences, change package visibility**.
6. Regresa a la lista de paquetes, entra en **`miniauth-cucumber`** y repite exactamente los pasos 2 a 5.

---

## 6. Cómo comprobar que las imágenes pueden descargarse sin autenticación

Para verificar que cualquier estudiante podrá descargar las imágenes de forma anónima:

1. Cierra cualquier sesión previa de Docker en `ghcr.io` en tu terminal:

   ```powershell
   docker logout ghcr.io
   ```

2. Inspecciona los manifiestos remotos para confirmar que son públicos y que incluyen soporte multi-arquitectura (`linux/amd64` y `linux/arm64`):

   ```powershell
   docker buildx imagetools inspect ghcr.io/marriott55/miniauth-app:v1.1.0
   docker buildx imagetools inspect ghcr.io/marriott55/miniauth-cucumber:v1.1.0
   ```

3. Descarga las imágenes usando el comando de preparación de los estudiantes:

   ```powershell
   docker compose pull
   ```

   **Resultado esperado:** `miniauth-app:v1.1.0`, `miniauth-cucumber:v1.1.0` y `zaproxy:2.16.0` se descargan con éxito sin solicitar usuario ni contraseña.

---

## 7. Cómo realizar una prueba limpia del laboratorio con los comandos definitivos del README

Simula la experiencia exacta de un estudiante ejecutando en orden los comandos del `README.md`:

```powershell
# 1. Asegurar que no hay contenedores previos activos
docker compose down

# 2. Levantar el entorno con las imágenes descargadas de GHCR
docker compose up -d
docker compose ps

# 3. Ejecutar los 2 escenarios normales de Cucumber (debe terminar en BUILD SUCCESS)
docker compose run --rm cucumber

# 4. Ejecutar el escenario de fallo controlado (debe terminar en BUILD FAILURE por aserción)
docker compose run --rm -e CUCUMBER_FILTER_TAGS=@fallo-controlado cucumber

# 5. Apagar el entorno al terminar
docker compose down
```

---

## 8. Cómo actuar si falla una construcción o publicación

| Problema observado | Causa probable | Cómo resolverlo |
|---|---|---|
| El trabajo `publish-ghcr` falla en `Login to GitHub Container Registry` o al hacer push con `403 Forbidden` | Los permisos de GitHub Actions en el repositorio están restringidos a solo lectura | En el repositorio de GitHub, ve a **Settings → Actions → General → Workflow permissions**, selecciona **Read and write permissions**, haz clic en **Save** y vuelve a lanzar el workflow (`Re-run jobs`). |
| `docker compose pull` devuelve `pull access denied` o `unauthorized` | Uno o ambos paquetes (`miniauth-app` o `miniauth-cucumber`) siguen en estado **Private** en GHCR | Completa la **Sección 5** de esta guía para cambiar la visibilidad de ambos paquetes a **Public**. |
| `docker compose pull` devuelve `manifest unknown` | La etiqueta publicada en GHCR no coincide con `v1.1.0` | Verifica en la pestaña **Packages** que exista la etiqueta `v1.1.0`. Si ejecutaste el workflow manualmente con otra etiqueta, vuelve a ejecutarlo indicando `v1.1.0`. |
| El paquete aparece en el perfil de usuario pero no en la portada del repositorio | El paquete aún no se vinculó visualmente al repositorio | Entra en el paquete en GitHub → **Package settings** → **Connect Repository** → selecciona `miniauth-lab`. |
| El paso de Buildx para `linux/arm64` tarda más de lo habitual en GitHub Actions | La compilación de `arm64` se ejecuta bajo emulación QEMU en el runner `ubuntu-latest` (`amd64`) | Es el comportamiento normal en la primera publicación (suele tardar entre 4 y 8 minutos en total). Espera a que termine sin cancelar el trabajo. |

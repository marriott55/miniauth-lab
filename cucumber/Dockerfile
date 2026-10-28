FROM maven:3.9.9-eclipse-temurin-21

LABEL org.opencontainers.image.title="MiniAuth Lab - Cucumber BDD" \
      org.opencontainers.image.description="Suite de pruebas de aceptación BDD con Cucumber-JVM y Gherkin en español para MiniAuth Lab" \
      org.opencontainers.image.version="1.0.0"

WORKDIR /workspace

# Crear usuario no root con directorio home escribible para caché Maven
RUN groupadd --gid 10002 cucumber && \
    useradd --uid 10002 --gid cucumber --shell /bin/bash --create-home cucumber && \
    chown -R cucumber:cucumber /workspace

USER cucumber

# 1. Copiar pom.xml primero para aprovechar la caché de capas de Docker
COPY --chown=cucumber:cucumber pom.xml /workspace/pom.xml

# 2. Copiar código fuente de pruebas y recursos Gherkin
COPY --chown=cucumber:cucumber src /workspace/src

# 3. Resolver dependencias, proveedores dinámicos de Surefire/JUnit Platform y compilar tests.
#    Se ejecuta una pasada real de `mvn test` con un filtro de etiqueta vacío (@warmup-cache-only)
#    para que Surefire y Cucumber JUnit Platform descarguen todos sus proveedores internos sin
#    requerir que el servidor Flask esté activo durante el docker build. Así `mvn -o test`
#    funciona 100% sin conexión a internet durante la clase.
RUN mvn --batch-mode dependency:go-offline test \
    "-Dcucumber.filter.tags=@warmup-cache-only" \
    "-Dsurefire.failIfNoSpecifiedTests=false"

ENV MINIAUTH_TARGET_URL="http://app:5000" \
    CUCUMBER_FILTER_TAGS="not @fallo-controlado"

# Ejecuta en modo offline (-o) usando las dependencias y plugins precargados en la imagen
ENTRYPOINT ["sh", "-c", "exec mvn --batch-mode -o test \"-Dcucumber.filter.tags=${CUCUMBER_FILTER_TAGS}\""]

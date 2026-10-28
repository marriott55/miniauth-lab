FROM python:3.12.6-slim-bookworm

LABEL org.opencontainers.image.title="MiniAuth Lab - App" \
      org.opencontainers.image.description="Aplicación web deliberadamente vulnerable para laboratorio DAST (OWASP ZAP) y BDD (Cucumber)" \
      org.opencontainers.image.version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MINIAUTH_PORT=5000

WORKDIR /app

# Crear usuario no root para ejecutar el servicio
RUN groupadd --gid 10001 miniauth && \
    useradd --uid 10001 --gid miniauth --shell /usr/sbin/nologin --create-home miniauth

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip==24.2 && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=miniauth:miniauth . /app

USER miniauth

EXPOSE 5000

# Healthcheck usando la biblioteca estándar de Python (sin depender de curl)
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
    CMD python -c "import urllib.request, sys; r = urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2); sys.exit(0 if r.status == 200 else 1)"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]

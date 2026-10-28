"""
MiniAuth Lab — Aplicación Web Deliberadamente Vulnerable para Laboratorio V&V.

Propósito educativo:
1. DAST (OWASP ZAP): Omite deliberadamente las cabeceras HTTP de defensa en
   profundidad `Content-Security-Policy` (CSP) y `X-Frame-Options` en sus
   respuestas HTML (ej. `GET /login`), permitiendo observar dos alertas pasivas
   reales y deterministas sin requerir escaneo activo.
2. BDD (Cucumber-JVM): Implementa el flujo de inicio de sesión, perfil protegido
   y cierre de sesión verificable mediante escenarios en Gherkin español.

ADVERTENCIA: Uso exclusivo en entorno local de laboratorio (127.0.0.1).
Nunca desplegar en producción ni exponer en redes públicas.
"""

import logging
import os
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

# Configuración de registro discreto: nunca registra contraseñas ni cookies.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] miniauth: %(message)s",
)
logger = logging.getLogger("miniauth")

# Base de usuarios en memoria (ficticia, constante y determinista).
# En un sistema real de producción se almacenarían hashes robustos (Argon2id/bcrypt)
# en una base de datos persistente, nunca texto plano en memoria.
DEMO_USERS = {
    "estudiante": "Taller123!",
}

AUTH_ERROR_MESSAGE = "Credenciales incorrectas"


def create_app() -> Flask:
    """Crea y configura la instancia de la aplicación Flask."""
    flask_app = Flask(__name__)

    # Clave de sesión pedagógica de laboratorio. Nunca reutilizar fuera del taller.
    flask_app.config["SECRET_KEY"] = os.environ.get(
        "MINIAUTH_SECRET_KEY",
        "miniauth-lab-insecure-secret-key-do-not-use-in-prod",
    )
    flask_app.config["DEBUG"] = False
    flask_app.config["TESTING"] = False
    flask_app.config["SESSION_COOKIE_HTTPONLY"] = True
    flask_app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    @flask_app.after_request
    def omit_security_headers_deliberately(response):
        """
        VULNERABILIDAD DELIBERADA DE LABORATORIO (Sección 3.4):
        Se garantiza explícitamente que las respuestas HTML carezcan de:
        - Content-Security-Policy (genera alerta ZAP 10038-1)
        - X-Frame-Options (genera alerta ZAP 10020-1)
        """
        response.headers.pop("Content-Security-Policy", None)
        response.headers.pop("X-Frame-Options", None)
        return response

    @flask_app.get("/")
    def index():
        """Ruta raíz: redirige de forma coherente a /login."""
        return redirect(url_for("login_get"))

    @flask_app.get("/login")
    def login_get():
        """Muestra el formulario de inicio de sesión."""
        return render_template("login.html", error=None), 200

    @flask_app.post("/login")
    def login_post():
        """Procesa las credenciales enviadas en el formulario de autenticación."""
        username = (
            request.form.get("username")
            or request.form.get("usuario")
            or ""
        ).strip()
        password = (
            request.form.get("password")
            or request.form.get("contrasena")
            or ""
        )

        expected_password = DEMO_USERS.get(username)
        if expected_password is not None and expected_password == password:
            session.clear()
            session["user"] = username
            logger.info("Inicio de sesion exitoso para el usuario de demostracion.")
            return redirect(url_for("perfil"))

        # Mismo mensaje para usuario inexistente o contraseña incorrecta
        # para evitar enumeración de usuarios (requisito BDD 3.3).
        logger.info("Intento de inicio de sesion rechazado.")
        return render_template("login.html", error=AUTH_ERROR_MESSAGE), 401

    @flask_app.get("/perfil")
    def perfil():
        """Página de perfil protegida por sesión."""
        current_user = session.get("user")
        if not current_user:
            return redirect(url_for("login_get"))
        return render_template("perfil.html", username=current_user), 200

    @flask_app.post("/logout")
    def logout():
        """Cierra la sesión actual e invalida el estado de autenticación."""
        session.clear()
        logger.info("Sesion cerrada correctamente.")
        return redirect(url_for("login_get"))

    @flask_app.get("/health")
    def health():
        """Endpoint de salud para Docker Compose y pruebas automatizadas."""
        return jsonify({"status": "ok"}), 200

    return flask_app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("MINIAUTH_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)

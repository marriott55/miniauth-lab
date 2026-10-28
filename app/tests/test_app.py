"""
Pruebas automatizadas de contrato para MiniAuth Lab (Sección 9.1).

Verifica tanto con `pytest` como con `python -m unittest`:
- /health devuelve HTTP 200 con {"status": "ok"}.
- / redirige a /login.
- /login devuelve HTML 200 con formulario y título MiniAuth Lab.
- Credenciales correctas (estudiante / Taller123!) acceden a /perfil con "Bienvenido, estudiante".
- Contraseña incorrecta o usuario inexistente devuelven 401 con "Credenciales incorrectas".
- /perfil sin sesión redirige a /login.
- /logout invalida la sesión activa.
- Respuesta HTML de /login carece deliberadamente de Content-Security-Policy,
  X-Frame-Options y directiva frame-ancestors (requisito DAST para OWASP ZAP).
- El modo debug de Flask está desactivado.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, create_app  # noqa: E402


class TestMiniAuthContract(unittest.TestCase):
    """Pruebas de contrato funcional y de seguridad deliberada para MiniAuth Lab."""

    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()

    def test_flask_debug_disabled(self) -> None:
        """Verifica que la aplicación no se ejecute en modo debug."""
        self.assertFalse(app.debug)
        self.assertFalse(self.app.config.get("DEBUG", False))

    def test_health_endpoint_returns_200_ok(self) -> None:
        """Verifica que GET /health devuelva HTTP 200 y {"status": "ok"}."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_root_redirects_to_login(self) -> None:
        """Verifica que GET / redirija de forma coherente a /login."""
        response = self.client.get("/", follow_redirects=False)
        self.assertIn(response.status_code, (301, 302, 303))
        self.assertTrue(response.headers.get("Location", "").endswith("/login"))

    def test_login_page_renders_expected_html(self) -> None:
        """Verifica que GET /login devuelva HTML 200 con formulario y etiquetas."""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("MiniAuth Lab", body)
        self.assertIn('<form', body)
        self.assertIn('name="username"', body)
        self.assertIn('name="password"', body)
        self.assertIn("Usuario", body)
        self.assertIn("Contraseña", body)

    def test_login_omits_csp_and_clickjacking_headers_deliberately(self) -> None:
        """
        Verifica las vulnerabilidades deliberadas (Sección 3.4):
        - Sin cabecera Content-Security-Policy (ZAP 10038-1)
        - Sin cabecera X-Frame-Options ni frame-ancestors (ZAP 10020-1)
        """
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Content-Security-Policy", response.headers)
        self.assertNotIn("X-Frame-Options", response.headers)
        csp_value = response.headers.get("Content-Security-Policy", "")
        self.assertNotIn("frame-ancestors", csp_value.lower())

    def test_valid_credentials_grant_profile_access(self) -> None:
        """Credenciales correctas redirigen a /perfil con 'Bienvenido, estudiante'."""
        response = self.client.post(
            "/login",
            data={"username": "estudiante", "password": "Taller123!"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Bienvenido, estudiante", body)

    def test_wrong_password_rejected_with_message(self) -> None:
        """Contraseña incorrecta rechaza el acceso y muestra 'Credenciales incorrectas'."""
        response = self.client.post(
            "/login",
            data={"username": "estudiante", "password": "incorrecta"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 401)
        body = response.get_data(as_text=True)
        self.assertIn("Credenciales incorrectas", body)
        self.assertNotIn("Bienvenido, estudiante", body)

    def test_nonexistent_user_rejected_with_same_message(self) -> None:
        """Usuario inexistente muestra exactamente el mismo mensaje de rechazo."""
        response = self.client.post(
            "/login",
            data={"username": "intruso", "password": "Taller123!"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 401)
        body = response.get_data(as_text=True)
        self.assertIn("Credenciales incorrectas", body)
        self.assertNotIn("Bienvenido,", body)

    def test_profile_without_session_redirects_to_login(self) -> None:
        """Acceso a /perfil sin sesión redirige a /login."""
        response = self.client.get("/perfil", follow_redirects=False)
        self.assertIn(response.status_code, (301, 302, 303))
        self.assertTrue(response.headers.get("Location", "").endswith("/login"))

    def test_logout_invalidates_session(self) -> None:
        """POST /logout invalida la sesión e impide volver a /perfil sin autenticarse."""
        login_res = self.client.post(
            "/login",
            data={"username": "estudiante", "password": "Taller123!"},
            follow_redirects=True,
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("Bienvenido, estudiante", login_res.get_data(as_text=True))

        logout_res = self.client.post("/logout", follow_redirects=False)
        self.assertIn(logout_res.status_code, (301, 302, 303))
        self.assertTrue(logout_res.headers.get("Location", "").endswith("/login"))

        profile_after_logout = self.client.get("/perfil", follow_redirects=False)
        self.assertIn(profile_after_logout.status_code, (301, 302, 303))
        self.assertTrue(
            profile_after_logout.headers.get("Location", "").endswith("/login")
        )


if __name__ == "__main__":
    unittest.main()

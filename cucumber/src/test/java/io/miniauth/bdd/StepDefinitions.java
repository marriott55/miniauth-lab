package io.miniauth.bdd;

import io.cucumber.java.Before;
import io.cucumber.java.es.Cuando;
import io.cucumber.java.es.Dado;
import io.cucumber.java.es.Entonces;
import org.junit.jupiter.api.Assertions;

import java.io.IOException;

/**
 * Definición de pasos (Step Definitions) en español para MiniAuth Lab.
 *
 * <p>Ejecuta peticiones HTTP reales contra el servicio MiniAuth sin utilizar mocks.</p>
 */
public class StepDefinitions {

    private HttpTestClient httpClient;

    @Before
    public void inicializarClienteAislado() {
        this.httpClient = new HttpTestClient();
    }

    @Dado("que existe el usuario de demostración")
    public void queExisteElUsuarioDeDemostracion() {
        boolean healthy = httpClient.checkHealth();
        Assertions.assertTrue(
                healthy,
                "No fue posible conectar con MiniAuth en " + httpClient.getBaseUrl()
                        + "/health. Verifica que el contenedor 'app' esté en ejecución (healthy)."
        );
    }

    @Cuando("inicia sesión con usuario {string} y contraseña {string}")
    public void iniciaSesionConUsuarioYContrasena(String usuario, String contrasena)
            throws IOException, InterruptedException {
        httpClient.login(usuario, contrasena);
    }

    @Entonces("debe acceder a su perfil")
    public void debeAccederASuPerfil() {
        Assertions.assertEquals(
                200,
                httpClient.getLastStatusCode(),
                "Se esperaba código HTTP 200 al acceder al perfil."
        );
        Assertions.assertEquals(
                "/perfil",
                httpClient.getLastPath(),
                "Se esperaba que la ruta final tras autenticar fuera '/perfil', pero fue '"
                        + httpClient.getLastPath() + "'."
        );
    }

    @Entonces("el acceso debe ser rechazado")
    public void elAccesoDebeSerRechazado() {
        Assertions.assertEquals(
                401,
                httpClient.getLastStatusCode(),
                "Se esperaba código HTTP 401 cuando las credenciales son inválidas."
        );
        Assertions.assertEquals(
                "/login",
                httpClient.getLastPath(),
                "Un inicio de sesión rechazado debe permanecer en '/login'."
        );
    }

    @Entonces("debe ver el mensaje {string}")
    public void debeVerElMensaje(String mensajeEsperado) {
        String cuerpoHtml = httpClient.getLastBody();
        Assertions.assertTrue(
                cuerpoHtml != null && cuerpoHtml.contains(mensajeEsperado),
                () -> String.format(
                        "Fallo de aserción BDD: Se esperaba encontrar el mensaje [\"%s\"] en la respuesta HTML (ruta %s, HTTP %d), pero no estuvo presente.",
                        mensajeEsperado,
                        httpClient.getLastPath(),
                        httpClient.getLastStatusCode()
                )
        );
    }
}

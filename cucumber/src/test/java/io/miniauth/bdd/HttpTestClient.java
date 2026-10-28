package io.miniauth.bdd;

import java.io.IOException;
import java.net.CookieManager;
import java.net.CookiePolicy;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Optional;

/**
 * Cliente HTTP ligero basado en {@link java.net.http.HttpClient} para las pruebas BDD.
 *
 * <p>Cada instancia mantiene su propio {@link CookieManager} aislado para garantizar que
 * ningún escenario comparta estado ni cookies de sesión con otro (Sección 4.4).</p>
 */
public class HttpTestClient {

    private final String baseUrl;
    private final HttpClient client;
    private int lastStatusCode;
    private String lastPath = "";
    private String lastBody = "";

    public HttpTestClient() {
        String configuredUrl = System.getProperty(
                "miniauth.target.url",
                System.getenv().getOrDefault("MINIAUTH_TARGET_URL", "http://app:5000")
        );
        if (configuredUrl.endsWith("/")) {
            configuredUrl = configuredUrl.substring(0, configuredUrl.length() - 1);
        }
        this.baseUrl = configuredUrl;

        CookieManager cookieManager = new CookieManager(null, CookiePolicy.ACCEPT_ALL);
        this.client = HttpClient.newBuilder()
                .cookieHandler(cookieManager)
                .connectTimeout(Duration.ofSeconds(5))
                .followRedirects(HttpClient.Redirect.NEVER)
                .build();
    }

    /**
     * Comprueba que el servicio MiniAuth esté activo consultando {@code GET /health}.
     */
    public boolean checkHealth() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/health"))
                    .timeout(Duration.ofSeconds(5))
                    .GET()
                    .build();
            HttpResponse<String> response = client.send(
                    request,
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8)
            );
            return response.statusCode() == 200 && response.body().contains("\"ok\"");
        } catch (IOException | InterruptedException e) {
            if (e instanceof InterruptedException) {
                Thread.currentThread().interrupt();
            }
            return false;
        }
    }

    /**
     * Envía el formulario {@code POST /login} y sigue redirecciones HTTP (301/302/303)
     * conservando la cookie de sesión en este cliente aislado.
     */
    public void login(String username, String password) throws IOException, InterruptedException {
        String formBody = "username=" + URLEncoder.encode(username, StandardCharsets.UTF_8)
                + "&password=" + URLEncoder.encode(password, StandardCharsets.UTF_8);

        URI loginUri = URI.create(baseUrl + "/login");
        HttpRequest request = HttpRequest.newBuilder()
                .uri(loginUri)
                .timeout(Duration.ofSeconds(5))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(formBody, StandardCharsets.UTF_8))
                .build();

        HttpResponse<String> response = client.send(
                request,
                HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8)
        );
        followRedirectsIfNeeded(loginUri, response);
    }

    /**
     * Realiza una petición {@code GET} a una ruta relativa (ej. {@code /perfil})
     * siguiendo redirecciones si ocurren.
     */
    public void get(String path) throws IOException, InterruptedException {
        URI targetUri = URI.create(baseUrl + path);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(targetUri)
                .timeout(Duration.ofSeconds(5))
                .GET()
                .build();

        HttpResponse<String> response = client.send(
                request,
                HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8)
        );
        followRedirectsIfNeeded(targetUri, response);
    }

    private void followRedirectsIfNeeded(URI initialUri, HttpResponse<String> initialResponse)
            throws IOException, InterruptedException {
        HttpResponse<String> currentResponse = initialResponse;
        URI currentUri = initialUri;
        int redirectCount = 0;

        while (isRedirect(currentResponse.statusCode()) && redirectCount < 5) {
            Optional<String> locationHeader = currentResponse.headers().firstValue("Location");
            if (locationHeader.isEmpty()) {
                break;
            }
            currentUri = currentUri.resolve(locationHeader.get());
            HttpRequest redirectGet = HttpRequest.newBuilder()
                    .uri(currentUri)
                    .timeout(Duration.ofSeconds(5))
                    .GET()
                    .build();
            currentResponse = client.send(
                    redirectGet,
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8)
            );
            redirectCount++;
        }

        this.lastStatusCode = currentResponse.statusCode();
        this.lastPath = currentUri.getPath();
        this.lastBody = currentResponse.body();
    }

    private boolean isRedirect(int statusCode) {
        return statusCode == 301 || statusCode == 302 || statusCode == 303
                || statusCode == 307 || statusCode == 308;
    }

    public int getLastStatusCode() {
        return lastStatusCode;
    }

    public String getLastPath() {
        return lastPath;
    }

    public String getLastBody() {
        return lastBody;
    }

    public String getBaseUrl() {
        return baseUrl;
    }
}

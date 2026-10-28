# language: es
@fallo-controlado
Característica: Comprobación deliberadamente incorrecta
  Escenario: Mensaje esperado equivocado
    Dado que existe el usuario de demostración
    Cuando inicia sesión con usuario "estudiante" y contraseña "Taller123!"
    Entonces debe ver el mensaje "Acceso denegado"

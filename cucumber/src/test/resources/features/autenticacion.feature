# language: es
@normal
Característica: Autenticación de usuarios
  Para proteger el acceso al perfil
  Como usuario de MiniAuth
  Quiero iniciar sesión con mis credenciales

  Escenario: Inicio de sesión correcto
    Dado que existe el usuario de demostración
    Cuando inicia sesión con usuario "estudiante" y contraseña "Taller123!"
    Entonces debe acceder a su perfil
    Y debe ver el mensaje "Bienvenido, estudiante"

  Escenario: Rechazo de contraseña incorrecta
    Dado que existe el usuario de demostración
    Cuando inicia sesión con usuario "estudiante" y contraseña "incorrecta"
    Entonces el acceso debe ser rechazado
    Y debe ver el mensaje "Credenciales incorrectas"

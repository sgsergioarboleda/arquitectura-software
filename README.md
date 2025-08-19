## Integrantes 
* Santiago Garzón
* Brayan Guerrero
* David Martinez

## Proyecto de automatizacion de tareas Escuela de Ciencias de la Computacion e Inteligencia Artificial
Sergio Arboleda

## Objetivo General
Automatizar diversas tareas de la Universidad Sergio Arboleda con el fin de mejorar la capacidad de toma decisiones tanto para estudiantes como para profesores.

## Objetivos especificos
* Generacion automatizada de horarios para profesores y estudiantes impulsado por Inteligencia Artificial, teniendo en cuenta las diferentes variables que esto implica.
* Automatizar la gestion de entrega y recuperacion de objetos perdidos desde el area de Decanatura de estudiantes.
* Automatizaciones de horarios de eventos  y actividades universitarias, debido a que entre tantos canales de comunicaciones, muchos eventos pasan desapercibidos.
* Canal informativo estudiantil relacionado al conocimiento de becas estudiantiles a las que los estudiantes pueden acceder, asi como conocer sus requerimientos y condiciones.
* Crear un portal web donde se integren los anteriores proyectos.

# Tecnologias a usar:

* ReactJs
* Python con fastapi
* Python con librerias de modelos de IA
* Nube con AWS
* Servicio SageMaker (Por ver)

# Sistema de Autenticación JWT

El proyecto incluye un sistema completo de autenticación basado en JWT (JSON Web Tokens) que protege todos los endpoints de la API.

## Características de Seguridad

- **Autenticación**: Login con correo y contraseña
- **Autorización**: Tokens JWT para acceso a endpoints protegidos
- **Protección**: Todos los endpoints de usuarios requieren autenticación
- **Verificación**: Validación automática de tokens en cada petición

## Endpoints de Autenticación

- `POST /auth/login` - Autenticar usuario y obtener token
- `POST /auth/logout` - Cerrar sesión
- `GET /auth/verify` - Verificar validez de token

## Configuración

Configura la clave secreta en las variables de entorno:

```bash
SECRET_PHRASE=tu-clave-super-secreta-aqui
JWT_EXPIRATION_MINUTES=30
```

Para más detalles, consulta [Auth/README.md](Auth/README.md).

# Resultados a esperar
Para la creacion del portal web se usará un frontend construido por *ReactJS*, y un backend con fastapi. El portal tendrá control de acceso (IAM), con keycloack. Donde se tendra diferentes roles de usuario, todavia por definir.

Para el proyecto de generacion Automatizada de horarios para profesores y estudiantes por IA, se realizara un proceso de ML supervisado, el procedimiento y metodologia aun esta por definirse.
Las variables a tomar en cuenta relacionada a este proyecta, salones, profesores, carga academica de cada profesor, cantidad de creditos por estudiantes, preferencia horario tanto para estudiante como profesor, cantidad de horas semanales por materia.

Para automatizar la gestion de entrega y recuperacion de objetos perdidos, se planea crear un portal web donde se pueda registrar tanto la foto del objeto, como la persona quien lo entrego (con posibilidad de ser anonima), y donde se encontro.

Para los horarios de eventos y actividades universitarias, se planea un portal centralizado, de diferentes administradores, con la posibilidad de crear eventos y publicarlos en el portal, asi como conocer su ubicacion, y saber que otros eventos ocurren en la misma franja horaria.

En el caso del canal informativo de becas estudiantiles, se planea una pagina informativa, con la capacidad de editarse segun el perfil de administrador, para conocer las becas, sus requerimientos y sus condiciones para aplicar, siendo completamente abierta a los estudiantes para conocer diferentes opciones de becas.


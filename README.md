# Juego Piedra, Papel o Tijera - Cliente Servidor

Proyecto académico desarrollado para la asignatura **Desarrollo de Apps Multiplataforma**. Consiste en un juego de Piedra, Papel o Tijera con versiones para PC y Android, utilizando un servidor central encargado de gestionar la comunicación entre los clientes y almacenar los resultados en una base de datos MySQL.

## Descripción

El proyecto implementa una arquitectura cliente-servidor en la que dos jugadores pueden conectarse desde diferentes plataformas y disputar una partida de Piedra, Papel o Tijera.

El servidor recibe las jugadas de los clientes, determina el resultado de la partida y registra la información en una base de datos. Además, permite consultar el ranking de jugadores y el historial de partidas mediante el envío de los resultados por correo electrónico.

## Arquitectura

```text
                 ┌──────────────────────┐
                 │     Cliente PC       │
                 │   Python + Tkinter   │
                 └──────────┬───────────┘
                            │
                            │ TCP / Socket
                            │
                 ┌──────────▼───────────┐
                 │       Servidor       │
                 │        Python        │
                 │                      │
                 │ Gestión de partidas  │
                 │ Comunicación TCP     │
                 │ MySQL                │
                 │ SMTP                 │
                 └───────┬───────┬──────┘
                         │       │
                    MySQL│       │SMTP
                         │       │
                 ┌───────▼──┐    ▼
                 │ Base de  │  Correo
                 │  datos   │
                 └──────────┘
                         ▲
                         │
                         │ TCP / Socket
                         │
                 ┌───────┴───────────┐
                 │  Cliente Android  │
                 │  Android Studio   │
                 │       Java        │
                 └───────────────────┘
```

## Funcionalidades

### Cliente PC

* Interfaz gráfica desarrollada con Tkinter.
* Conexión con el servidor mediante sockets TCP.
* Registro de jugadores mediante nickname.
* Juego de Piedra, Papel o Tijera.
* Selección de Piedra, Papel o Tijera.
* Determinación del resultado de la partida.
* Opción para jugar nuevamente.
* Consulta de resultados mediante correo electrónico.

### Cliente Android

* Aplicación desarrollada en Android Studio.
* Interfaz para acceder al juego y consultar resultados.
* Conexión TCP con el servidor.
* Registro mediante nickname.
* Envío de jugadas.
* Recepción del resultado de la partida.
* Opción para jugar nuevamente.
* Solicitud de resultados mediante correo electrónico.

### Servidor

* Servidor TCP desarrollado en Python.
* Gestión de conexiones de los clientes.
* Administración de dos jugadores por partida.
* Recepción y procesamiento de las jugadas.
* Determinación del ganador, perdedor o empate.
* Registro de resultados en MySQL.
* Consulta del ranking de jugadores.
* Consulta del historial de partidas.
* Generación y envío de resultados mediante correo electrónico.

### Base de datos

La base de datos utiliza MySQL y contiene:

* Tabla `jugadores`: almacena nickname, victorias y derrotas.
* Tabla `partidas`: almacena el ganador, perdedor y fecha de cada partida.
* Procedimiento almacenado `registrar_resultado`: actualiza las estadísticas y registra cada partida.

## Tecnologías utilizadas

* Python
* Tkinter
* Sockets TCP
* Threading
* MySQL
* MySQL Connector/Python
* SMTP
* Android Studio
* Java
* XML
* SQL

## Estructura del proyecto

```text
Juego-Piedra-Papel-Tijera-Cliente-Servidor/
│
├── Cliente-PC/
│   └── cliente.py
│
├── Android/
│   ├── app/
│   ├── gradle/
│   └── ...
│
├── Servidor/
│   └── servidor.py
│
├── SQL/
│   └── juego_app.sql
│
│
└── README.md
```

## Configuración

Antes de ejecutar el proyecto es necesario configurar la dirección IP del servidor en los clientes.

En el cliente PC:

```python
IP_Servidor = "IP_DEL_SERVIDOR"
Puerto = 1234
```

En las aplicaciones Android:

```java
private static final String IP_SERVIDOR = "IP_DEL_SERVIDOR";
private static final int PUERTO = 1234;
```

El servidor utiliza el puerto `1234` para las conexiones TCP.

## Configuración de MySQL

Crear la base de datos utilizando el archivo SQL incluido en la carpeta `SQL`.

La configuración del servidor debe coincidir con las credenciales de MySQL:

```python
ORIGEN = "localhost"
USUARIO = "root"
CONTRASENA = "TU_CONTRASEÑA"
BASEDATOS = "juego_app"
```

## Instalación de dependencias

Instalar la dependencia de MySQL Connector:

```bash
pip install mysql-connector-python
```

Las librerías `socket`, `threading`, `smtplib` y `email` utilizadas por el servidor forman parte de la biblioteca estándar de Python.

## Ejecución

### 1. Configurar MySQL

Ejecutar el script SQL para crear la base de datos, las tablas y el procedimiento almacenado.

### 2. Iniciar el servidor

Desde la carpeta del servidor:

```bash
python servidor.py
```

El servidor quedará esperando las conexiones de los clientes.

### 3. Ejecutar el cliente PC

Desde la carpeta correspondiente:

```bash
python cliente.py
```

### 4. Ejecutar el cliente Android

Abrir el proyecto en **Android Studio**, verificar la dirección IP del servidor y ejecutar la aplicación en un dispositivo o emulador compatible.

Para realizar una partida deben conectarse dos clientes y registrar sus respectivos nicknames.

## Flujo de una partida

```text
Cliente PC / Android
        │
        │ Conexión TCP
        ▼
     Servidor
        │
        │ Registro de jugadores
        ▼
  Espera 2 jugadores
        │
        │ Envío de jugadas
        ▼
Determinar resultado
        │
   ┌────┼────┐
   ▼    ▼    ▼
 Ganar Perder Empate
        │
        ▼
     MySQL
        │
        ▼
 Ranking e historial
        │
        ▼
     Correo
```

## Comunicación

Los clientes utilizan mensajes de texto estructurados mediante comandos separados por `|`.

Algunos ejemplos utilizados por el sistema son:

```text
NICKNAME|Jugador
JUGADA|piedra
JUGADA|papel
JUGADA|tijera
SOLO_CORREO
CORREO|correo@ejemplo.com
cerrar
```

El servidor responde con mensajes como:

```text
NICKNAME_OK
INICIO
GANASTE
PERDISTE
EMPATE
CORREO_OK
CORREO_ERROR
```

## Base de datos

La base de datos `juego_app` utiliza las siguientes tablas:

### jugadores

| Campo     | Descripción                   |
| --------- | ----------------------------- |
| id        | Identificador del jugador     |
| nickname  | Nombre del jugador            |
| victorias | Cantidad de partidas ganadas  |
| derrotas  | Cantidad de partidas perdidas |

### partidas

| Campo             | Descripción                 |
| ----------------- | --------------------------- |
| id                | Identificador de la partida |
| nickname_ganador  | Jugador ganador             |
| nickname_perdedor | Jugador perdedor            |
| fecha_hora        | Fecha y hora de la partida  |

## Correo electrónico

El servidor puede consultar el ranking y el historial almacenados en MySQL y generar un mensaje HTML con los resultados para enviarlo al correo indicado por el usuario.

## Proyecto académico

Este proyecto fue desarrollado como parte de las actividades académicas de la asignatura **Desarrollo de Apps Multiplataforma**, integrando conceptos de:

* Desarrollo de aplicaciones para Android.
* Programación en Python.
* Arquitectura cliente-servidor.
* Comunicación mediante sockets.
* Programación concurrente.
* Bases de datos SQL.
* Procedimientos almacenados.
* Comunicación mediante correo electrónico.
* Integración entre diferentes plataformas.

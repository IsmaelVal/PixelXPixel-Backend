# Pixel x Pixel Back End

Este repositorio contiene la lógica del servidor y la base de datos para el juego **Pixel x Pixel**. Incluye:

* Un contenedor de desarrollo con Python y SQL Server.
* El script de inicialización de la base de datos (`init_db.sql`) con tablas y datos de ejemplo.
* Un pequeño front-end de prueba en `static/index.html` para invocar los endpoints CRUD genéricos.
* Servicios REST en `web services/ws.py` (Flask + pymssql + Flask-CORS).

---

## Pre-requisitos

Antes de empezar, asegúrate de tener:

* **GitHub Codespaces** o Docker + Python 3.11 en tu máquina local.
* **Docker** corriendo (solo si no usas Codespaces).
* El contenedor de SQL Server disponible en el puerto **1433**.
* Python 3.11 y los paquetes listados en `.devcontainer/devcontainer.json`.

---

## Arrancar el contenedor (Codespaces)

1. Abre este repositorio en GitHub Codespaces.
2. El `.devcontainer/devcontainer.json` instalará **Python 3.11** y `docker-in-docker`.
3. Al crear el Codespace, automáticamente correrá:

   ```bash
   pip install pymssql flask flask-cors requests
   ```
4. El contenedor forwardea los puertos **1433**, **2025**, **5000**.

---

## Inicializar la base de datos

Dentro del Codespace (o en tu host con `sqlcmd` apuntando a tu SQL Server), ejecuta:

```bash
# Lanza un contenedor de SQL Server si no está ya levantado
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourPassword123!' \
  -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest

### Instalar sqlcmd
sh
sudo apt update
sudo apt install mssql-tools unixodbc-dev
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc

# Conéctate con sqlcmd
sqlcmd -S localhost -U sa -P YourPassword123!

# Desde sqlcmd, ejecuta:
:r .devcontainer/init_db.sql
GO

# Sal de sqlcmd
quit
```

Esto creará las tablas (`usuario`, `boleto`, `evento`, `imagen`, `pregunta`, `casillapixel`) y cargará datos de ejemplo.

---

## Estructura del proyecto

```
Pixel-x-Pixel-backend/
├── .devcontainer/
│   ├── devcontainer.json    # configuración del entorno Codespaces
│   └── init_db.sql          # script de creación y población de la BD
├── static/
│   └── index.html           # página de prueba CRUD genérico
└── web services/
    └── ws.py                # Flask app con endpoints de login y CRUD
```

---

## Ejecutar el servidor

1. Entra en el folder de servicios web:

   ```bash
   cd "web services"
   ```

2. Asegúrate de que la DB SQL Server esté corriendo y hayas importado `init_db.sql`.

3. Arranca la API Flask:

   ```bash
   python ws.py
   ```

   * La app escuchará en `http://localhost:5000`.
   * CORS está habilitado para todas las rutas.

---

## Probar endpoints

### Autenticación

* **POST** `/usuariored`
  Registro rápido vía redes sociales:

  ```json
  { "usuario": "nickFB", "contacto": "Facebook" }
  ```

* **POST** `/login`
  Login tradicional:

  ```json
  { "username": "user1", "password": "laClave" }
  ```

### CRUD Genérico

Carga `static/index.html` en tu navegador y usa el formulario para invocar:

* **GET**  `/test`            – obtener todos (envía `{ table: "usuario" }` en body)
* **GET**  `/test/<table>/<id>`
* **POST** `/test`            – insertar (body con `{ table, campo1:valor1,… }`)
* **PUT**  `/test/<table>/<id>`– actualizar (body con `{ campo1:valor… }`)
* **DELETE** `/test/<table>/<id>`

---

## Tecnologías usadas

* **Flask** – micro-framework Python
* **pymssql** – driver para SQL Server
* **Flask-CORS** – habilita CORS
* **Docker** – contenedor SQL Server
* **sqlcmd** – utilitario CLI para SQL Server

---

> **Nota:**
> Ajusta credenciales y puertos en `ws.py` y en tu contenedor según tus necesidades.

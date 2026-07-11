# 📘 Documentación del Proyecto — Finanzas App

> **Documento vivo.** Se actualiza al final de cada sesión. Registra la arquitectura, la explicación de cada archivo línea por línea, los conceptos aprendidos y el estado del proyecto.
>
> **Autor:** Carlos · **Última actualización:** Sesión 11 (autenticación cerrada + CRUD completo de transacciones)

---

## 📑 Índice

1. [Visión general del proyecto](#1-visión-general-del-proyecto)
2. [Arquitectura general](#2-arquitectura-general)
3. [Estructura de archivos](#3-estructura-de-archivos)
4. [Configuración del entorno](#4-configuración-del-entorno)
5. [Trabajar en dos equipos](#5-trabajar-en-dos-equipos)
6. [Explicación de cada archivo (línea por línea)](#6-explicación-de-cada-archivo-línea-por-línea)
7. [Conceptos clave aprendidos](#7-conceptos-clave-aprendidos)
8. [Comandos de referencia rápida](#8-comandos-de-referencia-rápida)
9. [Estado actual y próximos pasos](#9-estado-actual-y-próximos-pasos)
10. [Registro de sesiones](#10-registro-de-sesiones)
- [Anexo A — Instalación de herramientas desde cero](#anexo-a--instalación-de-herramientas-desde-cero)

---

## 1. Visión general del proyecto

**Finanzas App** es una aplicación de finanzas personales en pesos colombianos (COP). Permite registrar ingresos y gastos, ver un dashboard con el saldo, gestionar presupuestos por categoría con alertas automáticas, analizar el gasto y crear metas de ahorro (incluida una calculadora de fondo de emergencia).

Este proyecto es, sobre todo, un **vehículo de aprendizaje**: el objetivo es entender cada pieza que se construye, no solo hacerla funcionar.

**Stack técnico:**

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy |
| Servidor | Uvicorn |
| Seguridad | pwdlib (Argon2) + PyJWT |
| Frontend (planeado) | React / React Native — por decidir |
| Control de versiones | Git + GitHub |

**Repositorio:** `carlosgarciavalencia1989/finanzas-app`

---

## 2. Arquitectura general

La app tiene tres capas. La mejor analogía es un **restaurante**:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   FRONTEND  │ ───▶ │   BACKEND   │ ───▶ │ BASE DE DATOS│
│  (comedor)  │      │  (cocina)   │      │  (despensa) │
│             │ ◀─── │             │ ◀─── │             │
└─────────────┘      └─────────────┘      └─────────────┘
   Lo que ve          FastAPI: recibe        PostgreSQL:
   el usuario         peticiones, aplica     guarda los datos
                      la lógica              de forma permanente
```

- **Frontend (comedor):** la pantalla con la que interactúa el usuario.
- **Backend (cocina):** donde vive la lógica. Recibe peticiones, las procesa y responde. Es lo que estamos construyendo con FastAPI.
- **Base de datos (despensa):** donde se guardan los datos de forma permanente. Es PostgreSQL.
- **La API (el mesero):** es la que comunica al frontend con el backend, llevando pedidos y trayendo respuestas.

**Flujo de una petición típica** (ejemplo: registrarse):

1. El usuario envía sus datos (nombre, email, password) desde el frontend.
2. FastAPI recibe la petición en el endpoint `/registro`.
3. Pydantic **valida** los datos automáticamente.
4. La lógica del endpoint hashea la contraseña y prepara el usuario.
5. SQLAlchemy **traduce** la orden y la guarda en PostgreSQL.
6. FastAPI responde con los datos seguros (sin la contraseña).

---

## 3. Estructura de archivos

```
finanzas-app/
├── venv/                 # Entorno virtual (NO se sube a GitHub)
├── .env                  # Secretos: contraseñas, clave JWT (NO se sube)
├── .gitignore            # Lista de lo que Git debe ignorar
├── requirements.txt      # Lista de librerías del proyecto
├── README.md             # Descripción del proyecto
├── DOCUMENTACION.md      # Este documento
├── database.py           # Conexión a PostgreSQL + sesión + get_db
├── models.py             # Definición de tablas (clases SQLAlchemy)
├── schemas.py            # Formas de datos que entran/salen (Pydantic)
├── security.py           # Hasheo de contraseñas + creación de tokens JWT
└── main.py               # App FastAPI + todos los endpoints
```

**Regla mental de qué va en cada archivo:**

- `database.py` → **plomería**: cómo conectarse a la base de datos.
- `models.py` → **cómo se guardan** los datos (estructura de las tablas).
- `schemas.py` → **cómo viajan** los datos por la API (entrada/salida).
- `security.py` → todo lo relacionado con **contraseñas y tokens**.
- `main.py` → los **endpoints** (las rutas de la API) y el arranque de la app.

**Lo que NUNCA se sube a GitHub** (está en `.gitignore`):
- `venv/` — se recrea en cada equipo.
- `.env` — contiene secretos; se recrea a mano en cada equipo.
- `__pycache__/`, `*.pyc` — archivos temporales de Python.

---

## 4. Configuración del entorno

Pasos para dejar un equipo listo para desarrollar (resumen de las primeras sesiones).

### Herramientas base a instalar (resumen)
- **Python** (verificar con `python --version`)
- **Node.js** (verificar con `node --version`) — para el frontend futuro
- **Git** (verificar con `git --version`)
- **VS Code** (editor de código)
- **PostgreSQL + pgAdmin** (motor de base de datos + su interfaz visual)

> El paso a paso completo de instalación de cada una está en el **Anexo A** al final de este documento.

### Configurar Git (una vez por equipo)
```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tucorreo@ejemplo.com"
```

### Arreglar PowerShell (si npm o activar el venv falla)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Entorno virtual (venv)
El `venv` es una "caja" aislada donde viven las librerías del proyecto, separada del Python global del sistema.
```powershell
python -m venv venv            # crear la caja
.\venv\Scripts\Activate.ps1    # activarla (aparece (venv) al inicio de la línea)
```
> **Fuente de verdad:** si ves `(venv)` al inicio de la línea de la terminal, el entorno está activo. Ignora avisos de VS Code que sugieran crear otro entorno.

### Instalar librerías
Desde cero (equipo nuevo):
```powershell
pip install -r requirements.txt
```
O individualmente (como se hizo la primera vez):
```powershell
pip install fastapi uvicorn
pip install sqlalchemy psycopg2-binary
pip install "pwdlib[argon2]"
pip install "pydantic[email]"
pip install python-dotenv
pip install pyjwt
```

### Arrancar el servidor
```powershell
uvicorn main:app --reload
```
- `main` = archivo `main.py` · `app` = la variable `app = FastAPI()`
- `--reload` = reinicia solo al guardar cambios (para desarrollo)
- Corre en `http://127.0.0.1:8000`
- Documentación interactiva en `http://127.0.0.1:8000/docs`

> ⚠️ El servidor debe quedarse corriendo en su terminal. Si la cierras o presionas `Ctrl+C`, se apaga y el navegador dará `ERR_CONNECTION_REFUSED`. Usa una **segunda terminal** para otros comandos.

---

## 5. Trabajar en dos equipos

El proyecto vive en dos máquinas (portátil y PC de mesa), sincronizadas por GitHub.

**Qué viaja y qué no:**

| Elemento | ¿Viaja por GitHub? | Cómo se obtiene en el otro equipo |
|----------|--------------------|-----------------------------------|
| Código (`.py`) | ✅ Sí | `git clone` / `git pull` |
| `requirements.txt` | ✅ Sí | Viene con el clon |
| `venv/` | ❌ No | Se recrea: `python -m venv venv` |
| `.env` | ❌ No | Se crea a mano con los secretos locales |
| Base de datos `finanzas` | ❌ No | Se crea en el PostgreSQL local |
| Los datos guardados | ❌ No | Cada equipo tiene sus propios datos |

**Disciplina de oro para no desincronizarse:**

> 🔽 **Bajo antes de empezar:** `git pull`
> 🔼 **Subo antes de irme:** `git add .` → `git commit -m "..."` → `git push`

**Configurar un equipo nuevo (resumen):**
1. `git clone https://github.com/carlosgarciavalencia1989/finanzas-app.git`
2. Recrear el venv: `python -m venv venv` + activarlo
3. Instalar librerías: `pip install -r requirements.txt`
4. Crear el `.env` con la contraseña de PostgreSQL **de ese equipo**
5. Crear la base de datos `finanzas` en pgAdmin
6. Arrancar: `uvicorn main:app --reload` (la tabla `usuarios` se crea sola)

**Generar/actualizar `requirements.txt`** (cuando instalas una librería nueva):
```powershell
pip freeze > requirements.txt
```

---

## 6. Explicación de cada archivo (línea por línea)

### 📄 `database.py` — La conexión a la base de datos

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

URL_BASE_DATOS = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(URL_BASE_DATOS)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- **`import os`** → módulo de Python para hablar con el sistema operativo, incluyendo leer variables de entorno. Viene incluido.
- **`from dotenv import load_dotenv`** → trae la función que carga el archivo `.env`.
- **`from sqlalchemy import create_engine`** → la herramienta que crea el "motor" de conexión.
- **`from sqlalchemy.orm import sessionmaker, declarative_base`** → `sessionmaker` fabrica sesiones; `declarative_base` es la base de la que heredan las tablas. Vienen del submódulo `.orm`.
- **`load_dotenv()`** → lee el `.env` y pone sus variables a disposición del programa. Debe correr **antes** de leerlas.
- **`os.getenv("DB_USER")`** (y las siguientes) → recuperan cada dato del `.env`. Así los secretos viven en el `.env` y el código solo los referencia por nombre.
- **`URL_BASE_DATOS = f"postgresql://..."`** → la dirección completa a la base de datos. La `f` la convierte en un **f-string** (cadena formateada) que inserta las variables entre `{llaves}`. Formato: `postgresql://usuario:contraseña@host:puerto/nombre_bd`.
- **`engine = create_engine(URL_BASE_DATOS)`** → crea el **motor**: el objeto central que gestiona la comunicación con PostgreSQL.
- **`SessionLocal = sessionmaker(...)`** → una **fábrica** que produce sesiones (conversaciones temporales con la BD).
  - `bind=engine` → ata la fábrica al motor.
  - `autocommit=False` / `autoflush=False` → los cambios no se guardan automáticamente; tú los confirmas con `commit`. Control total.
- **`Base = declarative_base()`** → la clase "molde madre" de la que heredarán todas las tablas.
- **`get_db()`** → **dependencia** que da una sesión a cada endpoint y la cierra al terminar.
  - `db = SessionLocal()` → produce una sesión nueva.
  - `try / finally` → garantiza que el cierre ocurra pase lo que pase.
  - `yield db` → "presta" la sesión al endpoint y vuelve aquí al terminar.
  - `db.close()` → cierra la sesión, liberando la conexión.

---

### 📄 `models.py` — La tabla de usuarios

```python
from sqlalchemy import Column, Integer, String
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
```

- **`from sqlalchemy import Column, Integer, String`** → `Column` define una columna; `Integer` y `String` son tipos de dato (número entero y texto).
- **`from database import Base`** → trae la "molde madre" para que la tabla herede de ella. (Ejemplo de cómo los archivos se conectan entre sí.)
- **`class Usuario(Base):`** → una clase que hereda de `Base` = una tabla. Nombre en singular y mayúscula por convención.
- **`__tablename__ = "usuarios"`** → el nombre **real** de la tabla en PostgreSQL (plural, minúscula). Hace el puente entre el nombre de la clase y el de la tabla.
- **Columnas** — opciones dentro de `Column(...)`:
  - `primary_key=True` → llave primaria: el identificador único de cada fila (PostgreSQL lo autonumera 1, 2, 3…).
  - `index=True` → crea un índice para búsquedas rápidas (útil en `id` y `email`).
  - `nullable=False` → la columna no puede quedar vacía.
  - `unique=True` → el valor no se puede repetir (dos usuarios no pueden tener el mismo email).
  - `hashed_password` → guarda la contraseña **hasheada**, nunca en texto plano. El nombre lo recuerda.

**Modelo `Transaccion` (agregado en Sesión 10):** la tabla de ingresos y gastos, conectada a `usuarios`.

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    # ... columnas de arriba ...
    transacciones = relationship("Transaccion", back_populates="usuario")


class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    monto = Column(Float, nullable=False)
    tipo = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="transacciones")
```

- **`Float`** → tipo para números con decimales (el monto puede ser `45000.50`).
- **`DateTime`** → tipo para guardar fecha y hora.
- **`descripcion` con `nullable=True`** → único campo opcional (una transacción puede no tener descripción).
- **`fecha` con `server_default=func.now()`** → la base de datos pone la fecha/hora automáticamente al crear el registro.
- **`usuario_id = Column(Integer, ForeignKey("usuarios.id"))`** → **la llave foránea.** Guarda el `id` del usuario dueño y le dice a la BD que ese número es una referencia real a la tabla `usuarios`. Es lo que hace la app multiusuario.
- **`relationship(...)` + `back_populates`** → atajos de Python para navegar la conexión: `mi_usuario.transacciones` (todas las de un usuario) y `mi_transaccion.usuario` (el dueño de una transacción). No crean columnas nuevas; `back_populates` conecta las dos puntas.

> **ForeignKey vs. relationship:** la `ForeignKey` es la conexión física (columna real en la BD); `relationship` es solo comodidad de código para navegarla.

---

### 📄 `security.py` — Contraseñas y tokens

```python
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hashear_password(password: str) -> str:
    return password_hash.hash(password)


def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    return password_hash.verify(password_plano, password_hasheado)


def crear_access_token(data: dict) -> str:
    to_encode = data.copy()
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expira})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
```

**Importaciones:**
- **`from datetime import datetime, timedelta, timezone`** → manejo de fechas/horas para calcular cuándo expira el token. `datetime` = un momento, `timedelta` = una duración, `timezone` = zona horaria.
- **`import jwt`** → la librería PyJWT (se instala como `pyjwt` pero se importa como `jwt`).
- **`from pwdlib import PasswordHash`** → la herramienta de hasheo.

**Configuración:**
- **`password_hash = PasswordHash.recommended()`** → objeto de hasheo con los ajustes recomendados (usa Argon2 por debajo).
- **`SECRET_KEY = os.getenv("SECRET_KEY")`** → la clave secreta con la que se firman los tokens (vive en el `.env`).
- **`ALGORITHM = "HS256"`** → el algoritmo estándar de firma de JWT.
- **`ACCESS_TOKEN_EXPIRE_MINUTES = 30`** → cuánto dura un token antes de caducar (seguridad).

**Funciones:**
- **`hashear_password(password)`** → convierte una contraseña en texto plano en un hash irreversible (`$argon2id$...`). El `: str` y `-> str` son anotaciones de tipo (entra texto, sale texto).
- **`verificar_password(plano, hasheado)`** → compara la contraseña que el usuario escribe con el hash guardado. Devuelve `True`/`False`. Nunca ve la contraseña original.
- **`crear_access_token(data)`** → la "fábrica de manillas":
  - `to_encode = data.copy()` → copia el diccionario para no modificar el original.
  - `expira = datetime.now(timezone.utc) + timedelta(...)` → calcula el momento de expiración (ahora + 30 min).
  - `to_encode.update({"exp": expira})` → agrega la expiración. `exp` es un nombre estándar de JWT que la librería reconoce sola.
  - `jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)` → genera el token firmado (`xxxxx.yyyyy.zzzzz`). La firma con la clave secreta lo hace imposible de falsificar.

**Función `verificar_access_token` (agregada en Sesión 9):** la contraria de `crear_access_token` — lee un token y valida que sea auténtico.

```python
from jwt.exceptions import InvalidTokenError


def verificar_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = payload.get("sub")
        if usuario_id is None:
            return None
        return usuario_id
    except InvalidTokenError:
        return None
```

- **`InvalidTokenError`** → el error que lanza la librería si un token es inválido (firma alterada, expirado…). Lo importamos para atraparlo.
- **`jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])`** → el corazón: verifica la firma con tu clave, comprueba que no haya expirado, y si todo está bien devuelve el payload. Nota: al decodificar es `algorithms=[...]` (plural, en lista), al crear era `algorithm=` (singular).
- **`payload.get("sub")`** → saca el `id` del usuario del token. Usa `.get()` (no `["sub"]`) para devolver `None` en vez de reventar si falta.
- **`try / except`** → si el token es malo, devuelve `None` sin tumbar el servidor.
- **En resumen:** devuelve el `id` del usuario si el token es válido, o `None` si no. Es el "portero que revisa la manilla".

---

### 📄 `schemas.py` — Formas de datos de la API

```python
from pydantic import BaseModel, EmailStr, ConfigDict


class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
```

**Concepto clave:** un "esquema" (Pydantic) describe la **forma de los datos que viajan por la API**, distinto del "modelo" (`models.py`) que describe **cómo se guardan** en la BD. Un mismo usuario tiene tres caras: lo que entra, lo que se guarda, y lo que sale.

- **`BaseModel`** → clase base de la que heredan los esquemas (da validación automática).
- **`EmailStr`** → tipo que valida que el texto sea un email con formato correcto.
- **`ConfigDict`** → herramienta para configurar el comportamiento de un esquema.

**`UsuarioCrear`** (lo que ENTRA al registrarse): `nombre`, `email`, `password` (en texto plano; el endpoint lo hashea).

**`UsuarioRespuesta`** (lo que SALE): `id`, `nombre`, `email`. **NO incluye la contraseña** (ni plana ni hasheada).
- `model_config = ConfigDict(from_attributes=True)` → permite a Pydantic leer datos directamente de un objeto SQLAlchemy (no solo de un diccionario). Es el puente objeto-tabla → respuesta-API.

**`UsuarioLogin`** (lo que ENTRA al iniciar sesión): solo `email` y `password` (no pide nombre).

**`Token`** (lo que SALE del login): `access_token` (el token) y `token_type` (`"bearer"`).

**Esquemas de transacciones (agregados en Sesión 10):**

```python
from datetime import datetime


class TransaccionCrear(BaseModel):
    monto: float
    tipo: str
    categoria: str
    descripcion: str | None = None


class TransaccionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monto: float
    tipo: str
    categoria: str
    descripcion: str | None
    fecha: datetime
    usuario_id: int
```

- **`TransaccionCrear`** (lo que ENTRA): `monto`, `tipo`, `categoria`, `descripcion`. **NO incluye `usuario_id` ni `fecha`** → el `usuario_id` se saca del token (seguridad: nadie crea transacciones a nombre de otro), y la `fecha` la pone la BD sola.
- **`descripcion: str | None = None`** → campo opcional. El `| None` significa "texto **o** nada"; el `= None` es el valor por defecto si no se envía.
- **`TransaccionRespuesta`** (lo que SALE): incluye todo, incluidos `id`, `fecha` y `usuario_id`, porque son datos que el usuario debe ver.
- **Cuidado con las tildes:** el campo se llama `descripcion` **sin tilde** en los tres archivos (modelo, esquema, endpoint). Escribirlo con tilde causa errores. Regla: nombres internos sin tildes; el texto que ve el usuario sí puede llevarlas.

---

### 📄 `main.py` — La app y los endpoints

```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
import schemas
from security import hashear_password, verificar_password, crear_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def inicio():
    return {"Mensaje": "Hola, mi backend funciona"}


@app.post("/registro", response_model=schemas.UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    password_hasheado = hashear_password(usuario.password)

    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        hashed_password=password_hasheado
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@app.post("/login", response_model=schemas.Token)
def login(credenciales: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == credenciales.email).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    if not verificar_password(credenciales.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    access_token = crear_access_token(data={"sub": str(usuario.id)})

    return {"access_token": access_token, "token_type": "bearer"}
```

**Importaciones y arranque:**
- **`from fastapi import FastAPI, Depends, HTTPException, status`** → `Depends` conecta dependencias; `HTTPException` devuelve errores controlados; `status` da nombres legibles a los códigos HTTP.
- **`from sqlalchemy.orm import Session`** → el tipo de una sesión, para anotar el parámetro `db`.
- **`Base.metadata.create_all(bind=engine)`** → crea en PostgreSQL todas las tablas que `Base` conoce. Por eso hay que `import models` (para que `Base` "se entere" de la tabla `Usuario`). Si la tabla ya existe, no hace nada.
- **`app = FastAPI()`** → crea la aplicación.

**Endpoint `GET /`** → un "hola mundo" que devuelve un diccionario (FastAPI lo convierte a JSON).

**Endpoint `POST /registro`:**
- `@app.post` → POST porque *crea* datos.
- `response_model=schemas.UsuarioRespuesta` → garantiza que la respuesta nunca incluya la contraseña (filtrado automático).
- `status_code=status.HTTP_201_CREATED` → devuelve `201` ("Creado") si todo sale bien.
- `usuario: schemas.UsuarioCrear` → FastAPI valida la entrada contra el esquema.
- `db: Session = Depends(get_db)` → inyecta una sesión de BD vía la dependencia.
- Lógica: (1) busca si el email ya existe → si sí, error `400`; (2) hashea la contraseña; (3) crea el objeto `Usuario`; (4) `db.add` + `db.commit` + `db.refresh` (prepara, confirma, y recarga para traer el `id`); (5) devuelve el usuario.

**Endpoint `POST /login`:**
- `response_model=schemas.Token` → la respuesta tendrá la forma `access_token` + `token_type`.
- Lógica: (1) busca el usuario por email; (2) si no existe → `401`; (3) verifica la contraseña con `verificar_password` → si falla, `401`; (4) crea el token con el `id` del usuario dentro (`sub`); (5) devuelve el token.
- **Detalle de seguridad:** el mensaje de error es vago a propósito ("Email o contraseña incorrectos"), sin decir cuál falló, para no revelar qué emails están registrados.
- `str(usuario.id)` → el `id` se convierte a texto porque el estándar JWT espera que `sub` sea un string.

**El "portero" `obtener_usuario_actual` y el endpoint protegido `/perfil` (Sesión 9):**

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    token = credenciales.credentials
    usuario_id = verificar_access_token(token)
    if usuario_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(usuario_id)).first()
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return usuario


@app.get("/perfil", response_model=schemas.UsuarioRespuesta)
def perfil(usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual
```

- **`HTTPBearer`** → extrae el token de la cabecera `Authorization: Bearer <token>` automáticamente. Se crea una vez como `security_scheme`.
- **`obtener_usuario_actual`** → **el "portero".** Es una dependencia que: (1) saca el token, (2) lo verifica con `verificar_access_token`, (3) busca al usuario en la BD, y (4) lo devuelve. Si algo falla, corta con `401`.
- **`int(usuario_id)`** → el `id` venía como texto en el token; se convierte a número para comparar con la columna `id`.
- **El endpoint `/perfil`** → al poner `Depends(obtener_usuario_actual)`, queda **protegido**: solo se ejecuta si el token es válido. Esa sola línea blinda cualquier endpoint. Se reutiliza en todos los endpoints protegidos.

**El módulo de transacciones — CRUD completo (Sesiones 10-11):**

Cuatro endpoints, todos protegidos con `Depends(obtener_usuario_actual)`:

```python
# CREAR (C)
@app.post("/transacciones", response_model=schemas.TransaccionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_transaccion(transaccion: schemas.TransaccionCrear, db: Session = Depends(get_db),
                      usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    nueva_transaccion = models.Transaccion(
        monto=transaccion.monto, tipo=transaccion.tipo, categoria=transaccion.categoria,
        descripcion=transaccion.descripcion, usuario_id=usuario_actual.id)
    db.add(nueva_transaccion); db.commit(); db.refresh(nueva_transaccion)
    return nueva_transaccion

# LISTAR (R)
@app.get("/transacciones", response_model=list[schemas.TransaccionRespuesta])
def listar_transacciones(db: Session = Depends(get_db),
                         usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == usuario_actual.id).all()

# EDITAR (U)
@app.put("/transacciones/{transaccion_id}", response_model=schemas.TransaccionRespuesta)
def actualizar_transaccion(transaccion_id: int, transaccion: schemas.TransaccionCrear,
                           db: Session = Depends(get_db),
                           usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    transaccion_db = db.query(models.Transaccion).filter(
        models.Transaccion.id == transaccion_id,
        models.Transaccion.usuario_id == usuario_actual.id).first()
    if transaccion_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
    transaccion_db.monto = transaccion.monto
    transaccion_db.tipo = transaccion.tipo
    transaccion_db.categoria = transaccion.categoria
    transaccion_db.descripcion = transaccion.descripcion
    db.commit(); db.refresh(transaccion_db)
    return transaccion_db

# BORRAR (D)
@app.delete("/transacciones/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db),
                         usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    transaccion_db = db.query(models.Transaccion).filter(
        models.Transaccion.id == transaccion_id,
        models.Transaccion.usuario_id == usuario_actual.id).first()
    if transaccion_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
    db.delete(transaccion_db); db.commit()
    return None
```

Claves de cada uno:
- **Crear (POST):** el `usuario_id` se toma de `usuario_actual.id` (del token), **no** del cuerpo → seguridad. Usa `add` + `commit` + `refresh`.
- **Listar (GET):** `response_model=list[...]` porque devuelve **varias**. El `.filter(usuario_id == usuario_actual.id)` hace que cada quien vea **solo las suyas**. `.all()` trae todas.
- **Editar (PUT):** ruta con **parámetro** `{transaccion_id}` (capturado por el parámetro `transaccion_id: int`). **Doble filtro** (`id` + `usuario_id`) por seguridad. Reasigna campos y hace `commit` + `refresh` (sin `add`, porque ya existía). Si no la encuentra → `404`.
- **Borrar (DELETE):** mismo doble filtro. `db.delete(...)` + `commit`. Devuelve `204` (borrado sin contenido).

> **Patrón reutilizable:** cualquier endpoint protegido solo necesita `usuario_actual = Depends(obtener_usuario_actual)`. Y para "recursos que pertenecen a un usuario", el doble filtro (`id` del recurso + `usuario_id` del token) es la clave de seguridad. Este mismo molde servirá para presupuestos, metas y análisis.

---

## 7. Conceptos clave aprendidos

**Framework** — un kit de herramientas y estructura ya hechos para construir algo sin empezar de cero. FastAPI es un framework.

**API** — el "mesero" que comunica dos programas (frontend ↔ backend).

**Endpoint** — una ruta de la API (ej. `/registro`) que ejecuta una función cuando se le llama.

**Métodos HTTP** — `GET` para *leer* datos, `POST` para *crear*, `PUT` para *actualizar/modificar*, `DELETE` para *borrar*. La ruta + el método definen el endpoint (misma dirección con distinto método = endpoint distinto).

**Parámetro en la ruta** — un hueco variable en la dirección, escrito entre llaves: `/transacciones/{transaccion_id}`. Sirve para apuntar a **un recurso específico** (la transacción 5, la 12…). FastAPI captura ese valor en el parámetro de la función del mismo nombre.

**CRUD** — las cuatro operaciones básicas sobre datos: **C**reate (crear), **R**ead (leer), **U**pdate (actualizar), **D**elete (borrar). Cada una es un endpoint con su método HTTP.

**Códigos de estado HTTP:**
- `200` OK · `201` Created (creado con éxito) · `204` No Content (éxito sin nada que devolver, ej. al borrar)
- `400` Bad Request (petición incorrecta) · `401` Unauthorized (credenciales/token inválidos) · `404` Not Found (recurso no existe)
- `422` Validation Error (datos con formato inválido) · `500` error interno del servidor (fallo en el código; el detalle está en la terminal)

**ORM (Object-Relational Mapping)** — puente que permite trabajar con clases de Python en lugar de escribir SQL a mano. SQLAlchemy es el ORM.

**Modelo vs. Esquema** — el modelo (`models.py`) define cómo se *guardan* los datos; el esquema (`schemas.py`) define cómo *viajan* por la API.

**Hasheo de contraseñas** — transformación de una sola vía e irreversible. Nunca se guarda la contraseña real; solo su hash. Se verifica volviendo a hashear y comparando. `pwdlib` con Argon2 lo maneja, incluido el "salt" (texto aleatorio para que claves iguales tengan hashes distintos).

**JWT (JSON Web Token)** — un "pase" firmado que el servidor entrega tras verificar la identidad una vez. En cada petición futura, el usuario lo presenta en lugar de la contraseña (como la manilla de un concierto). Tiene tres partes (`header.payload.firma`). La firma se genera con una clave secreta y hace el token imposible de falsificar. Los tokens caducan por seguridad.

**Endpoint protegido** — una ruta que solo responde si se presenta un token válido. Se logra agregando la dependencia del "portero" (`obtener_usuario_actual`). Si el token falta o es inválido, el endpoint nunca se ejecuta.

**Llave foránea (ForeignKey)** — una columna que guarda el `id` de un registro de otra tabla, creando una conexión real entre ambas (ej. cada transacción guarda el `usuario_id` de su dueño). Es lo que hace posible una app multiusuario: cada dato "pertenece" a alguien.

**relationship (SQLAlchemy)** — atajo de código para navegar una llave foránea sin escribir consultas manuales (ej. `usuario.transacciones` o `transaccion.usuario`). No crea columnas; solo da comodidad. `back_populates` conecta las dos puntas de la relación.

**Doble filtro de seguridad** — al buscar un recurso que pertenece a un usuario (editar/borrar una transacción), se filtra por el `id` del recurso **y** por el `usuario_id` del token. Así nadie puede tocar datos de otro usuario aunque conozca el `id`.

**Variables de entorno (`.env`)** — los secretos (contraseñas, claves) viven separados del código, en un archivo que Git ignora. El código los referencia por nombre con `os.getenv()`.

**Dependencia (FastAPI)** — una función (como `get_db`) que FastAPI ejecuta automáticamente antes de un endpoint para proveerle algo (una sesión de BD).

**Buenas prácticas adoptadas:**
- Separar responsabilidades por archivo.
- No repetirse (funciones reutilizables como las de `security.py`).
- Verificar antes de subir (`git status` para no filtrar el `.env`).
- Copia de seguridad antes de tocar archivos de configuración.
- Leer los errores de abajo hacia arriba (la última línea suele decir el qué y el dónde).

---

## 8. Comandos de referencia rápida

**Entorno virtual:**
```powershell
python -m venv venv            # crear
.\venv\Scripts\Activate.ps1    # activar
deactivate                     # desactivar
```

**Servidor:**
```powershell
uvicorn main:app --reload      # arrancar (Ctrl+C para detener)
```

**Librerías:**
```powershell
pip install -r requirements.txt   # instalar todo desde la lista
pip freeze > requirements.txt     # regenerar la lista
```

**Git (rutina diaria):**
```powershell
git pull                          # bajar cambios (al empezar)
git status                        # ver qué cambió
git add .                         # preparar cambios
git commit -m "mensaje"           # tomar la foto
git push                          # subir (al terminar)
git log --oneline                 # ver historial de commits
```

**URLs útiles (con el servidor corriendo):**
- `http://127.0.0.1:8000` → la app
- `http://127.0.0.1:8000/docs` → documentación interactiva (Swagger UI)

---

## 9. Estado actual y próximos pasos

### ✅ Completado
- [x] Entorno de desarrollo (Python, Node, Git, VS Code, PostgreSQL) en dos equipos
- [x] Repositorio Git + GitHub conectado
- [x] Conexión FastAPI ↔ PostgreSQL (SQLAlchemy + psycopg2)
- [x] Tabla `usuarios` creada vía ORM
- [x] Registro de usuarios con hasheo de contraseñas (Argon2)
- [x] Manejo de secretos con `.env`
- [x] Login con generación de tokens JWT
- [x] Migración del proyecto a un segundo equipo
- [x] **Autenticación completa** → verificación de token + endpoint protegido `/perfil`
- [x] **Módulo de transacciones — CRUD completo** (crear, listar, editar, borrar) con relación a usuarios y seguridad multiusuario

### 🔨 Próximos pasos (backend)
1. **Presupuestos** → límites por categoría + lógica de alertas (80% / sobre el límite). *Mediano.*
2. **Metas de ahorro** → calculadora de fondo de emergencia + cálculo de cuotas. *Mediano.*
3. **Análisis** → datos para las gráficas (gasto por mes / por categoría). *Pequeño-mediano.*

> **Progreso estimado del backend: ~60-65%** — las dos piezas más difíciles (autenticación completa y el CRUD de transacciones) ya están hechas. Los módulos restantes reutilizan el mismo patrón (modelo → esquema → endpoints protegidos con doble filtro), así que el ritmo es más ágil.

### 🎨 Frontend (más adelante)
- Decidir framework: React web (PWA) vs. React Native / Expo (móvil nativo). El diseño hi-fi del equipo sugiere móvil nativo.

---

## 10. Registro de sesiones

> Aquí anotamos qué se hizo en cada sesión, para tener memoria del avance.

### Sesiones 1-3 — Configuración del entorno
- Instalación de herramientas base, configuración de Git.
- Creación del repo `finanzas-app`, primer commit.
- Entorno virtual + `.gitignore`.

### Sesión 4 — Primer endpoint FastAPI
- Instalación de FastAPI + Uvicorn.
- `main.py` con el endpoint `GET /` ("Hola, mi backend funciona").
- Descubrimiento de la documentación interactiva (`/docs`).

### Sesión 5 — Conexión a PostgreSQL
- Instalación de PostgreSQL + creación de la base `finanzas`.
- Instalación de SQLAlchemy + psycopg2.
- `database.py` (motor, sesión, `get_db`).
- `models.py` con la tabla `Usuario`.

### Sesión 6 — Registro de usuarios
- Hasheo de contraseñas con `pwdlib[argon2]` → `security.py`.
- Esquemas Pydantic (`UsuarioCrear`, `UsuarioRespuesta`) → `schemas.py`.
- Endpoint `POST /registro` + primer usuario creado (201).
- Manejo de secretos: `.env` + `python-dotenv`.
- Commit: "Agregar conexión a PostgreSQL y registro de usuarios con hasheo".

### Sesión 7 — Migración al segundo equipo (PC de mesa)
- Generación de `requirements.txt`.
- Clonado del proyecto, recreación del venv, instalación desde `requirements.txt`.
- Restablecimiento de la contraseña olvidada de PostgreSQL (editando `pg_hba.conf` a modo `trust` y revirtiendo).
- Recreación del `.env` y la base `finanzas` en el equipo nuevo.

### Sesión 8 — Login con JWT
- Concepto de tokens JWT (analogía de la manilla del concierto).
- Instalación de PyJWT + generación de `SECRET_KEY`.
- Función `crear_access_token` en `security.py`.
- Esquemas `UsuarioLogin` y `Token`.
- Endpoint `POST /login` + primer token generado (200).
- Creación de este documento de documentación.
- Agregado del Anexo A (guía de instalación desde cero).

### Sesión 9 — Verificación de token y endpoint protegido
- Función `verificar_access_token` en `security.py` (lee y valida un token).
- El "portero" `obtener_usuario_actual` en `main.py` (dependencia que extrae el token, lo verifica y devuelve el usuario).
- Endpoint protegido `GET /perfil` + botón "Authorize" en `/docs`.
- **Autenticación cerrada por completo.**
- Errores resueltos leyendo el mensaje: `NameError` (faltaba `security_scheme`) y una importación incompleta.

### Sesión 10 — Módulo de transacciones (crear + listar)
- Concepto de CRUD y de relaciones entre tablas.
- Modelo `Transaccion` con llave foránea (`usuario_id`) y `relationship`.
- Esquemas `TransaccionCrear` y `TransaccionRespuesta`.
- Endpoints `POST /transacciones` (crear) y `GET /transacciones` (listar), protegidos y con filtro por usuario.
- Error `500` resuelto leyendo el Traceback (campo `descripcion` con tilde en el esquema).

### Sesión 11 — CRUD de transacciones completo
- Concepto de parámetros en la ruta (`/transacciones/{transaccion_id}`).
- Endpoint `PUT /transacciones/{id}` (editar) con doble filtro de seguridad.
- Endpoint `DELETE /transacciones/{id}` (borrar) con código `204`.
- **CRUD de transacciones completo (las cuatro operaciones).**
- Configuración de identidad de Git en el PC de mesa (`git config`).
- Actualización de este documento con todo lo de las sesiones 9-11.

---

## Anexo A — Instalación de herramientas desde cero

Guía paso a paso para dejar un equipo Windows completamente listo, partiendo de cero. Útil para configurar un tercer equipo o para consulta futura. Instala en **este orden**.

> **Consejo general:** después de instalar cada herramienta, **cierra y vuelve a abrir** cualquier terminal o VS Code que tuvieras abierto, para que reconozca el nuevo programa. Muchos "no se reconoce el comando" se deben a no haber reabierto la terminal.

### A.1 — Python

Python es el lenguaje en el que está escrito todo el backend.

1. Entra a **https://www.python.org/downloads/**
2. Descarga la última versión estable (**Python 3.14.x**). El botón amarillo grande suele ofrecer la correcta para Windows.
3. Ejecuta el instalador `.exe`.
4. **⚠️ EL PASO MÁS IMPORTANTE:** en la primera pantalla del instalador, marca la casilla de abajo **"Add python.exe to PATH"** (Agregar Python al PATH) **antes** de continuar. Sin esto, el comando `python` no funcionará en la terminal y tendrás que reinstalar.
5. Haz clic en **"Install Now"** y espera a que termine.
6. **Verifica** abriendo una terminal nueva:
   ```powershell
   python --version
   ```
   Debe responder `Python 3.14.x`.

### A.2 — Node.js

Node.js se necesita para el frontend futuro (React) y sus herramientas.

1. Entra a **https://nodejs.org/**
2. Descarga la versión **LTS** (Long Term Support). En 2026 es **Node.js 24 LTS** — es la recomendada para proyectos nuevos por su estabilidad y soporte largo. **No** descargues la "Current" (26), que es para experimentar.
3. Ejecuta el instalador `.msi`.
4. Da **Next** en todas las pantallas aceptando los valores por defecto (el instalador de Node agrega el PATH automáticamente, no tienes que marcar nada especial). Acepta la licencia.
5. En una pantalla puede ofrecerte instalar "Tools for Native Modules" — puedes **dejarla sin marcar**; no la necesitas para este proyecto.
6. **Verifica** en una terminal nueva:
   ```powershell
   node --version    # debe mostrar v24.x.x
   npm --version     # debe mostrar un número (npm viene incluido con Node)
   ```
   > Si `npm` da un error sobre ejecución de scripts, corre el comando de la sección "Arreglar PowerShell" y vuelve a probar.

### A.3 — Git

Git es el control de versiones; GitHub es donde se guarda el repositorio en la nube.

1. Entra a **https://git-scm.com/downloads** y descarga la versión para Windows.
2. Ejecuta el instalador. Tiene **muchas** pantallas de opciones; para un principiante, **acepta todos los valores por defecto** dando Next. Los defaults de Git son sensatos.
3. Un default útil que ya viene marcado: el editor por defecto suele ser Vim; si quieres, puedes cambiarlo a VS Code en esa pantalla, pero no es obligatorio.
4. **Verifica** en una terminal nueva:
   ```powershell
   git --version
   ```
   Debe responder `git version 2.xx.x`.
5. **Configura tu identidad** (una sola vez por equipo):
   ```powershell
   git config --global user.name "Tu Nombre"
   git config --global user.email "tucorreo@ejemplo.com"
   ```
   > Usa el mismo correo con el que creas/tienes tu cuenta de GitHub.

**Crear la cuenta de GitHub** (si no la tienes): entra a **https://github.com**, regístrate con tu correo, y verifícalo. La primera vez que hagas un `git push` o `git clone` desde un equipo, se abrirá el navegador para que inicies sesión y autorices — es normal y solo pasa una vez por equipo.

### A.4 — VS Code

VS Code es el editor donde escribes el código.

1. Entra a **https://code.visualstudio.com/** y descarga la versión para Windows.
2. Ejecuta el instalador. En la pantalla de "Tareas adicionales", conviene marcar:
   - ✅ **"Agregar al PATH"** (suele venir marcado) → te permite abrir carpetas con `code .` desde la terminal.
   - ✅ **"Agregar acción "Abrir con Code" al menú contextual"** (opcional pero cómodo) → te deja abrir carpetas con clic derecho.
3. Termina la instalación y ábrelo.
4. **Extensión recomendada:** dentro de VS Code, ve al panel de extensiones (ícono de cuadritos a la izquierda, o `Ctrl+Shift+X`), busca **"Python"** (la de Microsoft) e instálala. Da resaltado de sintaxis, autocompletado y detección del entorno virtual.
5. **Verifica** en una terminal nueva:
   ```powershell
   code --version
   ```

### A.5 — PostgreSQL + pgAdmin

PostgreSQL es el motor de base de datos; pgAdmin es su interfaz visual.

1. Entra a **https://www.postgresql.org/download/windows/** y haz clic en "Download the installer" (instalador oficial de EDB).
2. Descarga la versión estable más reciente (**PostgreSQL 18** en 2026). **No** descargues versiones "Beta".
3. Ejecuta el `.exe`. Ve dando **Next**, pero presta atención a estas cuatro pantallas:
   - **Select Components:** marca ✅ PostgreSQL Server, ✅ pgAdmin 4, ✅ Command Line Tools. Puedes desmarcar Stack Builder.
   - **Password (⚠️ la más importante):** define la contraseña del superusuario `postgres` y **anótala en un lugar seguro de inmediato**. La necesitarás para pgAdmin y para el `.env`. *(Olvidarla obliga a un proceso de recuperación editando `pg_hba.conf` — ver Sesión 7.)*
   - **Port:** déjalo en **5432** (el estándar).
   - **Locale:** deja "Default locale".
4. Termina la instalación (tarda unos minutos).
5. **Verifica:** abre **pgAdmin**, conéctate a tu servidor con la contraseña de `postgres`, y confirma que entras.

> **Recomendación multi-equipo:** usa la **misma contraseña de `postgres`** en todos tus equipos. Así el `.env` es casi idéntico y te evitas confusiones.

### Orden de verificación final

Con todo instalado, una terminal nueva debe responder a los cuatro comandos:
```powershell
python --version    # Python 3.14.x
node --version      # v24.x.x
git --version       # git version 2.xx.x
code --version      # 1.xxx.x
```
Y pgAdmin debe permitirte conectar al servidor PostgreSQL. Si todo eso funciona, el equipo está listo para clonar el proyecto (ver sección 5).

---

*Fin del documento. Se continuará en la próxima sesión.* 🚀
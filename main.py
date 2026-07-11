from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
import schemas
from security import hashear_password, verificar_password, crear_access_token, verificar_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI()

security_scheme = HTTPBearer()

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

def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    token = credenciales.credentials
    usuario_id = verificar_access_token(token)

    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(usuario_id)).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    return usuario


@app.get("/perfil", response_model=schemas.UsuarioRespuesta)
def perfil(usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

@app.post("/transacciones", response_model=schemas.TransaccionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_transaccion(
    transaccion: schemas.TransaccionCrear,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    nueva_transaccion = models.Transaccion(
        monto= transaccion.monto,
        tipo=transaccion.tipo,
        categoria=transaccion.categoria,
        descripcion=transaccion.descripcion,
        usuario_id=usuario_actual.id
    )

    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)

    return nueva_transaccion


@app.get("/transacciones", response_model=list[schemas.TransaccionRespuesta])
def listar_transacciones(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    transacciones = db.query(models.Transaccion).filter(
        models.Transaccion.usuario_id == usuario_actual.id
    ).all()

    return transacciones

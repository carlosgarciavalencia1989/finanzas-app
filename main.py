from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
import schemas
from security import hashear_password, verificar_password, crear_access_token, verificar_access_token
from sqlalchemy import func

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

def calcular_estado_presupuesto(presupuesto: models.Presupuesto, db: Session):
    gastado = db.query(func.sum(models.Transaccion.monto)).filter(
        models.Transaccion.usuario_id == presupuesto.usuario_id,
        models.Transaccion.categoria == presupuesto.categoria,
        models.Transaccion.tipo == "gasto"
    ).scalar()

    if gastado is None:
        gastado = 0.0

    if presupuesto.limite > 0:
        porcentaje = round(gastado / presupuesto.limite * 100)
    else:
        porcentaje = 0

    if porcentaje >= 100:
        estado = "excedido"
    elif porcentaje >= 80:
        estado = "cerca"
    else:
        estado = "ok"
    
    return {
        "id": presupuesto.id,
        "categoria": presupuesto.categoria,
        "limite": presupuesto.limite,
        "usuario_id": presupuesto.usuario_id,
        "gastado": gastado,
        "porcentaje": porcentaje,
        "estado": estado
    }

def calcular_estado_meta(meta: models.Meta):
    if meta.meses > 0:
        cuota_mensual = meta.objetivo / meta.meses
    else:
        cuota_mensual = 0.0

    if meta.objetivo > 0:
        porcentaje = round(meta.ahorrado / meta.objetivo * 100)
    else:
        porcentaje = 0

    falta = meta.objetivo - meta.ahorrado

    if falta < 0:
        falta = 0.0

    return {
        "id": meta.id,
        "nombre": meta.nombre,
        "objetivo": meta.objetivo,
        "meses": meta.meses,
        "ahorrado": meta.ahorrado,
        "usuario_id": meta.usuario_id,
        "cuota_mensual": cuota_mensual,
        "porcentaje": porcentaje,
        "falta": falta
    }


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


@app.put("/transacciones/{transaccion_id}", response_model=schemas.TransaccionRespuesta)
def actualizar_transaccion(
    transaccion_id: int,
    transaccion: schemas.TransaccionCrear,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    transaccion_db = db.query(models.Transaccion).filter(
        models.Transaccion.id == transaccion_id,
        models.Transaccion.usuario_id == usuario_actual.id
    ).first()

    if transaccion_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada"
        )

    transaccion_db.monto = transaccion.monto
    transaccion_db.tipo = transaccion.tipo
    transaccion_db.categoria = transaccion.categoria
    transaccion_db.descripcion = transaccion.descripcion

    db.commit()
    db.refresh(transaccion_db)

    return transaccion_db


@app.delete("/transacciones/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(
    transaccion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    transaccion_db = db.query(models.Transaccion).filter(
        models.Transaccion.id == transaccion_id,
        models.Transaccion.usuario_id == usuario_actual.id
    ).first()

    if transaccion_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada"
        )

    db.delete(transaccion_db)
    db.commit()

    return None

@app.post("/presupuestos", response_model=schemas.PresupuestoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_presupuesto(
    presupuesto: schemas.PresupuestoCrear,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    nuevo_presupuesto = models.Presupuesto(
        categoria=presupuesto.categoria,
        limite=presupuesto.limite,
        usuario_id=usuario_actual.id
    )

    db.add(nuevo_presupuesto)
    db.commit()
    db.refresh(nuevo_presupuesto)

    return calcular_estado_presupuesto(nuevo_presupuesto, db)

@app.get("/presupuestos", response_model=list[schemas.PresupuestoRespuesta])
def listar_presupuestos(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    presupuestos = db.query(models.Presupuesto).filter(
        models.Presupuesto.usuario_id == usuario_actual.id
    ).all()

    return [calcular_estado_presupuesto(p, db) for p in presupuestos]

@app.put("/presupuestos/{presupuesto_id}", response_model=schemas.PresupuestoRespuesta)
def actualizar_presupuesto(
    presupuesto_id: int,
    presupuesto: schemas.PresupuestoCrear,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    presupuesto_db = db.query(models.Presupuesto).filter(
        models.Presupuesto.id == presupuesto_id,
        models.Presupuesto.usuario_id == usuario_actual.id
    ).first()

    if presupuesto_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado"
        )

    presupuesto_db.categoria = presupuesto.categoria
    presupuesto_db.limite = presupuesto.limite

    db.commit()
    db.refresh(presupuesto_db)

    return calcular_estado_presupuesto(presupuesto_db, db)

@app.delete("/presupuestos/{presupuesto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_presupuesto(
    presupuesto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    presupuesto_db = db.query(models.Presupuesto).filter(
        models.Presupuesto.id == presupuesto_id,
        models.Presupuesto.usuario_id == usuario_actual.id
    ).first()

    if presupuesto_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado"
        )

    db.delete(presupuesto_db)
    db.commit()

    return None

@app.post("/metas", response_model=schemas.MetaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_meta(
    meta: schemas.MetaCrear,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    nueva_meta = models.Meta(
        nombre=meta.nombre,
        objetivo=meta.objetivo,
        meses=meta.meses,
        usuario_id=usuario_actual.id
    )

    db.add(nueva_meta)
    db.commit()
    db.refresh(nueva_meta)

    return calcular_estado_meta(nueva_meta)


@app.get("/metas", response_model=list[schemas.MetaRespuesta])
def listar_metas(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    metas = db.query(models.Meta).filter(
        models.Meta.usuario_id == usuario_actual.id
    ).all()

    return [calcular_estado_meta(m) for m in metas]
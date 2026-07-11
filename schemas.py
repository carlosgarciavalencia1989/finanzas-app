from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

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

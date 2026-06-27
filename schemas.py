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

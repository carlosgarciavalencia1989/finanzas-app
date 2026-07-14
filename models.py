from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    transacciones = relationship("Transaccion", back_populates="usuario")
    presupuestos = relationship("Presupuesto", back_populates="usuario")

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

class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, nullable=False)
    limite = Column(Float, nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="presupuestos")
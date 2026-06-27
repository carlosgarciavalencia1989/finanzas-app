from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hashear_password(password: str) -> str:
    return password_hash.hash(password)

def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    return password_hash.verify(password_plano, password_hasheado)
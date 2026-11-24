import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Secretos leídos EXCLUSIVAMENTE desde variables de entorno del servidor cloud
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cambiar-en-produccion-env-secreto")
ALGORITHM = "HS256"

USUARIOS_ENV = {
    os.getenv("OPERADOR_USER", "operador_ica"): {
        "password": os.getenv("OPERADOR_PASS", "OpIca2026!"),
        "rol": "OPERADOR",
        "nombre": "Personal de Campo / Packing"
    },
    os.getenv("SUPERVISOR_USER", "supervisor_ica"): {
        "password": os.getenv("SUPERVISOR_PASS", "SupIca2026!"),
        "rol": "SUPERVISOR",
        "nombre": "Jefatura de Operaciones"
    }
}

security = HTTPBearer(auto_error=False)

def autenticar_usuario(username: str, password: str) -> dict | None:
    user = USUARIOS_ENV.get(username)
    if not user or user["password"] != password:
        return None
    expira = datetime.now(timezone.utc) + timedelta(hours=8)
    token = jwt.encode(
        {"sub": username, "rol": user["rol"], "nombre": user["nombre"], "exp": expira},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer", "rol": user["rol"], "nombre": user["nombre"]}

def obtener_usuario_actual(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado: falta token de acceso."
        )
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

def requerir_supervisor(usuario: dict = Depends(obtener_usuario_actual)) -> dict:
    if usuario.get("rol") != "SUPERVISOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: este recurso es exclusivo para SUPERVISOR."
        )
    return usuario
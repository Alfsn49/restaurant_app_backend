from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import bcrypt

SECRET_KEY = "secreto123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

bearer_scheme = HTTPBearer()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str)-> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")  # Guardar como string en la DB

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Token validation ---
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no es de acceso")
        return payload  # ahora retorna todo el contenido
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")



def get_refresh_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return token

def validate_refresh_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    print(token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no es de refresh")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    
def role_required(*allowed_roles: str):
    async def verify_role(credentials = Depends(bearer_scheme)):
        token = credentials.credentials
        print('Token recibido',token)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no es de acceso")

            rol_data = payload.get("rol")
            if not rol_data or rol_data.get("nombre") not in allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para acceder a este recurso")

            return payload  # si quieres devolver todos los datos del usuario

        except JWTError:
            print("Error en la decodificacion del token", JWTError)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    return verify_role

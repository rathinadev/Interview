from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import httpx
from jose import jwt, JWTError

from shared.app.settings import Settings

app = FastAPI(title="API Gateway")
settings = Settings()
client = httpx.AsyncClient()

async def get_current_user_id(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: User ID missing")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

# --- User Service Routes ---
@app.post("/register")
@app.post("/token")
async def user_auth_routes(request: Request):
    url = f"{settings.USER_SERVICE_URL}{request.url.path}"
    body = await request.json()
    response = await client.post(url, json=body)
    return JSONResponse(status_code=response.status_code, content=response.json())

# --- Product Service Routes ---
@app.post("/products")
async def create_product(request: Request, user_id: int = Depends(get_current_user_id)):
    url = f"{settings.PRODUCT_SERVICE_URL}{request.url.path}"
    body = await request.json()
    response = await client.post(url, json=body)
    return JSONResponse(status_code=response.status_code, content=response.json())

@app.get("/products/{product_id}")
async def get_product(request: Request, product_id: int):
    url = f"{settings.PRODUCT_SERVICE_URL}{request.url.path}"
    response = await client.get(url)
    return JSONResponse(status_code=response.status_code, content=response.json())

# --- Order Service Routes ---
@app.post("/orders")
async def create_order(request: Request, user_id: int = Depends(get_current_user_id)):
    url = f"{settings.ORDER_SERVICE_URL}{request.url.path}"
    body = await request.json()
    # Pass the authenticated user's ID to the order service in a header
    headers = {"user-id": str(user_id)}
    response = await client.post(url, json=body, headers=headers)
    return JSONResponse(status_code=response.status_code, content=response.json())
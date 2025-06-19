from fastapi import FastAPI, Depends, HTTPException
from . import models, schemas
from .database import engine
from .dependencies import get_api_key_from_header
from .services.divination_service import perform_divination

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Liu Yao Divination API",
    description="An API service for performing Liu Yao divination based on time.",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Liu Yao Divination API. Access the docs at /docs"}

@app.post("/divination", response_model=schemas.DivinationResponse)
async def create_divination(
    request: schemas.DivinationRequest,
    api_key: models.ApiKey = Depends(get_api_key_from_header) # 在这里注入安全依赖
):
    """
    Perform a divination.
    
    - **Authentication**: Requires a valid API key in the `X-API-Key` header.
    - **Body**: You can optionally provide a `target_time` in ISO 8601 format 
      (e.g., "2025-06-18T10:30:00") to perform divination for a specific moment.
      If omitted, the current server time is used.
    """
    try:
        divination_result = perform_divination(request.target_time)
        return divination_result
    except Exception as e:
        # 捕捉潜在的计算或数据查找错误
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
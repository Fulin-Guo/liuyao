from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas import DivinationRequest, DivinationResponse, EnhancedDivinationRequest, EnhancedDivinationResponse
from services.divination_service import perform_divination
from services.enhanced_divination_service import (
    perform_time_divination,
    perform_manual_divination,
    perform_name_divination
)
import os

app = FastAPI(title="六爻排盘API", version="1.0.0")

# 安全认证
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证API密钥"""
    api_key = os.getenv("API_KEY", "your-secret-api-key")
    if credentials.credentials != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

@app.post("/divination", response_model=DivinationResponse)
async def create_divination(
    request: DivinationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    六爻排盘API（原版）
    """
    try:
        result = perform_divination(request.target_time)
        return DivinationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enhanced-divination", response_model=EnhancedDivinationResponse)
async def create_enhanced_divination(
    request: EnhancedDivinationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    增强型六爻排盘API
    支持三种起卦方式：时间起卦、手工指定、卦名起卦
    返回完整的六爻盘信息，包括纳甲、六亲、六神、世应等
    """
    try:
        print(f"收到请求，起卦类型: {request.divination_type}")
        if request.divination_type in ["时间起卦", "time"]:
            result = perform_time_divination(request.target_time)
        elif request.divination_type in ["手工指定", "manual"]:
            if not request.manual_yaos:
                raise HTTPException(status_code=400, detail="手工指定模式需要提供manual_yaos参数")
            result = perform_manual_divination(request.manual_yaos, request.target_time)
        elif request.divination_type in ["卦名起卦", "name"]:
            if not all([request.upper_original, request.lower_original, 
                       request.upper_changed, request.lower_changed]):
                raise HTTPException(status_code=400, detail="卦名起卦模式需要提供所有卦名参数")
            result = perform_name_divination(
                request.upper_original, request.lower_original,
                request.upper_changed, request.lower_changed,
                request.target_time
            )
        else:
            print(f"不支持的起卦类型: {request.divination_type}")
            raise HTTPException(status_code=400, detail="不支持的起卦类型")
        
        return EnhancedDivinationResponse(**result)
    except Exception as e:
        print(f"API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "六爻排盘API服务正在运行"}
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class DivinationRequest(BaseModel):
    # 允许用户传入一个特定的时间进行排盘
    target_time: Optional[datetime] = None

class DivinationResponse(BaseModel):
    # 定义详细的响应结构，以确保API输出的一致性
    query_time: Dict[str, Any]
    hexagram: Dict[str, Any]

    class Config:
        orm_mode = True # 在新版 Pydantic 中可能是 from_attributes = True
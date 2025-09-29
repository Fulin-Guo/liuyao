from pydantic import BaseModel
from typing import Dict, Any, Optional, List
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

# 新增的增强型API模型
class EnhancedDivinationRequest(BaseModel):
    """增强型六爻起卦请求"""
    divination_type: str  # "时间起卦", "手工指定", "卦名起卦"
    target_time: Optional[datetime] = None
    
    # 手工指定模式的参数
    manual_yaos: Optional[List[str]] = None  # 如 ['阳爻', '阴爻动', '阳爻', '阴爻', '阳爻动', '阴爻']
    
    # 卦名起卦模式的参数
    upper_original: Optional[str] = None  # 本卦上卦
    lower_original: Optional[str] = None  # 本卦下卦
    upper_changed: Optional[str] = None   # 变卦上卦
    lower_changed: Optional[str] = None   # 变卦下卦

class YaoInfo(BaseModel):
    """单个爻的详细信息"""
    position: int        # 爻位（1-6）
    binary: str         # 二进制值（0或1）
    type: str           # 爻类型（阳爻/阴爻）
    liuqin: str         # 六亲（父母、兄弟、子孙、妻财、官鬼）
    najia: str          # 纳甲（如：戌土、申金等）
    liushen: str        # 六神（青龙、朱雀、勾陈、螣蛇、白虎、玄武）
    shi_ying: str       # 世应标记（世/应/空）

class HexagramInfo(BaseModel):
    """卦象详细信息"""
    name: str           # 卦名
    upper_trigram: str  # 上卦
    lower_trigram: str  # 下卦
    yao_binary: str     # 六爻二进制串
    gong: str           # 所属宫
    yaos: List[YaoInfo] # 六爻详细信息

class EnhancedDivinationResponse(BaseModel):
    """增强型六爻起卦响应"""
    divination_type: str                    # 起卦类型
    query_time: Dict[str, Any]             # 时间信息
    hexagram: Dict[str, Any]               # 卦象信息（包含original、changed、moving_line/moving_lines）

    class Config:
        orm_mode = True
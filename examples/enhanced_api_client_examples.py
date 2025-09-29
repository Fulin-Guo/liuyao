#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型六爻排盘API客户端示例
支持三种起卦方式的统一API调用
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# API配置
API_BASE_URL = os.getenv("LIUYAO_API_URL", "http://localhost:8001")
API_KEY = os.getenv("LIUYAO_API_KEY", "your-secret-api-key")

class LiuyaoAPIClient:
    """六爻排盘API客户端"""
    
    def __init__(self, base_url: str = API_BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def enhanced_divination(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用增强型六爻排盘API"""
        url = f"{self.base_url}/enhanced-divination"
        
        try:
            response = requests.post(url, headers=self.headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"错误详情: {e.response.text}")
            raise
    
    def time_divination(self, target_time: Optional[datetime] = None) -> Dict[str, Any]:
        """时间起卦"""
        request_data = {
            "divination_type": "time"
        }
        
        if target_time:
            request_data["target_time"] = target_time.isoformat()
        
        return self.enhanced_divination(request_data)
    
    def manual_divination(self, manual_yaos: List[str], target_time: Optional[datetime] = None) -> Dict[str, Any]:
        """手工指定起卦"""
        request_data = {
            "divination_type": "manual",
            "manual_yaos": manual_yaos
        }
        
        if target_time:
            request_data["target_time"] = target_time.isoformat()
        
        return self.enhanced_divination(request_data)
    
    def name_divination(self, upper_original: str, lower_original: str, 
                       upper_changed: str, lower_changed: str,
                       target_time: Optional[datetime] = None) -> Dict[str, Any]:
        """卦名起卦"""
        request_data = {
            "divination_type": "name",
            "upper_original": upper_original,
            "lower_original": lower_original,
            "upper_changed": upper_changed,
            "lower_changed": lower_changed
        }
        
        if target_time:
            request_data["target_time"] = target_time.isoformat()
        
        return self.enhanced_divination(request_data)

def print_divination_result(result: Dict[str, Any]):
    """打印六爻排盘结果"""
    print("=" * 60)
    print(f"起卦类型: {result['divination_type']}")
    print("=" * 60)
    
    # 时间信息
    query_time = result['query_time']
    print(f"查询时间: {query_time['formatted_time']}")
    print(f"农历: {query_time['lunar_date']}")
    print(f"干支: {query_time['ganzhi_info']['year_gz']} {query_time['ganzhi_info']['month_gz']} {query_time['ganzhi_info']['day_gz']} {query_time['ganzhi_info']['hour_gz']}")
    print()
    
    # 卦象信息
    hexagram = result['hexagram']
    original = hexagram['original']
    
    print(f"本卦: {original['name']} ({original['upper_trigram']}{original['lower_trigram']})")
    print(f"所属宫: {original['gong']}")
    print(f"二进制: {original['yao_binary']}")
    print()
    
    # 六爻详细信息
    print("六爻详细信息:")
    print("爻位 | 类型 | 纳甲   | 六亲 | 六神 | 世应")
    print("-" * 45)
    
    for yao in original['yaos']:
        print(f"{yao['position']:2d}   | {yao['type']:2s} | {yao['najia']:4s} | {yao['liuqin']:2s} | {yao['liushen']:2s} | {yao['shi_ying']:2s}")
    
    # 变卦信息（如果有）
    if 'changed' in hexagram and hexagram['changed']:
        changed = hexagram['changed']
        print()
        print(f"变卦: {changed['name']} ({changed['upper_trigram']}{changed['lower_trigram']})")
        print(f"所属宫: {changed['gong']}")
        print(f"二进制: {changed['yao_binary']}")
        
        if 'moving_line' in hexagram:
            print(f"动爻: 第{hexagram['moving_line']}爻")
        elif 'moving_lines' in hexagram:
            print(f"动爻: {hexagram['moving_lines']}")
    
    print("=" * 60)

def main():
    """主函数 - 演示三种起卦方式"""
    client = LiuyaoAPIClient()
    
    print("六爻排盘API增强版客户端示例")
    print("支持三种起卦方式的统一API调用")
    print()
    
    try:
        # 1. 时间起卦示例
        print("1. 时间起卦示例")
        print("-" * 30)
        
        # 使用当前时间
        result1 = client.time_divination()
        print_divination_result(result1)
        
        # 使用指定时间
        specific_time = datetime(2024, 6, 18, 14, 30, 0)
        result2 = client.time_divination(specific_time)
        print_divination_result(result2)
        
        # 2. 手工指定起卦示例
        print("2. 手工指定起卦示例")
        print("-" * 30)
        
        manual_yaos = ['阳爻', '阴爻动', '阳爻', '阴爻', '阳爻动', '阴爻']
        result3 = client.manual_divination(manual_yaos)
        print_divination_result(result3)
        
        # 3. 卦名起卦示例
        print("3. 卦名起卦示例")
        print("-" * 30)
        
        result4 = client.name_divination("乾", "坤", "震", "巽")
        print_divination_result(result4)
        
        # 4. 展示如何解析API返回的详细信息
        print("4. API返回数据结构示例")
        print("-" * 30)
        
        result = client.time_divination()
        
        print("完整的API返回结构:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n如何提取关键信息:")
        print(f"- 起卦类型: result['divination_type']")
        print(f"- 日干: result['query_time']['ganzhi_info']['day'][0]")
        print(f"- 本卦名: result['hexagram']['original']['name']")
        print(f"- 本卦宫位: result['hexagram']['original']['gong']")
        print(f"- 六爻信息: result['hexagram']['original']['yaos']")
        print(f"- 每爻的纳甲: yao['najia']")
        print(f"- 每爻的六亲: yao['liuqin']")
        print(f"- 每爻的六神: yao['liushen']")
        print(f"- 每爻的世应: yao['shi_ying']")
        
    except Exception as e:
        print(f"示例执行失败: {e}")

if __name__ == "__main__":
    main()
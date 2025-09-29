# app/services/enhanced_divination_service.py
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from . import constants
from .time_converter import LunarDateTimeConverter
from .divination_service import HexagramCalculator, calculate_liushen

def parse_yao_details(yao_info: Dict[str, str]) -> Dict[str, str]:
    """
    解析爻位信息，分离纳甲、六亲、世应等信息
    :param yao_info: 原始爻位信息，如 {'name': '父母戌土 世'}
    :return: 解析后的详细信息
    """
    name = yao_info.get('name', '')
    
    # 分离世应标记
    shi_ying = ''
    if name.endswith(' 世'):
        shi_ying = '世'
        name = name[:-2].strip()
    elif name.endswith(' 应'):
        shi_ying = '应'
        name = name[:-2].strip()
    
    # 解析纳甲六亲信息（格式：六亲+纳甲）
    # 例如：父母戌土 -> 六亲：父母，纳甲：戌土
    liuqin = ''
    najia = ''
    
    if name:
        # 常见六亲：父母、兄弟、子孙、妻财、官鬼
        liuqin_patterns = ['父母', '兄弟', '子孙', '妻财', '官鬼']
        for pattern in liuqin_patterns:
            if name.startswith(pattern):
                liuqin = pattern
                najia = name[len(pattern):].strip()
                break
        
        if not liuqin:
            # 如果没有匹配到标准六亲，整个作为纳甲
            najia = name
    
    return {
        'liuqin': liuqin,
        'najia': najia,
        'shi_ying': shi_ying
    }

def get_enhanced_hexagram_details(binary_str: str, day_tiangan: str = None) -> Dict[str, Any]:
    """
    获取增强的卦象详情，包含完整的六爻盘信息
    """
    # 建立二进制 -> 卦名 的反向查找表
    TRIGRAM_BINARY_MAP = {
        HexagramCalculator.generate_binary_representation(i): name 
        for i, name in enumerate(constants.HEXAGRAM_NAMES)
    }

    upper_bin = binary_str[:3]
    lower_bin = binary_str[3:]

    upper_name = TRIGRAM_BINARY_MAP.get(upper_bin, "未知")
    lower_name = TRIGRAM_BINARY_MAP.get(lower_bin, "未知")

    full_name_key = f"{upper_name}{lower_name}"
    full_name = constants.GUA_64.get(full_name_key, f"未知卦 ({full_name_key})")
    
    base_name_for_liuyao = full_name.split('（')[0]
    gua_info = constants.GUA_LIUYAO.get(base_name_for_liuyao, {})
    liuyao_info = gua_info.get('yao_info', [])
    gong = gua_info.get('gong', '未知宫')
    
    # 计算六神（如果提供了日干）
    liushen_list = []
    if day_tiangan:
        liushen_list = calculate_liushen(day_tiangan)
    
    # 构建详细的六爻信息
    detailed_yaos = []
    for i in range(6):
        yao_position = i + 1  # 爻位：1-6（初爻到上爻）
        yao_binary = binary_str[5-i]  # 二进制串是从上爻到初爻
        yao_type = "阳爻" if yao_binary == "0" else "阴爻"
        
        # 纳甲六亲信息
        yao_details = {}
        if i < len(liuyao_info):
            yao_details = parse_yao_details(liuyao_info[i])
        
        # 六神信息
        liushen = ""
        if i < len(liushen_list):
            liushen = liushen_list[i]
        
        detailed_yaos.append({
            'position': yao_position,
            'binary': yao_binary,
            'type': yao_type,
            'liuqin': yao_details.get('liuqin', ''),
            'najia': yao_details.get('najia', ''),
            'liushen': liushen,
            'shi_ying': yao_details.get('shi_ying', '')
        })

    return {
        "name": full_name,
        "upper_trigram": upper_name,
        "lower_trigram": lower_name,
        "yao_binary": binary_str,
        "gong": gong,
        "yaos": detailed_yaos
    }

def perform_time_divination(target_time: datetime = None) -> Dict[str, Any]:
    """
    执行时间起卦
    """
    if target_time is None:
        target_time = datetime.now()

    converter = LunarDateTimeConverter(target_time)
    basic_info = converter.get_basic_info()
    ganzhi_info = converter.get_ganzhi_info()
    
    calculation_params = {
        'dizhi_year': HexagramCalculator.get_dizhi_number(ganzhi_info['year_gz'][1]),
        'month': abs(basic_info['month']),
        'day': basic_info['day'],
        'dizhi_hour': HexagramCalculator.get_dizhi_number(ganzhi_info['hour_gz'][1])
    }
    
    upper_idx, lower_idx, moving_line = HexagramCalculator.calculate_hexagram_indices(calculation_params)
    ben_gua_bin, bian_gua_bin = HexagramCalculator.calculate_changes(upper_idx, lower_idx, moving_line)
    
    # 获取日干用于计算六神
    day_tiangan = ganzhi_info['day_gz'][0]
    
    # 获取增强的卦象详情
    ben_gua_details = get_enhanced_hexagram_details(ben_gua_bin, day_tiangan)
    bian_gua_details = get_enhanced_hexagram_details(bian_gua_bin, day_tiangan)

    return {
        "divination_type": "时间起卦",
        "query_time": {
            "formatted_time": target_time.strftime('%Y-%m-%d %H:%M:%S'),
            "lunar_date": f"{basic_info['year']}年{basic_info['month']}月{basic_info['day']}日 {basic_info['hour']}时",
            "ganzhi_info": ganzhi_info
        },
        "hexagram": {
            "original": ben_gua_details,
            "changed": bian_gua_details,
            "moving_line": moving_line
        }
    }

def perform_manual_divination(manual_yaos: List[str], target_time: datetime = None) -> Dict[str, Any]:
    """
    执行手工指定起卦
    :param manual_yaos: 六个爻的选择，如 ['阳爻', '阴爻动', '阳爻', '阴爻', '阳爻动', '阴爻']
    """
    if target_time is None:
        target_time = datetime.now()
    
    # 获取时间信息用于四柱
    converter = LunarDateTimeConverter(target_time)
    basic_info = converter.get_basic_info()
    ganzhi_info = converter.get_ganzhi_info()
    day_tiangan = ganzhi_info['day_gz'][0]
    
    # 转换手工爻选择为二进制和动爻
    ben_gua_bits = []
    moving_lines = []
    
    for i, yao_choice in enumerate(manual_yaos):
        if "阳爻" in yao_choice:
            ben_gua_bits.append('0')  # 阳爻
        else:
            ben_gua_bits.append('1')  # 阴爻
        
        if "动" in yao_choice:
            moving_lines.append(i + 1)  # 记录动爻位置（1-6）
    
    # 组合为上→下顺序的二进制串
    ben_gua_binary = ''.join(reversed(ben_gua_bits))
    
    # 计算变卦
    if not moving_lines:
        bian_gua_binary = ben_gua_binary
    else:
        bian_gua_bits = list(ben_gua_binary)
        for ml in moving_lines:
            idx = 6 - ml  # 转换为二进制串中的索引
            bian_gua_bits[idx] = str(1 - int(bian_gua_bits[idx]))
        bian_gua_binary = ''.join(bian_gua_bits)
    
    # 获取增强的卦象详情
    ben_gua_details = get_enhanced_hexagram_details(ben_gua_binary, day_tiangan)
    bian_gua_details = get_enhanced_hexagram_details(bian_gua_binary, day_tiangan)

    return {
        "divination_type": "手工指定",
        "query_time": {
            "formatted_time": target_time.strftime('%Y-%m-%d %H:%M:%S'),
            "lunar_date": f"{basic_info['year']}年{basic_info['month']}月{basic_info['day']}日 {basic_info['hour']}时",
            "ganzhi_info": ganzhi_info
        },
        "hexagram": {
            "original": ben_gua_details,
            "changed": bian_gua_details,
            "moving_lines": moving_lines
        }
    }

def perform_name_divination(upper_original: str, lower_original: str, 
                          upper_changed: str, lower_changed: str, 
                          target_time: datetime = None) -> Dict[str, Any]:
    """
    执行卦名起卦
    """
    if target_time is None:
        target_time = datetime.now()
    
    # 获取时间信息用于四柱
    converter = LunarDateTimeConverter(target_time)
    basic_info = converter.get_basic_info()
    ganzhi_info = converter.get_ganzhi_info()
    day_tiangan = ganzhi_info['day_gz'][0]
    
    # 卦名到二进制的映射
    NAME_TO_BIN = {
        name: HexagramCalculator.generate_binary_representation(i) 
        for i, name in enumerate(constants.HEXAGRAM_NAMES)
    }
    
    # 构建本卦和变卦的二进制串
    ben_gua_binary = NAME_TO_BIN.get(upper_original, '000') + NAME_TO_BIN.get(lower_original, '000')
    bian_gua_binary = NAME_TO_BIN.get(upper_changed, '000') + NAME_TO_BIN.get(lower_changed, '000')
    
    # 计算动爻
    moving_lines = []
    for i in range(6):
        if ben_gua_binary[i] != bian_gua_binary[i]:
            moving_lines.append(6 - i)  # 转换为爻位（1-6）
    
    # 获取增强的卦象详情
    ben_gua_details = get_enhanced_hexagram_details(ben_gua_binary, day_tiangan)
    bian_gua_details = get_enhanced_hexagram_details(bian_gua_binary, day_tiangan)

    return {
        "divination_type": "卦名起卦",
        "query_time": {
            "formatted_time": target_time.strftime('%Y-%m-%d %H:%M:%S'),
            "lunar_date": f"{basic_info['year']}年{basic_info['month']}月{basic_info['day']}日 {basic_info['hour']}时",
            "ganzhi_info": ganzhi_info
        },
        "hexagram": {
            "original": ben_gua_details,
            "changed": bian_gua_details,
            "moving_lines": moving_lines
        }
    }
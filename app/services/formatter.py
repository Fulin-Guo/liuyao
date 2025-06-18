from typing import Dict
from . import constants # 引入常量，方便未来使用GUA_64等

class ResultFormatter:
    """结果格式化输出"""
    @staticmethod
    def format_output(basic_info: Dict, ganzhi_info: Dict, hexagram_data: Dict) -> str:
        """格式化输出结果"""
        output_lines = []
        output_lines.append("--- 公历时间 ---")
        # (可以从 datetime.now() 获取更精确的公历时间加入到 basic_info 中)
        # output_lines.append(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


        output_lines.append("\n--- 农历及干支信息 ---")
        # 为了对齐，可以动态计算key的最大长度
        # max_len = max(len(k) for k in list(basic_info.keys()) + list(ganzhi_info.keys()))
        
        # 合并农历时间为一行显示
        lunar_time = f"{basic_info['year']}年 {basic_info['month']}月 {basic_info['day']}日 {basic_info['hour']}时 {basic_info['minute']}分"
        output_lines.append(f"{'农历时间':8}: {lunar_time}")

        ganzhi_display_map = {
            'year_gz': '年柱', 'month_gz': '月柱', 
            'day_gz': '日柱', 'hour_gz': '时柱'
        }
        for k, v_key in ganzhi_display_map.items():
            output_lines.append(f"{v_key:8}: {ganzhi_info[k]}")
        
        output_lines.append("\n--- 卦象信息 ---")
        # 提取上下卦的中文名和数字索引，用于组合查询 GUA_64
        upper_trigram_name_char = hexagram_data['upper_hexagram'].split(' ')[0] # 如 '乾'
        lower_trigram_name_char = hexagram_data['lower_hexagram'].split(' ')[0] # 如 '巽'
        
        # 形成GUA_64的查询键
        ben_gua_key = f"{upper_trigram_name_char}{lower_trigram_name_char}"
        bian_gua_key = f"{upper_trigram_name_char}{lower_trigram_name_char}"
        full_ben_gua_name = constants.GUA_64.get(ben_gua_key, "未知本卦")
        full_bian_gua_name = constants.GUA_64.get(bian_gua_key, "未知本卦")
        output_lines.append(f"{'本卦':8}: {full_ben_gua_name} ({hexagram_data['ben_gua']})")
        output_lines.append(f"{'动爻':8}: {hexagram_data['moving_line']}")
        output_lines.append(f"{'变卦':8}: {full_bian_gua_name} ({hexagram_data['bian_gua']})")
    
        return "\n".join(output_lines)
from datetime import datetime
from typing import Dict
from lunar_python import Lunar
# 如果此类需要访问常量，可以从 .constants 导入，但目前看其方法主要依赖lunar_python库

class LunarDateTimeConverter:
    """农历日期时间转换器"""

    def __init__(self):
        self.lunar = Lunar.fromDate(datetime.now())
        
    def get_basic_info(self) -> Dict:
        """获取基础农历信息"""
        return {
            'year': self.lunar.getYear(),
            'month': self.lunar.getMonth(),
            'day': self.lunar.getDay(),
            'hour': self.lunar.getHour(),
            'minute': self.lunar.getMinute()
        }
    
    def get_ganzhi_info(self) -> Dict:
        """获取干支信息"""
        return {
            'year_gz': self.lunar.getYearInGanZhiExact(),
            'month_gz': self.lunar.getMonthInGanZhiExact(),
            'day_gz': self.lunar.getDayInGanZhi(),
            'hour_gz': self.lunar.getTimeInGanZhi()
        }
from datetime import datetime
from typing import Dict
from lunar_python import Lunar

class LunarDateTimeConverter:
    def __init__(self, dt: datetime = None):
        if dt is None:
            dt = datetime.now()
        self.lunar = Lunar.fromDate(dt)
        
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
"""
L2 感知层：魏征/都察院
Reality Perception - 现实对账

职责：
1. 读取现实数据（睡眠、财务、健康等）
2. 只说真话，不许粉饰
3. 以"犯颜直谏"的姿态对账现实
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RealityMetric:
    """现实指标"""
    name: str
    value: Any
    unit: str = ""
    timestamp: str = ""
    source: str = ""  # 数据来源
    abnormal: bool = False  # 是否异常


class PerceptionLayer:
    """
    感知层 - 魏征/都察院
    
    "犯颜直谏，只说真话"
    
    读取身体、财务、家庭等现实数据。
    发现异常必须如实上报，不许粉饰太平。
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data_sources = self._init_data_sources()
        self.last_observation = None
        
    def _init_data_sources(self) -> Dict[str, Dict]:
        """初始化数据源配置"""
        return self.config.get("data_sources", {
            "health": {
                "enabled": True,
                "type": "apple_health",  # or "manual", "api"
                "metrics": ["sleep", "steps", "heart_rate", "weight"]
            },
            "finance": {
                "enabled": True,
                "type": "manual",
                "metrics": ["balance", "income", "expense"]
            },
            "calendar": {
                "enabled": True,
                "type": "system",
                "metrics": ["today_events", "upcoming"]
            },
            "weather": {
                "enabled": True,
                "type": "api",
                "endpoint": "weather"
            }
        })

    def observe(self, user_input: str) -> Dict[str, Any]:
        """
        观察用户输入涉及的现实数据
        
        分析用户意图，提取需要感知的现实维度，
        然后读取对应数据。
        """
        observations = []
        anomalies = []
        
        # 意图分析：用户关心什么现实数据？
        intent = self._analyze_intent(user_input)
        
        for intent_type in intent:
            if intent_type == "health":
                health_data = self._read_health_data()
                observations.append(("health", health_data))
                if health_data.get("anomalies"):
                    anomalies.extend(health_data["anomalies"])
                    
            elif intent_type == "finance":
                finance_data = self._read_finance_data()
                observations.append(("finance", finance_data))
                if finance_data.get("anomalies"):
                    anomalies.extend(finance_data["anomalies"])
                    
            elif intent_type == "time":
                time_data = self._read_time_data()
                observations.append(("time", time_data))
                
            elif intent_type == "weather":
                weather_data = self._read_weather_data()
                observations.append(("weather", weather_data))
        
        result = {
            "intent": intent,
            "observations": dict(observations),
            "anomalies": anomalies,
            "vetoed": len([a for a in anomalies if a.get("severity") > 2]) > 0,
            "raw": self._build_raw_context(observations)
        }
        
        self.last_observation = result
        return result

    def _analyze_intent(self, text: str) -> List[str]:
        """分析用户意图，判断需要哪些现实数据"""
        text_lower = text.lower()
        intents = []
        
        if any(k in text_lower for k in ["睡眠", "健康", "身体", "步数", "心率", "体重"]):
            intents.append("health")
        if any(k in text_lower for k in ["钱", "财务", "支出", "收入", "账单", "余额"]):
            intents.append("finance")
        if any(k in text_lower for k in ["日程", "会议", "安排", "时间", "几点"]):
            intents.append("time")
        if any(k in text_lower for k in ["天气", "温度", "下雨"]):
            intents.append("weather")
            
        return intents

    def _read_health_data(self) -> Dict[str, Any]:
        """读取健康数据（模拟）"""
        # 实际项目中，这里会调用 Apple Health / Fitbit / 自定义 API
        return {
            "sleep_hours": 6.5,
            "sleep_quality": "一般",
            "steps": 8200,
            "heart_rate": 72,
            "weight": 70.5,
            "anomalies": [
                {"metric": "sleep", "expected": "7-8小时", "actual": "6.5小时", "severity": 1}
            ]
        }

    def _read_finance_data(self) -> Dict[str, Any]:
        """读取财务数据（模拟）"""
        return {
            "balance": 12345.67,
            "income_this_month": 25000,
            "expense_this_month": 18500,
            "anomalies": []
        }

    def _read_time_data(self) -> Dict[str, Any]:
        """读取时间数据"""
        now = datetime.now()
        return {
            "now": now.isoformat(),
            "hour": now.hour,
            "weekday": now.strftime("%A"),
            "date": now.strftime("%Y-%m-%d")
        }

    def _read_weather_data(self) -> Dict[str, Any]:
        """读取天气数据（模拟）"""
        return {
            "temp": 22,
            "condition": "多云",
            "humidity": 65,
            "pm25": 45
        }

    def _build_raw_context(self, observations: List) -> str:
        """构建原始上下文字符串"""
        lines = []
        for source, data in observations:
            lines.append(f"【{source.upper()}】")
            for key, value in data.items():
                if key != "anomalies":
                    lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    def add_data_source(self, name: str, config: Dict):
        """添加数据源"""
        self.data_sources[name] = config

    def get_current_reality(self) -> Dict[str, Any]:
        """获取当前所有现实数据"""
        return {
            "health": self._read_health_data(),
            "finance": self._read_finance_data(),
            "time": self._read_time_data(),
            "weather": self._read_weather_data()
        }

"""时间工具 - 获取当前时间信息"""

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前时间
    
    当用户询问当前时间、日期或时间相关信息时，使用此工具。
    
    Returns:
        str: 当前时间的字符串表示
    """
    try:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"获取当前时间: {current_time}")
        return current_time
    except Exception as e:
        print(f"获取当前时间失败: {e}")
        return f"获取时间失败: {str(e)}"

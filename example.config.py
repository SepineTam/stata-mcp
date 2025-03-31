from datetime import datetime
# Stata MCP 配置文件

# 临时数据存储路径
TEMP_DATA_PATH = "～/tempdata"

# 其他配置项可以在此添加
readme_content = f"""# stata-mcp-log\nHere is the log of your use of stata-mcp-serve
# Naming convention\ntime.log
# Init
The first time you use the serve is {datetime.strftime(datetime.now(), "%Y-%m-%d")}
"""

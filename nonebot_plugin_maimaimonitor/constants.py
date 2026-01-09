from enum import IntEnum

class ReportCode(IntEnum):
    ERR_NET_LOST = 101
    ERR_LOGIN = 102
    ERR_MAI_NET = 103
    ACC_INVOICE = 201
    ACC_BAN = 202
    ACC_SCAN = 203
    WAIT_TIME = 300

OG_API_URL = "https://mai.chongxi.us/api/og"

REPORT_MAPPING = {
    "1": (ReportCode.ERR_NET_LOST, "断网"),
    "断网": (ReportCode.ERR_NET_LOST, "断网"),
    
    "2": (ReportCode.ERR_LOGIN, "无法登录"),
    "无法登录": (ReportCode.ERR_LOGIN, "无法登录"),

    "3": (ReportCode.ERR_MAI_NET, "NET打不开"),
    "net打不开": (ReportCode.ERR_MAI_NET, "NET打不开"),

    "4": (ReportCode.ACC_INVOICE, "被发票"),
    "被发票": (ReportCode.ACC_INVOICE, "被发票"),

    "5": (ReportCode.ACC_BAN, "小黑屋"),
    "小黑屋": (ReportCode.ACC_BAN, "小黑屋"),

    "6": (ReportCode.ACC_SCAN, "其他扫号行为"),
    "其他扫号行为": (ReportCode.ACC_SCAN, "其他扫号行为"),

    "7": (ReportCode.WAIT_TIME, "罚站时长"),
    "罚站时长": (ReportCode.WAIT_TIME, "罚站时长"),
    "罚站": (ReportCode.WAIT_TIME, "罚站时长"),
}

def get_help_menu():
    menu = """查看使用方法:
/report help 或 /上报 帮助

帮助菜单
用法: /report [类型] [参数(可选)]
1. 断网
2. 无法登录
3. NET打不开
4. 被发票
5. 小黑屋
6. 其他扫号行为
7. 罚站时长 + [秒数]

示例:
/report 1
/report 7 120
/report 断网
/report 罚站 120

其他查询:
/net : 查看服务器状态图
直接发送「网咋样」或「炸了吗」也可触发"""
    return menu
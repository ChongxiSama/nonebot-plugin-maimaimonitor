# isMaiDownOBot11/plugins/maimai_plugin_v11.py
from asyncio import Lock
from collections import defaultdict
from nonebot import on_command, get_driver, require, get_plugin_config
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event, Message # V11 imports
from nonebot.params import CommandArg
import asyncio # New import
from nonebot import get_plugin_config
from .config import Config

config = get_plugin_config(Config)
from .client import MaimaiReporter
from .constants import get_help_menu, REPORT_MAPPING, ReportCode

reporter = MaimaiReporter(
    client_id=config.maimai_bot_client_id,
    private_key=config.maimai_bot_private_key,
    worker_url=config.maimai_worker_url
)

report_cache: defaultdict[int, list[int]] = defaultdict(list)
cache_lock = Lock()

report_matcher = on_command("report", aliases={"上报"}, priority=5, block=False)

@report_matcher.handle()
async def handle_report(bot: Bot, event: Event, args: Message = CommandArg()):
    arg_text = args.extract_plain_text().strip()
    arg_parts = arg_text.split()

    if not arg_text or len(arg_parts) == 0:
        await report_matcher.finish(f"指令格式错误。\n{get_help_menu()}")
        return

    if arg_parts[0].lower() in ['help', '帮助']:
        await report_matcher.finish(get_help_menu())
        return

    report_key = arg_parts[0].lower()
    if report_key not in REPORT_MAPPING:
        await report_matcher.finish(f"未知的报告类型: '{report_key}'\n请使用 /report help 查看可用类型。")
        return

    report_code, report_name = REPORT_MAPPING[report_key]
    report_value = 1 # Initialize report_value to 1

    if report_code == ReportCode.WAIT_TIME:
        if len(arg_parts) > 1:
            try:
                report_value = int(arg_parts[1])
            except ValueError:
                await report_matcher.finish("罚站时长参数必须是数字（秒数）")
                return
        else:
            await report_matcher.finish("请输入罚站时长（秒）。\n用法: /report 罚站 [秒数]")
            return

    async with cache_lock:
        report_cache[report_code].append(report_value)

    await report_matcher.finish(f"{report_name}上报成功")

COUNT_BASED_TYPES = {
    ReportCode.ERR_NET_LOST, ReportCode.ERR_LOGIN, ReportCode.ERR_MAI_NET,
    ReportCode.ACC_INVOICE, ReportCode.ACC_BAN, ReportCode.ACC_SCAN
}

async def send_aggregated_reports():
    """Aggregates and sends reports from the cache."""
    final_payload = []
    
    async with cache_lock:
        if not report_cache:
            return
        
        cached_items = list(report_cache.items())
        report_cache.clear()

    for report_type, values in cached_items:
        if report_type in COUNT_BASED_TYPES:
            total_value = sum(values)
            if total_value > 0:
                final_payload.append({"t": report_type, "v": total_value, "r": "BOT"})
        else:
            for value in values:
                final_payload.append({"t": report_type, "v": value, "r": "BOT"})
    
    if not final_payload:
        return

    try:
        print("--- Sending aggregated bot report... ---")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, reporter.send_report, final_payload, config.maimai_bot_display_name)
    except Exception as e:
        print(f"Error sending aggregated report: {e}")

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

scheduler.add_job(send_aggregated_reports, "interval", seconds=30, id="maimai_report_scheduler_v11")

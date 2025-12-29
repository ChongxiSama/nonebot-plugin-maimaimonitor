from asyncio import Lock
from collections import defaultdict
from nonebot import on_command, get_driver, require
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from nonebot.params import CommandArg
import asyncio
from typing import Any # Added import for 'Any'
from .config import Config

driver = get_driver()
global_config = driver.config

config = Config(
    maimai_bot_client_id=getattr(global_config, "maimai_bot_client_id", None),
    maimai_bot_private_key=getattr(global_config, "maimai_bot_private_key", None),
    maimai_bot_display_name=getattr(global_config, "maimai_bot_display_name", None),
    maimai_worker_url=getattr(global_config, "maimai_worker_url", "https://maiapi.chongxi.us"),
    command_aliases=getattr(global_config, "command_aliases", {}),
)
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
    report_value = 1

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

    result_message = await process_maimai_report(
        report_code=report_code,
        report_name=report_name,
        report_value=report_value,
        bot=bot,
        event=event
    )
    await report_matcher.finish(result_message)


async def process_maimai_report(
    report_code: ReportCode,
    report_name: str,
    report_value: Any,
    bot: Bot,
    event: Event
) -> str:
    async with cache_lock:
        report_cache[report_code].append(report_value)
    return f"{report_name}上报成功"


async def trigger_report_by_command_string(
    command_string: str,
    bot: Bot,
    event: Event
) -> str:
    arg_text = command_string.lstrip('/').lstrip("report").strip()
    arg_parts = arg_text.split()

    if not arg_text or len(arg_parts) == 0:
        return f"指令格式错误。\n{get_help_menu()}"

    report_key = arg_parts[0].lower()
    if report_key not in REPORT_MAPPING:
        return f"未知的报告类型: '{report_key}'\n请使用 /report help 查看可用类型。"

    report_code, report_name = REPORT_MAPPING[report_key]
    report_value = 1

    if report_code == ReportCode.WAIT_TIME:
        if len(arg_parts) > 1:
            try:
                report_value = int(arg_parts[1])
            except ValueError:
                return "罚站时长参数必须是数字（秒数）。"
        else:
            return "请输入罚站时长（秒）。\n用法: /report 罚站 [秒数]"

    return await process_maimai_report(
        report_code=report_code,
        report_name=report_name,
        report_value=report_value,
        bot=bot,
        event=event
    )

COUNT_BASED_TYPES = {
    ReportCode.ERR_NET_LOST, ReportCode.ERR_LOGIN, ReportCode.ERR_MAI_NET,
    ReportCode.ACC_INVOICE, ReportCode.ACC_BAN, ReportCode.ACC_SCAN
}

async def send_aggregated_reports():
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
        await reporter.send_report(final_payload, config.maimai_bot_display_name)
    except Exception as e:
        print(f"Error sending aggregated report: {e}")


def create_dynamic_alias_matcher(trigger_cmd: str, target_cmd_string: str):
    dynamic_matcher = on_command(trigger_cmd, block=False, priority=5)

    @dynamic_matcher.handle()
    async def handle_dynamic_alias(bot: Bot, event: Event, args: Message = CommandArg()):
        result_message = await trigger_report_by_command_string(
            command_string=target_cmd_string,
            bot=bot,
            event=event
        )
        await dynamic_matcher.finish(f"命令联动触发 [{trigger_cmd}]: {result_message}")


for trigger_cmd, target_cmd_string in config.command_aliases.items():
    create_dynamic_alias_matcher(trigger_cmd, target_cmd_string)


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

scheduler.add_job(send_aggregated_reports, "interval", seconds=30, id="maimai_report_scheduler_v11")
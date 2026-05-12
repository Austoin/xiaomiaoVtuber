#!/bin/python
import faulthandler

faulthandler.enable()

import asyncio
import datetime
import os
import random
import re
import base64
import urllib.parse
import emoji
import time
import traceback
from openai import OpenAI
import requests, aiohttp
from Hyper import Configurator
import platform
import psutil
import GPUtil
import subprocess
from typing import Set
from PIL import Image
import io
import threading
import paramiko
from console_output import configure_console_output
from desktop_bridge import publish_desktop_state, start_desktop_bridge_server

# import framework
Configurator.cm = Configurator.ConfigManager(
    Configurator.Config(file="config.json").load_from_file()
)
bot_name = Configurator.cm.get_cfg().others["bot_name"]  # 星·简
bot_name_en = Configurator.cm.get_cfg().others["bot_name_en"]  # Shining girl
from Hyper import Listener, Events, Logger, Manager, Segments
from Hyper.Utils import Logic
from Hyper.Events import *

# import moudles
from GoogleAI import genai, Context, Parts, Roles

# from google.generativeai.types import FunctonDeclaration
from SearchOnline import network_gpt as SearchOnline
from prerequisites import prerequisite, select_role, update_role_lists
import Quote

config = Configurator.cm.get_cfg()
logger = Logger.Logger()
logger.set_level(config.log_level)
configure_console_output()
version_name = "2.0"
cooldowns = {}
cooldowns1 = {}
second_start = time.time()
EnableNetwork = "Pixmap"
user_lists = {}
in_timing = False
emoji_send_count: datetime = None

generating = False
bridge_server = None
bridge_lock = threading.Lock()
RUNTIME_DIR = "runtime"
SUPER_USER_FILE = os.path.join(RUNTIME_DIR, "Super_User.ini")
MANAGE_USER_FILE = os.path.join(RUNTIME_DIR, "Manage_User.ini")
SISTERS_FILE = os.path.join(RUNTIME_DIR, "sisters.ini")
JHQ_FILE = os.path.join(RUNTIME_DIR, "jhq.ini")
PROGRAMMERS_FILE = os.path.join(RUNTIME_DIR, "programmers.ini")
TIMING_MESSAGE_FILE = os.path.join(RUNTIME_DIR, "timing_message.ini")
BLACKLIST_FILE = os.path.join(RUNTIME_DIR, "blacklist.sr")


class Tools:
    pass


generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

sys_prompt = f""""""

model = genai.GenerativeModel()

key = Configurator.cm.get_cfg().others["gemini_key"]
gemini_base_url = Configurator.cm.get_cfg().others.get("gemini_base_url", None)
reminder: str = Configurator.cm.get_cfg().others["reminder"]
genai.configure(api_key=key, base_url=gemini_base_url)

# 模型配置
default_model = Configurator.cm.get_cfg().others.get(
    "default_model", "gemini-3-flash-preview"
)
fallback_model = Configurator.cm.get_cfg().others.get("fallback_model", "deepseek-v3")
fallback_key = Configurator.cm.get_cfg().others.get("fallback_key", key)

# 图片API配置
image_api_config = Configurator.cm.get_cfg().others.get("image_api", {})
pixiv_api_url = image_api_config.get("pixiv_url", "https://api.mossia.top/duckMo")
x_api_url = image_api_config.get("x_url", "https://api.mossia.top/duckMo/x")

# 人设配置
personas_config = Configurator.cm.get_cfg().others.get("personas", {})

tools = []
ROOT_User: list = Configurator.cm.get_cfg().others["ROOT_User"]
Super_User: list = []
Manage_User: list = []
sisters: list = []
jhq: list = []
programmers: list = []


def load_blacklist():
    try:
        with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
            blacklist115 = set(
                line.strip() for line in f
            )  # 使用集合方便快速查找,不然容易溶血
        return blacklist115
    except FileNotFoundError:
        return set()


class ContextManager:
    def __init__(self):
        self.groups: dict[int, dict[int, Context]] = {}

    def get_context(self, uin: int, gid: int):
        try:
            ctx = self.groups[gid][uin]
            # 同步更新 model 配置，确保使用最新的模型
            ctx.model = model
            ctx.model_name = getattr(
                model, "model_name", "gemini-2.0-flash-thinking-exp-01-21"
            )
            ctx.system_instruction = getattr(model, "_system_instruction", None)
            ctx.generation_config = getattr(model, "generation_config", {})
            return ctx
        except KeyError:
            if self.groups.get(gid):
                self.groups[gid][uin] = Context(
                    key, model, base_url=gemini_base_url, tools=tools
                )
                return self.groups[gid][uin]
            else:
                self.groups[gid] = {}
                self.groups[gid][uin] = Context(
                    key, model, base_url=gemini_base_url, tools=tools
                )
                return self.groups[gid][uin]


cmc = ContextManager()


def has_emoji(s: str) -> bool:
    # 判断找到的 emoji 数量是否为 1 并且字符串的长度大于等于 1
    return emoji.emoji_count(s) == 1 and len(s) == 1


def get_market_face_url(face_id: str) -> str:
    """获取商城表情包的图片 URL"""
    # 商城表情包 URL 格式
    return f"https://gxh.vip.qq.com/club/item/parcel/item/{face_id[:2]}/{face_id}/raw300.gif"


def select_persona_prompt(user_id: int, event_user: str) -> str:
    user_id_str = str(user_id)
    persona = prerequisite(bot_name, event_user, personas_config)
    role = select_role(user_id_str, sisters, jhq, programmers)

    if role == "programmer":
        return persona.senior_programmer()
    if role == "mother":
        return persona.mother()
    if role == "sister":
        return persona.sister()
    return persona.girl_friend()


def generate_desktop_reply(user_id: int, text: str) -> str:
    global model
    global sys_prompt

    desktop_user_name = f"桌面用户{user_id}"
    sys_prompt = select_persona_prompt(user_id, desktop_user_name)

    with bridge_lock:
        model = genai.GenerativeModel(
            model_name=default_model,
            generation_config=generation_config,
            system_instruction=sys_prompt or None,
        )
        message = Roles.User(Parts.Text(text))
        try:
            result = cmc.get_context(user_id, 0).gen_content(message).rstrip("\n")
            publish_desktop_state(user_id, result)
            return result
        except Exception as primary_error:
            print(f"[桌面桥接][主模型失败] {default_model}: {primary_error}")
            genai.configure(api_key=fallback_key, base_url=gemini_base_url)
            model = genai.GenerativeModel(
                model_name=fallback_model,
                generation_config=generation_config,
                system_instruction=sys_prompt or None,
            )
            cmc.groups.clear()
            result = cmc.get_context(user_id, 0).gen_content(message).rstrip("\n")
            genai.configure(api_key=key, base_url=gemini_base_url)
            model = genai.GenerativeModel(
                model_name=default_model,
                generation_config=generation_config,
                system_instruction=sys_prompt or None,
            )
            publish_desktop_state(user_id, result)
            return result


def start_desktop_bridge() -> None:
    global bridge_server

    if bridge_server is not None:
        return

    bridge_user_id = int((config.owner or [config.others["ROOT_User"][0]])[0])
    bridge_server = start_desktop_bridge_server(
        host="127.0.0.1",
        port=5519,
        default_user_id=bridge_user_id,
        model_name=default_model,
        reply_callback=generate_desktop_reply,
    )
    bridge_thread = threading.Thread(target=bridge_server.serve_forever, daemon=True)
    bridge_thread.start()
    print(f"[桌面桥接] 已启动: http://127.0.0.1:5519/v1/chat/completions")


def timing_message(actions: Listener.Actions):
    while True:
        echo = asyncio.run(actions.custom.get_group_list())
        result = Manager.Ret.fetch(echo)

        with open(TIMING_MESSAGE_FILE, "r", encoding="utf-8") as f:
            send_time = f.read()

        send_time = send_time.split("\n")
        send_time = send_time[0].split("⊕")

        now = datetime.datetime.now()
        if f"{now.hour:02}:{now.minute:02}" == send_time[0]:
            print(f"[定时消息] 发送时间到达: {send_time[0]}")
            blacklist = load_blacklist()  # 在发送消息前加载黑名单,防止返回一个sb空集合
            for group in result.data.raw:
                group_id = str(
                    group["group_id"]
                )  # 将group_id转为字符串类型,不然来个error会溶血
                if group_id not in blacklist:  # 检查群组 ID 是否在黑名单中,在就别给lz发
                    asyncio.run(
                        actions.send(
                            group_id=group["group_id"],
                            message=Manager.Message(Segments.Text(send_time[1])),
                        )
                    )
                    time.sleep(random.random() * 3)

        time.sleep(60 - now.second)


def Read_Settings():
    global Super_User, Manage_User, sisters, jhq, programmers
    with open(SUPER_USER_FILE, "r") as f:
        Super_User = f.read().split("\n")
        f.close()
    with open(MANAGE_USER_FILE, "r") as f:
        Manage_User = f.read().split("\n")
        f.close()
    with open(SISTERS_FILE, "r") as f:
        sisters = f.read().split("\n")
        f.close()
    with open(JHQ_FILE, "r") as f:
        jhq = f.read().split("\n")
        f.close()
    try:
        with open(PROGRAMMERS_FILE, "r") as f:
            programmers = f.read().split("\n")
            f.close()
    except FileNotFoundError:
        programmers = []


def Write_Roles(role: str, user_id: int) -> bool:
    global sisters, jhq, programmers
    sisters, jhq, programmers = update_role_lists(
        str(user_id), role, sisters, jhq, programmers
    )
    try:
        with open(SISTERS_FILE, "w") as f:
            f.write("\n".join(sisters))
        with open(JHQ_FILE, "w") as f:
            f.write("\n".join(jhq))
        with open(PROGRAMMERS_FILE, "w") as f:
            f.write("\n".join(programmers))
        return True
    except Exception:
        return False


def Write_Settings(s: list, m: list) -> bool:
    s = [item for item in s if item]
    m = [item for item in m if item]
    global Super_User, Manage_User
    su = ""
    for item in range(len(s)):
        su += s[item]
        if item != len(s) - 1:
            su += "\n"
    ma = ""
    for item in range(len(m)):
        ma += m[item]
        if item != len(m) - 1:
            ma += "\n"

    try:
        with open(SUPER_USER_FILE, "w") as f:
            f.write(su)
            f.close()
        with open(MANAGE_USER_FILE, "w") as f:
            f.write(ma)
            f.close()

        Super_User = s
        Manage_User = m

        return True
    except:
        return False


@Listener.reg
@Logic.ErrorHandler().handle_async
async def handler(event: Events.Event, actions: Listener.Actions) -> None:
    global in_timing, bot_name, bot_name_en, reminder
    if not in_timing:
        Read_Settings()
        in_timing = True
        thread = threading.Thread(target=timing_message, args=(actions,))
        thread.start()

    if isinstance(event, Events.HyperListenerStartNotify):
        if os.path.exists("restart.temp"):
            with open("restart.temp", "r", encoding="utf-7") as f:
                group_id = f.read()
                f.close()
            os.remove("restart.temp")
            await actions.send(
                group_id=group_id,
                message=Manager.Message(
                    Segments.Text(f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Welcome! {bot_name} was restarted successfully. Now you can send {reminder}帮助 to know more.""")
                ),
            )

    if isinstance(event, Events.GroupMemberIncreaseEvent):
        user = event.user_id
        welcome = f""" 加入{bot_name}的大家庭，{bot_name}是你最忠实可爱的女朋友噢o(*≧▽≦)ツ
随时和{bot_name}交流，你只需要在问题的前面加上 {reminder} 就可以啦！( •̀ ω •́ )✧
{bot_name}是你最二次元的好朋友，经常@{bot_name} 看看{bot_name}又学会做什么新事情啦~o((>ω< ))o
祝你在{bot_name}的大家庭里生活愉快！♪(≧∀≦)ゞ☆"""

        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(
                Segments.Image(
                    f"http://q2.qlogo.cn/headimg_dl?dst_uin={user}&spec=640"
                ),
                Segments.Text("欢迎"),
                Segments.At(user),
                Segments.Text(welcome),
            ),
        )

    if isinstance(event, Events.GroupAddInviteEvent):
        keywords: list = Configurator.cm.get_cfg().others["Auto_approval"]
        cleaned_text = event.comment.strip().lower()

        for keyword6 in keywords:
            processed_keyword = keyword6.strip().lower()
            all_chars_present = True
            for char in processed_keyword:
                if char not in cleaned_text:
                    all_chars_present = False
                    break
            if all_chars_present:
                await actions.set_group_add_request(
                    flag=event.flag, sub_type=event.sub_type, approve=True, reason=""
                )
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"用户 {event.user_id} 的答案正确,已自动批准,题目数据为 {event.comment} "
                        )
                    ),
                )
                break

    def execute_command(command):
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, shell=True
            )
            # capture_output=True 捕获输出(stdout/stderr)
            # text=True  解码为文本字符串,可以返回text
            # check=True  当返回非零退出码时引发 CalledProcessError 异常,开不开差不多（）
            # shell=True  允许使用 shell 的特性，不建议开,不然容易溶血

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.CalledProcessError as e:
            return {"stdout": e.stdout, "stderr": e.stderr, "returncode": e.returncode}
        except Exception as e:
            return {"stdout": None, "stderr": str(e), "returncode": -1}

    if isinstance(event, Events.GroupMessageEvent):
        user_message = str(event.message)
        order = ""
        global user_lists
        global sys_prompt
        global second_start
        global EnableNetwork
        global generating
        global Super_User, Manage_User, ROOT_User, sisters, jhq
        global model

        event_user = (await actions.get_stranger_info(event.user_id)).data.raw
        event_user = event_user["nickname"]
        print(event_user)

        # match str(event.message):
        #     case "ping":
        #         await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Text("pong")))
        #     case "/生图 Pixiv":
        #         await actions.send(group_id=event.group_id, message=Manager.Message(Segments.Image("https://pixiv.t.sr-studio.top/img-original/img/2023/01/24/03/53/38/104766095_p0.png")))
        print(event.user_id)
        sys_prompt = select_persona_prompt(event.user_id, event_user)

        if "ping" == user_message:
            print(str(event.user_id))
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text("pong! 爆炸！v(◦'ωˉ◦)~♡ ")),
            )

        elif f"{bot_name}真棒" in user_message:
            i = random.randint(1, 3)
            match i:
                case 1:
                    m = "啊！老……老公，别怎么说啦，人……人家好害羞的啦，人家还会努力的(*ᴗ͈ˬᴗ͈)ꕤ*.ﾟ"
                case 2:
                    m = "啊~老公~你不要这么夸人家啦~〃∀〃"
                case 3:
                    m = "唔……谢……谢谢老公啦🥰~"

            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text(m))
            )

        # not_allowed_word = ["小塑塑真棒", "小塑塑棒不棒"]
        # for item in not_allowed_word:
        #     contains = []
        #     for p in range(len(item)):
        #         if item[p] in user_message:
        #             contains.append("1")
        #     if len(contains) >= len(item):
        #         try:
        #             await actions.del_message(event.message_id)
        #         except:
        #             pass
        #         break

        global emoji_send_count
        if has_emoji(user_message):
            if (
                emoji_send_count is None
                or datetime.datetime.now() - emoji_send_count
                > datetime.timedelta(seconds=15)
            ):
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text(user_message)),
                )
                emoji_send_count = datetime.datetime.now()
            else:
                print(
                    f"emoji +1 延迟 {abs(datetime.datetime.now() - emoji_send_count)} s"
                )

        if user_message.startswith(reminder):
            order_i = user_message.find(reminder)
            if order_i != -1:
                order = user_message[order_i + len(reminder) :].strip()
                print("收到命令 " + order)

        # 检查是否 @ 了机器人，如果是则提取 @ 后面的内容作为命令
        is_at_bot = False
        if len(event.message) >= 1 and isinstance(event.message[0], Segments.At):
            if int(event.message[0].qq) == event.self_id:
                is_at_bot = True
                # 提取 @ 后面的文本内容
                at_content = ""
                for seg in event.message[1:]:
                    if isinstance(seg, Segments.Text):
                        at_content += seg.text
                at_content = at_content.strip()
                if at_content and not order:  # 如果还没有通过 reminder 获取到命令
                    order = at_content
                    print(f"收到@命令 {order}")

        # 快捷命令：直接发送"生图"或"生图 xxx"也可以触发
        if not order and (user_message == "生图" or user_message.startswith("生图 ")):
            order = user_message
            print(f"收到快捷命令 {order}")

        if f"{reminder}重启" == user_message:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text(f"Restarting in progress……")),
                )

                try:
                    with open("restart.temp", "w", encoding="utf-7") as f:
                        f.write(str(event.group_id))
                        f.close()
                except:
                    pass

                Listener.restart()
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif "runcommand " in order:
            blacklist_file = BLACKLIST_FILE

            if (
                str(event.user_id) in Manage_User
                or str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
            ):
                order = order.removeprefix("runcommand").strip()
                order_lower = order.lower()
                print(order_lower)

                # 定义危险命令
                dangerous_commands = [
                    "rm",
                    "vi",
                    "vim",
                    "tsab",
                    "del",
                    "rmdir",
                    "format",
                    "shutdown",
                    "shutdown.exe",
                ]

                # 检查危险命令
                if any(
                    dangerous_cmd in order_lower for dangerous_cmd in dangerous_commands
                ):
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text("❌ ERROR 危险命令，已屏蔽。\nℹ️ INFO None.")
                        ),
                    )
                    return

                match order_lower:
                    case cmd if re.match(r"^scheduled sends.*", cmd):
                        print("使用命令定时")
                        try:
                            send_time = order_lower[
                                order_lower.find("scheduled sends ")
                                + len("scheduled sends ") :
                            ].strip()
                            if not re.match(
                                r"^([01][0-9]|2[0-3]):([0-5][0-9])$", send_time[:5]
                            ):
                                r = f"""命令执行结果:
❌ERROR {bot_name}不能识别给定的时间是什么 Σ( ° △ °|||)︴
ℹ️ INFO 举个🌰子：{reminder}runcommand scheduled sends 00:00 早安 —> 即可让{bot_name}在0点0分准时问候早安噢⌯oᴗo⌯"""
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(Segments.Text(r)),
                                )
                            else:
                                timing_settings = f"{send_time[:5]}⊕{send_time[6::]}"
                                with open(
                                    TIMING_MESSAGE_FILE, "w", encoding="utf-8"
                                ) as f:
                                    f.write(timing_settings)
                                r = f"""命令执行结果:
ℹ️ INFO {bot_name}设置成功！(*≧▽≦) """
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(Segments.Text(r)),
                                )
                        except Exception as e:
                            r = f"""命令执行结果:
❌ERROR {str(type(e))}
❌ERROR {bot_name}设置失败了…… (╥﹏╥)"""
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(Segments.Text(r)),
                            )

                    case "restart":
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(f"""命令执行结果:
⚠️ WARN 正在退出(Ctrl+C) 
ℹ️ INFO 重新启动监听器....""")
                            ),
                        )
                        try:
                            with open("restart.temp", "w", encoding="utf-7") as f:
                                f.write(str(event.group_id))
                        except Exception as e:
                            print(f"Error saving restart info: {e}")
                        Listener.restart()

                    case "message clear":
                        global cmc
                        del cmc
                        cmc = ContextManager()
                        user_lists.clear()
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text("命令执行结果:\nℹ️ INFO 清除完成")
                            ),
                        )

                    case cmd if re.match(r"^set_group_ban.*", cmd):
                        start_index = order_lower.find("set_group_ban")
                        if start_index != -1:
                            result = order[start_index + len("set_group_ban") :].strip()
                            user_and_duration = re.findall(r"\d+", result)
                            if len(user_and_duration) == 2:
                                print("At in loading...")
                                user_id = user_and_duration[0]
                                ban_duration = user_and_duration[1]
                                await actions.set_group_ban(
                                    group_id=event.group_id,
                                    user_id=user_id,
                                    duration=ban_duration,
                                )
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(
                                        Segments.Text(
                                            f"命令执行结果:\nℹ️ INFO 将{user_id}在{event.group_id}中禁言{ban_duration}秒\nℹ️ INFO None."
                                        )
                                    ),
                                )

                    case cmd if re.match(r"^set_group_kick.*", cmd):
                        start_index = order.find("set_group_kick")
                        if start_index != -1:
                            result = order[
                                start_index + len("set_group_kick") :
                            ].strip()
                            user_id = re.search(r"\d+", result).group()
                            await actions.set_group_kick(
                                group_id=event.group_id, user_id=user_id
                            )
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"命令执行结果:\nℹ️ INFO 将{user_id}从{event.group_id}中踢出\nℹ️ INFO None."
                                    )
                                ),
                            )

                    case cmd if re.match(r"^scheduled_sends_black add.*", cmd):
                        black_add_target = order[
                            order.find("scheduled_sends_black add ")
                            + len("scheduled_sends_black add ") :
                        ].strip()
                        print(black_add_target)

                        def load_blacklist():
                            try:
                                with open(blacklist_file, "r", encoding="utf-8") as f:
                                    return set(line.strip() for line in f)
                            except FileNotFoundError:
                                return set()

                        blacklist_content = load_blacklist()
                        if black_add_target not in blacklist_content:
                            blacklist_content.add(black_add_target)
                            try:
                                with open(blacklist_file, "w", encoding="utf-8") as f:
                                    for item in blacklist_content:
                                        f.write(item + "\n")
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(
                                        Segments.Text(
                                            f"命令执行结果:\nℹ️ INFO 黑名單添加成功, 現列表:{', '.join(blacklist_content)}"
                                        )
                                    ),
                                )
                            except Exception as e:
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(
                                        Segments.Text(
                                            f"命令执行结果:\n❌ ERROR 黑名單添加失败, 原因:{e}"
                                        )
                                    ),
                                )
                        else:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"命令执行结果:\n❌ ERROR 黑名單添加失败, 原因:群{black_add_target}已在群发黑名單！"
                                    )
                                ),
                            )

                    case cmd if re.match(r"^scheduled_sends_black del.*", cmd):
                        black_del_target = order[
                            order.find("scheduled_sends_black del ")
                            + len("scheduled_sends_black del ") :
                        ].strip()
                        blacklist_content = load_blacklist()
                        if black_del_target in blacklist_content:
                            blacklist_content.remove(black_del_target)
                            try:
                                with open(blacklist_file, "w", encoding="utf-8") as f:
                                    for item in blacklist_content:
                                        f.write(item + "\n")
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(
                                        Segments.Text(
                                            f"命令执行结果:\nℹ️ INFO 黑名單删除成功, 現列表:{', '.join(blacklist_content)}"
                                        )
                                    ),
                                )
                            except Exception as e:
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(
                                        Segments.Text(
                                            f"命令执行结果:\n❌ ERROR 黑名單删除失败, 原因:{e}"
                                        )
                                    ),
                                )
                        else:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"命令执行结果:\n❌ ERROR 黑名單删除失败, 原因:群{black_del_target}不在群发黑名單！"
                                    )
                                ),
                            )

                    case cmd if re.match(r"^scheduled_sends_black list.*", cmd):
                        blacklist_content = load_blacklist()
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(
                                    f"黑名单列表加载完成: {', '.join(blacklist_content)}"
                                )
                            ),
                        )

                    case _:
                        # 执行用户的命令
                        command_result = execute_command(order)
                        if command_result["returncode"] == 0:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"命令执行结果:\nℹ️ INFO 执行成功\nℹ️ INFO {command_result['stdout']}."
                                    )
                                ),
                            )
                            if command_result["stderr"]:
                                await actions.send(
                                    group_id=event.group_id,
                                    message=Manager.Message(
                                        Segments.Text(
                                            f"命令执行结果:\n❌ ERROR 执行失败, 代码命令可能有误\nℹ️ INFO {command_result['stderr']}."
                                        )
                                    ),
                                )
                        else:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"命令执行结果:\n❌ ERROR 执行失败, 代码命令可能有误\nℹ️ INFO {command_result['stderr']}.\n❌ ERROR 返回码:{command_result['returncode']}."
                                    )
                                ),
                            )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif "读图" in order:
            EnableNetwork = "Pixmap"
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Text(f"{bot_name}打开了新视界！o(*≧▽≦)ツ")
                ),
            )
        elif "列出黑名单" in order:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                try:
                    with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
                        blacklist1 = set(line.strip() for line in f)
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(f"黑名单列表加载完成: {blacklist1}")
                            ),
                        )
                except FileNotFoundError:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text("黑名单列表加载失败,原因:没有文件")
                        ),
                    )
                except UnicodeDecodeError:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text("黑名单列表加载失败,原因:解码失败")
                        ),
                    )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )
        elif "添加黑名单 " in order:
            blacklist_file = BLACKLIST_FILE

            def load_blacklist():
                try:
                    with open(blacklist_file, "r", encoding="utf-8") as f:
                        blacklist115 = set(
                            line.strip() for line in f
                        )  # 使用集合方便快速查找,不然容易溶血
                    return blacklist115
                except FileNotFoundError:
                    return set()

            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                Toset2 = order[order.find("添加黑名单 ") + len("添加黑名单 ") :].strip()
                blacklist114 = load_blacklist()  # 加载现有的黑名单,防止已修改沒更新
                if Toset2 not in blacklist114:
                    blacklist114.add(Toset2)
                    try:
                        with open(blacklist_file, "w", encoding="utf-8") as f:
                            for item in blacklist114:
                                f.write(item + "\n")  # 防止之前的丟失555，并添加换行符
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(f"黑名單添加成功,現列表:{blacklist114}")
                            ),
                        )

                    except Exception as e:
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(f"黑名單添加失败,原因:{e}")
                            ),
                        )
                else:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text(f"黑名單添加失败,原因:群{Toset2}已在黑名單！")
                        ),
                    )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )
        elif "删除黑名单 " in order:
            blacklist_file = BLACKLIST_FILE

            def load_blacklist():
                try:
                    with open(blacklist_file, "r", encoding="utf-8") as f:
                        blacklist116 = set(
                            line.strip() for line in f
                        )  # 使用集合方便快速查找,不然容易溶血
                    return blacklist116
                except FileNotFoundError:
                    return set()

            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                Toset1 = order[order.find("删除黑名单 ") + len("删除黑名单 ") :].strip()
                blacklist117 = load_blacklist()  # 加载现有的黑名单,防止已修改沒更新
                if Toset1 in blacklist117:
                    blacklist117.remove(Toset1)
                    try:
                        with open(blacklist_file, "w", encoding="utf-8") as f:
                            for item in blacklist117:
                                f.write(item + "\n")  # 防止之前的丟失555，并添加换行符
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(f"黑名單刪除成功,現列表:{blacklist117}")
                            ),
                        )
                    except Exception as e:
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(f"黑名單刪除失败,原因:{e}")
                            ),
                        )
                else:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text(f"黑名單刪除失败,原因:群{Toset1}不在黑名單！")
                        ),
                    )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif "删除管理 " in order:
            r = ""
            if str(event.user_id) in Super_User or str(event.user_id) in ROOT_User:
                Toset = order[order.find("删除管理 ") + len("删除管理 ") :].strip()
                s = Super_User
                m = Manage_User
                if Toset in ROOT_User:
                    r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: The specified user is a ROOT_User and group ROOT_User is read only."""
                else:
                    if Toset in s:
                        s.remove(Toset)
                    if Toset in m:
                        m.remove(Toset)

                    if Write_Settings(s, m):
                        r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Succeeded: @{Toset} is a Common User now.
Now use {reminder}帮助 to know what permissions you have now."""
                    else:
                        r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: Settings files are not writeable."""
            else:
                r = f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"

            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text(r))
            )

        elif "管理 " in order:
            r = ""
            if str(event.user_id) in Super_User or str(event.user_id) in ROOT_User:
                if "管理 M " in order:
                    Toset = order[order.find("管理 M ") + len("管理 M ") :].strip()
                    print(f"try to get_user {Toset}")
                    nikename = (
                        await actions.get_stranger_info(Toset, no_cache=True)
                    ).data.raw
                    print(str(nikename))
                    if len(nikename) == 0:
                        r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: {Toset} is not a valid user."""
                    else:
                        nikename = nikename["nickname"]
                        m = Manage_User
                        s = Super_User
                        if Toset in Manage_User:
                            r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Succeeded: {nikename}(@{Toset}) has become a Manage_User."""
                        elif Toset in Super_User:
                            s.remove(Toset)
                            m.append(Toset)
                            if Write_Settings(s, m):
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Succeeded: {nikename}(@{Toset}) has become a Manage_User.
Now use {reminder}帮助 to know what permissions you have now."""
                            else:
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: Settings files are not writeable."""
                        elif Toset in ROOT_User:
                            r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: The specified user is a ROOT_User and group ROOT_User is read only."""
                        else:
                            m.append(Toset)
                            if Write_Settings(s, m):
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Succeeded: {nikename}(@{Toset}) has become a Manage_User.
Now use {reminder}帮助 to know what permissions you have now."""
                            else:
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: Settings files are not writeable."""

                elif "管理 S " in order:
                    Toset = order[order.find("管理 S ") + len("管理 S ") :].strip()
                    print(f"try to get_user {Toset}")
                    nikename = (
                        await actions.get_stranger_info(Toset, no_cache=True)
                    ).data.raw
                    print(str(nikename))
                    if len(nikename) == 0:
                        r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: {Toset} is not a valid user."""
                    else:
                        nikename = nikename["nickname"]
                        m = Manage_User
                        s = Super_User
                        if Toset in Manage_User:
                            m.remove(Toset)
                            s.append(Toset)
                            if Write_Settings(s, m):
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Succeeded: {nikename}(@{Toset}) has become a Super_User.
Now use {reminder}帮助 to know what permissions you have now."""
                            else:
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: Settings files are not writeable."""
                        elif Toset in Super_User:
                            r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Succeeded: {nikename}(@{Toset}) has become a Super_User."""
                        elif Toset in ROOT_User:
                            r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: The specified user is a ROOT_User and group ROOT_User is read only."""
                        else:
                            s.append(Toset)
                            if Write_Settings(s, m):
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Succeeded: {nikename}(@{Toset}) has become a Super_User.
Now use {reminder}帮助 to know what permissions you have now."""
                            else:
                                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: Settings files are not writeable."""

                else:
                    r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: Only Manage_User or Super_User could be set."""

            else:
                r = f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"

            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text(r))
            )
        elif "让我访问" in order:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
sisters: {sisters}
————————————————————
Manage_User: {Manage_User}
Super_User: {Super_User}
ROOT_User: {ROOT_User}
If you are a Super_User or ROOT_User, you can manage these users. Use {reminder}帮助 to know more."""
            else:
                r = f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text(r))
            )
        elif "帮助" in order:
            if str(event.user_id) in ROOT_User or str(event.user_id) in Super_User:
                content = f"""管理我们的{bot_name}
————————————————————
你拥有管理{bot_name}的权限。若要查看普通帮助，请@{bot_name}
    1. {reminder}让我访问 —> 检索用有权限的用户
    2. {reminder}管理 M (QQ号，必填) —> 为用户添加 Manage_User 权限
    3. {reminder}管理 S (QQ号，必填) —> 为用户添加 Super_User 权限
    4. {reminder}删除管理 (QQ号，必填) —> 删除这个用户的全部权限
    5. {reminder}禁言 (@QQ+空格+时间(以秒为单位)，必填) —> 禁言用户一段时间
    6. {reminder}解禁 (@QQ，必填) —> 解除该用户禁言
    7. {reminder}踢出 (@QQ，必填) —> 将该用户踢出聊群
    8. 撤回 (引用一条消息) —> 撤回该消息
    9. {reminder}注销 —> 删除所有用户的上下文
    10. {reminder}修改 (hh:mm) (内容，必填) —> 改变定时消息时间与内容
    11. {reminder}感知 —> 查看运行状态
    12. {reminder}核验 (QQ号，必填) —> 检索QQ账号信息
    13. {reminder}重启 —> 关闭所有线程和进程，关闭{bot_name}。然后重新启动{bot_name}。
    14. {reminder}添加黑名单 +空格 + 群号 —> 将该群加入群发黑名单
    15. {reminder}删除黑名单 +空格 + 群号 —> 将该群移除群发黑名单
    16. {reminder}列出黑名单 —> 列出黑名单中的所有群
你的每一步操作，与用户息息相关。"""
            elif str(event.user_id) in Manage_User:
                content = f"""管理我们的{bot_name}
————————————————————
你拥有管理{bot_name}的权限。若要查看普通帮助，请@{bot_name}
    1. {reminder}让我访问 —> 检索用有权限的用户
    2. {reminder}注销 —> 删除所有用户的上下文
    3. {reminder}修改 (hh:mm) (内容，必填) —> 改变定时消息时间与内容
    4. {reminder}感知 —> 查看运行状态
    5. {reminder}核验 (QQ号，必填) —> 检索QQ账号信息
    6. {reminder}重启 —> 关闭所有线程和进程，关闭{bot_name}。然后重新启动{bot_name}
    7. {reminder}禁言 (@QQ+空格+时间(以秒为单位)，必填) —> 禁言用户一段时间
    8. {reminder}解禁 (@QQ，必填) —> 解除该用户禁言
    9. {reminder}踢出 (@QQ，必填) —> 将该用户踢出聊群
    10. 撤回 (引用一条消息) —> 撤回该消息
    11. {reminder}添加黑名单 +空格 + 群号 —> 将该群加入群发黑名单
    12. {reminder}删除黑名单 +空格 + 群号 —> 将该群移除群发黑名单
    13. {reminder}列出黑名单 —> 列出黑名单中的所有群
    你的每一步操作，与用户息息相关。"""
            else:
                p = " "
                n = " "
                r = " "
                match EnableNetwork:
                    case "Pixmap":
                        p = "（当前）"
                    case "Normal":
                        r = "（当前）"
                    case "Net":
                        n = "（当前）"

                content = f"""如何与{bot_name}交流( •̀ ω •́ )✧
    注：对话前必须加上 {reminder} 或者直接 @{bot_name} 噢！~
    1. {reminder}(任意问题) 或 @{bot_name} (任意问题) —> {bot_name}回复
    2. {reminder}名言【引用一条消息】 —> {bot_name}将消息载入史册
    3. {reminder}读图{p}—> {bot_name}可以查看您发送的图片
    4. {reminder}大头照 【@一个用户】—> {bot_name}给他拍张大头照
    5. 生图 / 生图 白丝/猫娘/初音/雷姆/JK —> {bot_name}获取Pixiv精美图片（支持标签搜索）
    6. {reminder}做我姐姐吧 / {reminder}当我女朋友（默认）/ {reminder}做我mm吧 —> {bot_name}切换不同的角色互动噢！~
    7. 撤回【引用一条消息】—> {bot_name}撤回该消息（需要管理权限）
快来聊天吧(*≧︶≦)"""

            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text(content))
            )
        elif (
            isinstance(event.message[0], Segments.At)
            and int(event.message[0].qq) == event.self_id
            and not order  # 只有在没有命令内容时才显示帮助
        ):
            p = " "
            match EnableNetwork:
                case "Pixmap":
                    p = "（当前）"

            content = f"""如何与{bot_name}交流( •̀ ω •́ )✧
    注：对话前必须加上 {reminder} 或者直接 @{bot_name} 噢！~
    1. {reminder}(任意问题) 或 @{bot_name} (任意问题) —> {bot_name}回复
    2. {reminder}名言【引用一条消息】 —> {bot_name}将消息载入史册
    3. {reminder}读图{p}—> {bot_name}可以查看您发送的图片
    4. {reminder}大头照 【@一个用户】—> {bot_name}给他拍张大头照
    5. 生图 / 生图 白丝/猫娘/初音/雷姆/JK —> {bot_name}获取Pixiv精美图片（支持标签搜索）
    6. {reminder}做我姐姐吧 / {reminder}当我女朋友（默认）/ {reminder}做我mm吧 —> {bot_name}切换不同的角色互动噢！~
    7. 撤回【引用一条消息】—> {bot_name}撤回该消息（需要管理权限）
快来聊天吧(*≧︶≦)"""
            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text(content))
            )

        elif "关于" in order:
            global version_name
            about = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Build Information
Version：{version_name}
Powered by NapCat.OneBot
Rebuilt from HypeR
————————————————————
Third-party API
1. Mirokoi API
2. Lolicon API
2. LoliAPI API
4. ChatGPT gpt-5.1
5. ChatGPT gpt-5.1
6. Google gemini-2.5-flash
————————————————————
Copyright
Made by SR Studio
2019~2025 All rights reserved"""
            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text(about))
            )

        elif "当我女朋友" in order:
            try:
                if not Write_Roles("girlfriend", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text("老公~你回来啦~(*≧︶≦)")),
                )
            except Exception as e:
                print(traceback.format_exc)
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"可是{bot_name}还想继续做你的姐姐，这样我就可以保护你了！(๑•̀ㅂ•́)و✧"
                        )
                    ),
                )

        elif "做我姐姐吧" in order:
            try:
                if not Write_Roles("sister", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text("你好呀！妹妹！~o(*≧▽≦)ツ")),
                )
            except Exception as e:
                print(traceback.format_exc)
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"呜呜呜……{bot_name}还想继续做你的女朋友，依赖你 (*/ω＼*)"
                        )
                    ),
                )

        elif "做我mm吧" in order:
            try:
                if not Write_Roles("mother", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text("你好呀！血小板！~o(*≧▽≦)ツ")
                    ),
                )
            except Exception as e:
                print(traceback.format_exc)
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"呜呜呜……{bot_name}还想继续做你的女朋友，依赖你 (*/ω＼*)"
                        )
                    ),
                )

        elif "程序员" in order:
            try:
                if not Write_Roles("programmer", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text("已切换到高级程序员模式。")),
                )
            except Exception:
                print(traceback.format_exc())
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text("切换高级程序员模式失败，请稍后再试。")
                    ),
                )

        elif "核验 " in order:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                uid = order[order.find("核验 ") + len("核验 ") :].strip()
                print(f"try to get_user {uid}")
                nikename = (await actions.get_stranger_info(uid)).data.raw
                print(f"get {nikename} successfully")
                if len(nikename) == 0:
                    r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Failed: {uid} is not a valid user."""
                else:
                    items = [f"{key}: {value}" for key, value in nikename.items()]
                    result = "\n".join(items)
                    r = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
{result}"""
                await actions.send(
                    group_id=event.group_id, message=Manager.Message(Segments.Text(r))
                )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif f"{reminder}感知" in str(event.message):
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                system_info = get_system_info()
                feel = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
System Now
Running {seconds_to_hms(round(time.time() - second_start, 2))}
Syetem Version：{system_info["version_info"]}
Architecture：{system_info["architecture"]}
CPU Usage：{str(system_info["cpu_usage"]) + "%"}
Memory Usage：{str(system_info["memory_usage_percentage"]) + "%"}"""
                for i, usage in enumerate(system_info["gpu_usage"]):
                    feel = feel + f"\nGPU {i} Usage：{usage * 100:.2f}%"
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text(feel)),
                )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif f"{reminder}注销" in str(event.message):
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                #   global cmc
                del cmc
                cmc = ContextManager()
                user_lists.clear()
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(f"卸下包袱，{bot_name}更轻松了~ (/≧▽≦)/")
                    ),
                )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif f"{reminder}名言" in str(event.message):
            print("获取名言")
            imageurl = None

            if isinstance(event.message[0], Segments.Reply):
                print("有消息反馈")
                msg_id = event.message[0].id
                content = await actions.get_msg(msg_id)
                message = content.data["message"]
                message = gen_message({"message": message})
                print("有引用消息")
                for i in message:
                    print(type(i))
                    print(str(i))
                    if isinstance(i, Segments.Image):
                        print("应该有图")
                        if i.file.startswith("http"):
                            imageurl = i.file
                        else:
                            imageurl = i.url

                quoteimage = await Quote.handle(event.message, actions, imageurl)
                print("制作名言")
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Reply(event.message_id), quoteimage
                    ),
                )
                os.remove("./temps/quote.png")
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Reply(event.message_id),
                        Segments.Text("在记录一条名言之前先引用一条消息噢 ☆ヾ(≧▽≦*)o"),
                    ),
                )

        elif f"{reminder}生成" in str(event.message):
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Image(
                        "https://gchat.qpic.cn/gchatpic_new/0/0-0-615ECBFE6A1B895F3D2B21544109FE1F/0"
                    )
                ),
            )

        elif "修改 " in order:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                try:
                    tm = order[order.find("修改 ") + len("修改 ") :].strip()
                    if not bool(re.match(r"^([01][0-9]|2[0-3]):([0-5][0-9])$", tm[:5])):
                        r = f"""{bot_name}不能识别给定的时间是什么 Σ( ° △ °|||)︴
        举个🌰子：{reminder}修改 00:00 早安 —> 即可让{bot_name}在0点0分准时问候早安噢⌯oᴗo⌯"""
                    else:
                        timing_settings = f"{tm[:5]}⊕{tm[6::]}"
                        with open(TIMING_MESSAGE_FILE, "w", encoding="utf-8") as f:
                            f.write(timing_settings)
                            f.close()
                        r = f"{bot_name}设置成功！(*≧▽≦) "
                except Exception as e:
                    r = f"""{str(type(e))}
{bot_name}设置失败了…… (╥﹏╥)"""
                await actions.send(
                    group_id=event.group_id, message=Manager.Message(Segments.Text(r))
                )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif f"{reminder}生草" in str(event.message):
            await actions.send(
                group_id=event.group_id, message=Manager.Message(Segments.Text("🌿"))
            )

        elif order == "生图" or "生图 " in order:
            # 统一生图命令：- 生图 <标签> 或直接 生图
            # 使用鸭子API (mossia.top) - Pixiv/X 图源
            if "生图 " in order:
                start_index = order.find("生图 ")
                result = order[start_index + len("生图 ") :].strip().lower()
            else:
                result = ""  # 没有参数时默认随机

            selfID = await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Text(f"{bot_name}正在生成图片 ヾ(≧▽≦*)o")
                ),
            )

            user_id = event.user_id
            current_time = time.time()

            if user_id in cooldowns and current_time - cooldowns[user_id] < 18:
                if not (
                    str(event.user_id) in Super_User
                    or str(event.user_id) in ROOT_User
                    or str(event.user_id) in Manage_User
                ):
                    time_remaining = 18 - (current_time - cooldowns[user_id])
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text(
                                f"18秒个人cd，请等待 {time_remaining:.1f} 秒后重试"
                            )
                        ),
                    )
                    return

            # 根据标签选择 API 类型
            # 鸭子API (mossia.top) 支持：Pixiv图源、X图源、R18筛选
            # Lolicon API 支持：标签搜索
            use_x_source = False  # 是否使用X图源
            use_tag_search = False  # 是否使用标签搜索
            search_tag = ""  # 搜索标签
            type_name = "Pixiv"
            post_data = {"num": 1}  # POST请求参数

            # 中文标签到英文标签的映射（热门角色和类型）
            tag_mapping = {
                # 丝袜类
                "白丝": "white_stockings|白タイツ",
                "黑丝": "black_stockings|黒タイツ",
                "丝袜": "pantyhose|パンスト",
                "裸足": "barefoot",
                "足控": "feet",
                # 猫娘/兽耳
                "猫娘": "cat_girl|猫耳|neko",
                "猫耳": "cat_ears|猫耳",
                "狐娘": "fox_girl|狐耳",
                "兔女郎": "bunny_girl|バニーガール",
                "兽耳": "animal_ears|獣耳",
                # VOCALOID
                "初音": "hatsune_miku|初音ミク",
                "初音未来": "hatsune_miku|初音ミク",
                "miku": "hatsune_miku|初音ミク",
                "洛天依": "luo_tianyi|洛天依",
                # 原神
                "甘雨": "ganyu|甘雨",
                "刻晴": "keqing|刻晴",
                "胡桃": "hu_tao|胡桃",
                "雷电将军": "raiden_shogun|雷電将軍",
                "神里绫华": "kamisato_ayaka|神里綾華",
                "纳西妲": "nahida|ナヒーダ",
                "芙宁娜": "furina|フリーナ",
                "莫娜": "mona|モナ",
                "优菈": "eula|エウルア",
                # 蓝色档案
                "蓝档": "blue_archive|ブルーアーカイブ",
                "爱丽丝": "aris|アリス",
                # 明日方舟
                "明日方舟": "arknights|アークナイツ",
                "阿米娅": "amiya|アーミヤ",
                # Re:Zero
                "雷姆": "rem|レム",
                "拉姆": "ram|ラム",
                "艾米莉亚": "emilia|エミリア",
                # 其他热门
                "友利奈绪": "tomori_nao|友利奈緒",
                "02": "zero_two|ゼロツー",
                "亚丝娜": "asuna|アスナ",
                "小鸟游六花": "takanashi_rikka|小鳥遊六花",
                "五河琴里": "itsuka_kotori|五河琴里",
                "时崎狂三": "tokisaki_kurumi|時崎狂三",
                "四糸乃": "yoshino|四糸乃",
                "两仪式": "ryougi_shiki|両儀式",
                "远坂凛": "tohsaka_rin|遠坂凛",
                "间桐樱": "matou_sakura|間桐桜",
                "saber": "saber|セイバー",
                # 服装类型
                "jk": "school_uniform|JK",
                "女仆": "maid|メイド",
                "泳装": "swimsuit|水着",
                "比基尼": "bikini|ビキニ",
                "旗袍": "china_dress|チャイナドレス",
                "和服": "kimono|着物",
                "婚纱": "wedding_dress|ウェディングドレス",
                "护士": "nurse|ナース",
                # 身体特征
                "巨乳": "large_breasts|巨乳",
                "贫乳": "flat_chest|貧乳",
                "白发": "white_hair|白髪",
                "银发": "silver_hair|銀髪",
                "金发": "blonde_hair|金髪",
                "黑发": "black_hair|黒髪",
                "双马尾": "twintails|ツインテール",
                "马尾": "ponytail|ポニーテール",
                # 场景/姿势
                "湿身": "wet",
                "睡姿": "sleeping",
                "趴着": "on_stomach",
                "躺着": "lying",
            }

            # 预设类型关键词
            preset_keywords = [
                "x",
                "推特",
                "twitter",
                "r18",
                "涩图",
                "色图",
                "涩涩",
                "ai",
                "非ai",
                "人工",
                "横图",
                "电脑",
                "pc",
                "竖图",
                "手机",
                "mobile",
                "安全",
                "sfw",
                "全年龄",
                "随机",
            ]

            # 检查是否匹配预设类型
            is_preset = any(kw in result for kw in preset_keywords) if result else True

            if "x" in result or "推特" in result or "twitter" in result:
                use_x_source = True
                type_name = "X(Twitter)"
            elif (
                "r18" in result
                or "涩图" in result
                or "色图" in result
                or "涩涩" in result
            ):
                post_data["r18Type"] = 1  # R18内容
                type_name = "R18"
            elif "ai" in result and "非" not in result and is_preset:
                post_data["aiType"] = 2  # AI作品
                type_name = "AI绘画"
            elif "非ai" in result or "人工" in result:
                post_data["aiType"] = 1  # 非AI作品
                type_name = "人工绘画"
            elif "横图" in result or "电脑" in result or "pc" in result:
                post_data["imageSizeType"] = 1  # 横图
                type_name = "横向壁纸"
            elif "竖图" in result or "手机" in result or "mobile" in result:
                post_data["imageSizeType"] = 2  # 竖图
                type_name = "竖向壁纸"
            elif "安全" in result or "sfw" in result or "全年龄" in result:
                post_data["r18Type"] = 0  # 非R18内容
                type_name = "全年龄"
            elif result and not is_preset:
                # 非预设关键词，使用标签搜索
                use_tag_search = True
                # 检查是否有中文标签映射
                search_tag = result
                display_tag = result
                for cn_tag, en_tag in tag_mapping.items():
                    if cn_tag in result.lower():
                        search_tag = en_tag
                        display_tag = cn_tag
                        break
                type_name = f"标签:{display_tag}"
            else:
                type_name = "Pixiv随机"

            # 选择API端点
            if use_tag_search:
                # 使用 Lolicon API 进行标签搜索
                api_url = f"https://api.lolicon.app/setu/v2?tag={search_tag}&num=1"
                print(f"请求 Lolicon API: {api_url}, 标签: {search_tag}")

                request = None
                for retry in range(3):
                    try:
                        print(f"请求 API (尝试 {retry + 1}/3)...")
                        response = requests.get(api_url, timeout=15)
                        request = response.json()
                        if request.get("error") == "" and request.get("data"):
                            break
                    except Exception as e:
                        print(f"请求失败: {e}")
                        if retry == 2:
                            request = None

                print("请求完成")

                if (
                    request is None
                    or request.get("error") != ""
                    or not request.get("data")
                ):
                    await actions.del_message(selfID.data.message_id)
                    error_msg = (
                        request.get("error", "未找到相关图片")
                        if request
                        else "请求超时"
                    )
                    if not error_msg:
                        error_msg = "未找到相关图片"
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text(
                                f"{bot_name}没找到「{search_tag}」相关的图片，换个关键词试试吧 ＞﹏＜\n提示：可以尝试英文标签如 cat_girl, miku 等"
                            )
                        ),
                    )
                else:
                    img_data = request["data"][0]
                    url = img_data.get("urls", {}).get("original", "")
                    title = img_data.get("title", "")
                    author = img_data.get("author", "")
                    pid = img_data.get("pid", "")
                    width = img_data.get("width", "未知")
                    height = img_data.get("height", "未知")
                    tags = img_data.get("tags", [])[:5]  # 取前5个标签
                    is_r18 = img_data.get("r18", False)

                    info = f"{type_name} | {width}x{height}"
                    if title:
                        info += f"\n标题: {title}"
                    if author:
                        info += f" | 作者: {author}"
                    if is_r18:
                        info += " | R18"
                    if tags:
                        info += f"\n标签: {', '.join(tags[:3])}"
                    if pid:
                        info += f"\nPID: {pid}"

                    print(f"图片URL: {url}")

                    if url:
                        # 下载并压缩图片，避免大图导致超时
                        compressed_base64 = await download_and_compress_image(url)
                        if compressed_base64:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Image(f"base64://{compressed_base64}"),
                                    Segments.Text(info),
                                ),
                            )
                            await actions.del_message(selfID.data.message_id)
                            cooldowns[user_id] = current_time
                        else:
                            # 压缩失败，尝试直接发送原图
                            print("压缩失败，尝试直接发送原图")
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Image(url), Segments.Text(info)
                                ),
                            )
                            await actions.del_message(selfID.data.message_id)
                            cooldowns[user_id] = current_time
                    else:
                        await actions.del_message(selfID.data.message_id)
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(
                                    f"{bot_name}生图失败了，再试一次吧 ＞﹏＜"
                                )
                            ),
                        )
            elif use_x_source:
                api_url = x_api_url
            else:
                api_url = pixiv_api_url

            # 非标签搜索时使用鸭子API
            if not use_tag_search:
                print(f"请求 API: {api_url}, 类型: {type_name}, 参数: {post_data}")

                # 重试机制
                request = None
                for retry in range(3):
                    try:
                        print(f"请求 API (尝试 {retry + 1}/3)...")
                        response = requests.post(
                            api_url,
                            json=post_data,
                            headers={"Content-Type": "application/json"},
                            timeout=15,
                        )
                        request = response.json()
                        if request.get("success") == True:
                            break
                    except Exception as e:
                        print(f"请求失败: {e}")
                        if retry == 2:
                            request = None

                print("请求完成")

                if request is None or not request.get("success"):
                    await actions.del_message(selfID.data.message_id)
                    error_msg = (
                        request.get("message", "未知错误") if request else "请求超时"
                    )
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text(
                                f"{bot_name}无法访问接口了({error_msg})，请稍后重试 ε(┬┬﹏┬┬)3"
                            )
                        ),
                    )
                else:
                    data_list = request.get("data", [])
                    if data_list and len(data_list) > 0:
                        img_data = data_list[0]

                        # 根据图源类型获取图片URL
                        if use_x_source:
                            # X图源格式
                            url = img_data.get("pictureUrl", "")
                            info = f"{type_name} | 来源: X"
                        else:
                            # Pixiv图源格式
                            urls_list = img_data.get("urlsList", [])
                            url = urls_list[0].get("url", "") if urls_list else ""
                            width = img_data.get("width", "未知")
                            height = img_data.get("height", "未知")
                            title = img_data.get("title", "")
                            author = img_data.get("author", "")
                            pid = img_data.get("pid", "")
                            ai_type = img_data.get("aiType", 0)
                            ai_label = (
                                "AI"
                                if ai_type == 2
                                else ("非AI" if ai_type == 1 else "")
                            )

                            info = f"{type_name} | {width}x{height}"
                            if title:
                                info += f"\n标题: {title}"
                            if author:
                                info += f" | 作者: {author}"
                            if ai_label:
                                info += f" | {ai_label}"
                            if pid:
                                info += f"\nPID: {pid}"

                        print(f"图片URL: {url}")

                        if url:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Image(url), Segments.Text(info)
                                ),
                            )
                            await actions.del_message(selfID.data.message_id)
                            cooldowns[user_id] = current_time
                        else:
                            await actions.del_message(selfID.data.message_id)
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"{bot_name}生图失败了，再试一次吧 ＞﹏＜"
                                    )
                                ),
                            )
                    else:
                        await actions.del_message(selfID.data.message_id)
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(
                                Segments.Text(
                                    f"{bot_name}没有找到符合条件的图片，换个关键词试试吧 ＞﹏＜"
                                )
                            ),
                        )

        elif "enc解密" in order:
            try:
                start_index = order.find("enc解密")
                if start_index != -1:
                    encoded_part = order[start_index + len("enc解密") :].strip()

                    if not encoded_part:
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(Segments.Text("您没有发送密文")),
                        )
                        return

                    base64_decoded = base64.b64decode(encoded_part).decode("utf-8")

                    url_decoded = urllib.parse.unquote(base64_decoded)

                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text(f"解密结果: {str(url_decoded)}")
                        ),
                    )
                else:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(Segments.Text("没有参数。")),
                    )
            except Exception as e:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text(f"解密失败: {str(e)}")),
                )

        elif "大头照" in order:
            uin = ""

            for i in event.message:
                print(type(i))
                print(str(i))
                if isinstance(i, Segments.At):
                    print("At in loading...")
                    uin = i.qq

            if uin == "":
                uin = event.user_id

            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.Image(
                        f"http://q2.qlogo.cn/headimg_dl?dst_uin={uin}&spec=640"
                    )
                ),
            )

        elif "禁言" in order:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                try:
                    start_index = order.find("禁言")
                    if start_index != -1:
                        result = order[start_index + len("禁言") :].strip()
                        numbers = re.findall(r"\d+", result)
                        complete = False
                        for i in event.message:
                            if isinstance(i, Segments.At):
                                print("At in loading...")
                                userid114 = numbers[0]
                                time114 = numbers[1]
                                await actions.set_group_ban(
                                    group_id=event.group_id,
                                    user_id=userid114,
                                    duration=time114,
                                )
                                complete = True
                                break

                        if not complete:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"管理员：你的格式有误。\n格式：{reminder}禁言 @anyone (seconds of duration)\n参考：{reminder}禁言 @Harcic#8042 128"
                                    )
                                ),
                            )
                        else:
                            await actions.send(
                                group_id=event.group_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"管理员：已禁言，时长 {time114} 秒。"
                                    )
                                ),
                            )

                except Exception as e:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Text(
                                f"管理员：你的格式有误。\n格式：{reminder}禁言 @anyone (seconds of duration)\n参考：{reminder}禁言 @Harcic#8042 128"
                            )
                        ),
                    )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif "解禁" in order:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                start_index = order.find("解禁")
                if start_index != -1:
                    result = order[start_index + len("解禁") :].strip()
                    numbers = re.findall(r"\d+", result)
                    for i in event.message:
                        if isinstance(i, Segments.At):
                            print("At in loading...")
                            userid114 = numbers[0]
                            time114 = 0
                            await actions.set_group_ban(
                                group_id=event.group_id,
                                user_id=userid114,
                                duration=time114,
                            )

            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif "踢出" in order:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                for i in event.message:
                    print(type(i))
                    print(str(i))
                    if isinstance(i, Segments.At):
                        print("At in loading...")
                        await actions.set_group_kick(
                            group_id=event.group_id, user_id=i.qq
                        )
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        elif "撤回" == user_message:
            if (
                str(event.user_id) in Super_User
                or str(event.user_id) in ROOT_User
                or str(event.user_id) in Manage_User
            ):
                if isinstance(event.message[0], Segments.Reply):
                    try:
                        await actions.del_message(event.message[0].id)
                    except:
                        pass
            else:
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"不能这么做！那是一块丞待开发的禁地，可能很危险，{bot_name}很胆小……꒰>﹏< ꒱"
                        )
                    ),
                )

        else:
            if len(order) >= 2:
                url = ""
                try:
                    match EnableNetwork:
                        case "Pixmap":
                            # search_tool = FunctionDeclaration(
                            #     name="google_search_retrieval",
                            #     description="利用 Google 搜索来检索信息",
                            #     parameters={
                            #         "type": "object",
                            #         "properties": {
                            #             "query": {
                            #                 "type": "string",
                            #                 "description": str(user_message),
                            #             }
                            #         },
                            #     },
                            # )

                            model = genai.GenerativeModel(
                                model_name=default_model,
                                generation_config=generation_config,
                                system_instruction=sys_prompt or None,
                                # tools=[search_tool]
                                # tools="code_execution
                            )

                            new = []

                            if isinstance(event.message[0], Segments.Reply):
                                print("有消息反馈")
                                msg_id = event.message[0].id
                                content = await actions.get_msg(msg_id)
                                message = content.data["message"]
                                message = gen_message({"message": message})
                                print("有引用消息")
                                for i in message:
                                    if isinstance(i, Segments.Text):
                                        new.append(
                                            Parts.Text(i.text.replace(reminder, "", 1))
                                        )
                                    elif isinstance(i, Segments.Image):
                                        if i.file.startswith("http"):
                                            url = i.file
                                        else:
                                            url = i.url
                                        try:
                                            new.append(Parts.File.upload_from_url(url))
                                            print("有图")
                                        except Exception as img_err:
                                            print(f"图片下载失败: {img_err}")
                                            new.append(Parts.Text("[图片下载失败]"))
                                    elif isinstance(i, Segments.MarketFace):
                                        # 商城表情包
                                        url = get_market_face_url(i.face_id)
                                        try:
                                            new.append(Parts.File.upload_from_url(url))
                                            print("有表情包")
                                        except Exception as img_err:
                                            print(f"表情包下载失败: {img_err}")
                                            new.append(Parts.Text("[表情包下载失败]"))

                            for i in event.message:
                                if isinstance(i, Segments.Text):
                                    new.append(
                                        Parts.Text(i.text.replace(reminder, "", 1))
                                    )
                                elif isinstance(i, Segments.Image):
                                    if i.file.startswith("http"):
                                        url = i.file
                                    else:
                                        url = i.url
                                    try:
                                        new.append(Parts.File.upload_from_url(url))
                                        print("有图")
                                    except Exception as img_err:
                                        print(f"图片下载失败: {img_err}")
                                        new.append(Parts.Text("[图片下载失败]"))
                                elif isinstance(i, Segments.MarketFace):
                                    # 商城表情包
                                    url = get_market_face_url(i.face_id)
                                    try:
                                        new.append(Parts.File.upload_from_url(url))
                                        print("有表情包")
                                    except Exception as img_err:
                                        print(f"表情包下载失败: {img_err}")
                                        new.append(Parts.Text("[表情包下载失败]"))

                            new = Roles.User(*new)
                            try:
                                result = (
                                    cmc.get_context(event.user_id, event.group_id)
                                    .gen_content(new)
                                    .rstrip("\n")
                                )
                            except Exception as primary_error:
                                print(f"[主模型失败] {default_model}: {primary_error}")
                                print(f"[切换候补模型] {fallback_model}")
                                # 使用候补模型重试
                                genai.configure(
                                    api_key=fallback_key, base_url=gemini_base_url
                                )
                                model = genai.GenerativeModel(
                                    model_name=fallback_model,
                                    generation_config=generation_config,
                                    system_instruction=sys_prompt or None,
                                )
                                cmc.groups.clear()  # 清空上下文重新创建
                                result = (
                                    cmc.get_context(event.user_id, event.group_id)
                                    .gen_content(new)
                                    .rstrip("\n")
                                )
                                # 恢复主模型配置
                                genai.configure(api_key=key, base_url=gemini_base_url)

                        case "Normal":
                            search = SearchOnline(
                                sys_prompt,
                                order,
                                user_lists,
                                event.user_id,
                                fallback_model,
                                bot_name,
                                Configurator.cm.get_cfg().others["openai_key"],
                                Configurator.cm.get_cfg().others.get("openai_base_url"),
                            )
                            ulist, result = search.Response()
                            user_lists = ulist

                        case "Net":
                            search = SearchOnline(
                                sys_prompt,
                                order,
                                user_lists,
                                event.user_id,
                                fallback_model,
                                bot_name,
                                Configurator.cm.get_cfg().others["openai_key"],
                                Configurator.cm.get_cfg().others.get("openai_base_url"),
                            )
                            ulist, result = search.Response()
                            user_lists = ulist

                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Reply(event.message_id), Segments.Text(result)
                        ),
                    )
                    publish_desktop_state(event.user_id, result)

                except UnboundLocalError:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Reply(event.message_id),
                            Segments.Text(f"请稍等，{bot_name}在思考 🤔"),
                        ),
                    )
                except TimeoutError:
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Reply(event.message_id),
                            Segments.Text(
                                f"哎呀，你问的问题太复杂了，{bot_name}想不出来了 ┭┮﹏┭┮"
                            ),
                        ),
                    )
                except Exception as e:
                    print(traceback.format_exc())
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(
                            Segments.Reply(event.message_id),
                            Segments.Text(
                                f"{type(e)}\n{url}\n{bot_name}发生错误，不能回复你的消息了，请稍候再试吧 ε(┬┬﹏┬┬)3"
                            ),
                        ),
                    )

    # 私聊消息处理
    if isinstance(event, Events.PrivateMessageEvent):
        user_message = str(event.message)
        order = ""

        event_user = (await actions.get_stranger_info(event.user_id)).data.raw
        event_user = event_user.get("nickname", "用户")
        print(f"[私聊] {event_user}: {user_message}")

        # 根据用户身份设置系统提示
        sys_prompt = select_persona_prompt(event.user_id, event_user)

        # ping 测试
        if "ping" == user_message:
            await actions.send(
                user_id=event.user_id,
                message=Manager.Message(Segments.Text("pong! 爆炸！v(◦'ωˉ◦)~♡ ")),
            )

        # 夸奖回复
        elif f"{bot_name}真棒" in user_message:
            i = random.randint(1, 3)
            match i:
                case 1:
                    m = "啊！老……老公，别怎么说啦，人……人家好害羞的啦，人家还会努力的(*ᴗ͈ˬᴗ͈)ꕤ*.ﾟ"
                case 2:
                    m = "啊~老公~你不要这么夸人家啦~〃∀〃"
                case 3:
                    m = "唔……谢……谢谢老公啦🥰~"
            await actions.send(
                user_id=event.user_id, message=Manager.Message(Segments.Text(m))
            )

        # 解析命令
        elif user_message.startswith(reminder):
            order_i = user_message.find(reminder)
            if order_i != -1:
                order = user_message[order_i + len(reminder) :].strip()
                print(f"[私聊] 收到命令: {order}")

        # 快捷命令：直接发送"生图"或"生图 xxx"也可以触发
        if not order and (user_message == "生图" or user_message.startswith("生图 ")):
            order = user_message
            print(f"[私聊] 收到快捷命令 {order}")

        # 帮助命令
        if "帮助" in order:
            p = " "
            match EnableNetwork:
                case "Pixmap":
                    p = "（当前）"

            content = f"""如何与{bot_name}私聊交流( •̀ ω •́ )✧
    注：对话前加上 {reminder} 或直接发送命令~
    1. {reminder}(任意问题，必填) —> {bot_name}回复
    2. {reminder}读图{p}—> {bot_name}可以查看您发送的图片
    3. {reminder}大头照 —> {bot_name}给你拍张大头照
    4. 生图 / 生图 白丝/猫娘/初音/雷姆/JK —> {bot_name}获取精美图片（支持标签搜索）
    5. {reminder}做我姐姐吧 / {reminder}当我女朋友（默认）/ {reminder}做我mm吧 —> {bot_name}切换不同的角色互动噢！~
快来聊天吧(*≧︶≦)"""
            await actions.send(
                user_id=event.user_id, message=Manager.Message(Segments.Text(content))
            )

        # 关于命令
        elif "关于" in order:
            about = f"""{bot_name} {bot_name_en} - 简单 可爱 个性 全知
————————————————————
Build Information
Version：{version_name}
Powered by NapCat.OneBot
Rebuilt from HypeR
————————————————————
Third-party API
1. Mirokoi API
2. Lolicon API
2. LoliAPI API
4. ChatGPT gpt-5.1
5. ChatGPT gpt-5.1
6. Google gemini-2.5-flash
————————————————————
Copyright
Made by SR Studio
2019~2025 All rights reserved"""
            await actions.send(
                user_id=event.user_id, message=Manager.Message(Segments.Text(about))
            )

        # 切换模式
        elif "读图" in order:
            EnableNetwork = "Pixmap"
            await actions.send(
                user_id=event.user_id,
                message=Manager.Message(
                    Segments.Text(f"{bot_name}打开了新视界！o(*≧▽≦)ツ")
                ),
            )

        # 角色切换 - 当我女朋友
        elif "当我女朋友" in order:
            try:
                if not Write_Roles("girlfriend", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(Segments.Text("老公~你回来啦~(*≧︶≦)")),
                )
            except Exception as e:
                print(traceback.format_exc())
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"可是{bot_name}还想继续做你的姐姐，这样我就可以保护你了！(๑•̀ㅂ•́)و✧"
                        )
                    ),
                )

        # 角色切换 - 做我姐姐吧
        elif "做我姐姐吧" in order:
            try:
                if not Write_Roles("sister", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(Segments.Text("你好呀！妹妹！~o(*≧▽≦)ツ")),
                )
            except Exception as e:
                print(traceback.format_exc())
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"呜呜呜……{bot_name}还想继续做你的女朋友，依赖你 (*/ω＼*)"
                        )
                    ),
                )

        # 角色切换 - 做我mm吧
        elif "做我mm吧" in order:
            try:
                if not Write_Roles("mother", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text("你好呀！血小板！~o(*≧▽≦)ツ")
                    ),
                )
            except Exception as e:
                print(traceback.format_exc())
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"呜呜呜……{bot_name}还想继续做你的女朋友，依赖你 (*/ω＼*)"
                        )
                    ),
                )

        # 角色切换 - 程序员
        elif "程序员" in order:
            try:
                if not Write_Roles("programmer", event.user_id):
                    raise RuntimeError("角色写入失败")
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(Segments.Text("已切换到高级程序员模式。")),
                )
            except Exception:
                print(traceback.format_exc())
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text("切换高级程序员模式失败，请稍后再试。")
                    ),
                )

        # 大头照
        elif "大头照" in order:
            uin = event.user_id
            await actions.send(
                user_id=event.user_id,
                message=Manager.Message(
                    Segments.Image(
                        f"http://q2.qlogo.cn/headimg_dl?dst_uin={uin}&spec=640"
                    )
                ),
            )

        # 生图功能（私聊版）- 使用鸭子API
        elif order == "生图" or "生图 " in order:
            if "生图 " in order:
                start_index = order.find("生图 ")
                result = order[start_index + len("生图 ") :].strip().lower()
            else:
                result = ""  # 没有参数时默认随机

            user_id = event.user_id
            current_time = time.time()

            if user_id in cooldowns and current_time - cooldowns[user_id] < 18:
                time_remaining = 18 - (current_time - cooldowns[user_id])
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"18秒个人cd，请等待 {time_remaining:.1f} 秒后重试"
                        )
                    ),
                )
            else:
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(f"{bot_name}正在生成图片 ヾ(≧▽≦*)o")
                    ),
                )

                # 根据标签选择 API 类型
                use_x_source = False
                use_tag_search = False
                search_tag = ""
                type_name = "Pixiv"
                post_data = {"num": 1}

                # 中文标签到英文标签的映射（与群聊共用）
                tag_mapping = {
                    "白丝": "white_stockings|白タイツ",
                    "黑丝": "black_stockings|黒タイツ",
                    "丝袜": "pantyhose|パンスト",
                    "猫娘": "cat_girl|猫耳|neko",
                    "猫耳": "cat_ears|猫耳",
                    "狐娘": "fox_girl|狐耳",
                    "兔女郎": "bunny_girl|バニーガール",
                    "初音": "hatsune_miku|初音ミク",
                    "初音未来": "hatsune_miku|初音ミク",
                    "甘雨": "ganyu|甘雨",
                    "刻晴": "keqing|刻晴",
                    "胡桃": "hu_tao|胡桃",
                    "雷电将军": "raiden_shogun|雷電将軍",
                    "雷姆": "rem|レム",
                    "拉姆": "ram|ラム",
                    "友利奈绪": "tomori_nao|友利奈緒",
                    "02": "zero_two|ゼロツー",
                    "时崎狂三": "tokisaki_kurumi|時崎狂三",
                    "jk": "school_uniform|JK",
                    "女仆": "maid|メイド",
                    "泳装": "swimsuit|水着",
                    "巨乳": "large_breasts|巨乳",
                    "白发": "white_hair|白髪",
                    "银发": "silver_hair|銀髪",
                }

                # 预设类型关键词
                preset_keywords = [
                    "x",
                    "推特",
                    "twitter",
                    "r18",
                    "涩图",
                    "色图",
                    "涩涩",
                    "ai",
                    "非ai",
                    "人工",
                    "横图",
                    "电脑",
                    "pc",
                    "竖图",
                    "手机",
                    "mobile",
                    "安全",
                    "sfw",
                    "全年龄",
                    "随机",
                ]

                is_preset = (
                    any(kw in result for kw in preset_keywords) if result else True
                )

                if "x" in result or "推特" in result or "twitter" in result:
                    use_x_source = True
                    type_name = "X(Twitter)"
                elif (
                    "r18" in result
                    or "涩图" in result
                    or "色图" in result
                    or "涩涩" in result
                ):
                    post_data["r18Type"] = 1
                    type_name = "R18"
                elif "ai" in result and "非" not in result and is_preset:
                    post_data["aiType"] = 2
                    type_name = "AI绘画"
                elif "非ai" in result or "人工" in result:
                    post_data["aiType"] = 1
                    type_name = "人工绘画"
                elif "横图" in result or "电脑" in result or "pc" in result:
                    post_data["imageSizeType"] = 1
                    type_name = "横向壁纸"
                elif "竖图" in result or "手机" in result or "mobile" in result:
                    post_data["imageSizeType"] = 2
                    type_name = "竖向壁纸"
                elif "安全" in result or "sfw" in result or "全年龄" in result:
                    post_data["r18Type"] = 0
                    type_name = "全年龄"
                elif result and not is_preset:
                    use_tag_search = True
                    # 检查是否有中文标签映射
                    search_tag = result
                    display_tag = result
                    for cn_tag, en_tag in tag_mapping.items():
                        if cn_tag in result.lower():
                            search_tag = en_tag
                            display_tag = cn_tag
                            break
                    type_name = f"标签:{display_tag}"
                else:
                    type_name = "Pixiv随机"

                # 标签搜索使用 Lolicon API
                if use_tag_search:
                    api_url = f"https://api.lolicon.app/setu/v2?tag={search_tag}&num=1"
                    try:
                        response = requests.get(api_url, timeout=15)
                        request = response.json()

                        if request.get("error") == "" and request.get("data"):
                            img_data = request["data"][0]
                            url = img_data.get("urls", {}).get("original", "")
                            title = img_data.get("title", "")
                            author = img_data.get("author", "")
                            pid = img_data.get("pid", "")
                            tags = img_data.get("tags", [])[:3]

                            info = f"{type_name}"
                            if title:
                                info += f"\n标题: {title}"
                            if author:
                                info += f" | 作者: {author}"
                            if tags:
                                info += f"\n标签: {', '.join(tags)}"

                            if url:
                                # 下载并压缩图片
                                compressed_base64 = await download_and_compress_image(
                                    url
                                )
                                if compressed_base64:
                                    await actions.send(
                                        user_id=event.user_id,
                                        message=Manager.Message(
                                            Segments.Image(
                                                f"base64://{compressed_base64}"
                                            ),
                                            Segments.Text(info),
                                        ),
                                    )
                                else:
                                    await actions.send(
                                        user_id=event.user_id,
                                        message=Manager.Message(
                                            Segments.Image(url), Segments.Text(info)
                                        ),
                                    )
                                cooldowns[user_id] = current_time
                            else:
                                await actions.send(
                                    user_id=event.user_id,
                                    message=Manager.Message(
                                        Segments.Text(f"{bot_name}生图失败了 ＞﹏＜")
                                    ),
                                )
                        else:
                            await actions.send(
                                user_id=event.user_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"{bot_name}没找到「{search_tag}」相关图片，试试英文标签如 cat_girl, miku"
                                    )
                                ),
                            )
                    except Exception as e:
                        await actions.send(
                            user_id=event.user_id,
                            message=Manager.Message(
                                Segments.Text(
                                    f"{bot_name}生图出错了: {type(e).__name__}"
                                )
                            ),
                        )
                else:
                    # 选择API端点
                    if use_x_source:
                        api_url = x_api_url
                    else:
                        api_url = pixiv_api_url

                    # 请求API
                    try:
                        response = requests.post(
                            api_url,
                            json=post_data,
                            headers={"Content-Type": "application/json"},
                            timeout=15,
                        )
                        request = response.json()

                        if request.get("success") and request.get("data"):
                            img_data = request["data"][0]

                            if use_x_source:
                                url = img_data.get("pictureUrl", "")
                                info = f"{type_name} | 来源: X"
                            else:
                                urls_list = img_data.get("urlsList", [])
                                url = urls_list[0].get("url", "") if urls_list else ""
                                width = img_data.get("width", "未知")
                                height = img_data.get("height", "未知")
                                title = img_data.get("title", "")
                                author = img_data.get("author", "")
                                info = f"{type_name} | {width}x{height}"
                                if title:
                                    info += f"\n标题: {title}"
                                if author:
                                    info += f" | 作者: {author}"

                            if url:
                                # 下载并压缩图片
                                compressed_base64 = await download_and_compress_image(
                                    url
                                )
                                if compressed_base64:
                                    await actions.send(
                                        user_id=event.user_id,
                                        message=Manager.Message(
                                            Segments.Image(
                                                f"base64://{compressed_base64}"
                                            ),
                                            Segments.Text(info),
                                        ),
                                    )
                                else:
                                    await actions.send(
                                        user_id=event.user_id,
                                        message=Manager.Message(
                                            Segments.Image(url), Segments.Text(info)
                                        ),
                                    )
                                cooldowns[user_id] = current_time
                            else:
                                await actions.send(
                                    user_id=event.user_id,
                                    message=Manager.Message(
                                        Segments.Text(
                                            f"{bot_name}生图失败了，再试一次吧 ＞﹏＜"
                                        )
                                    ),
                                )
                        else:
                            await actions.send(
                                user_id=event.user_id,
                                message=Manager.Message(
                                    Segments.Text(
                                        f"{bot_name}无法访问接口了，请稍后重试 ε(┬┬﹏┬┬)3"
                                    )
                                ),
                            )
                    except Exception as e:
                        print(f"[私聊生图] 错误: {e}")
                        await actions.send(
                            user_id=event.user_id,
                            message=Manager.Message(
                                Segments.Text(
                                    f"{bot_name}生图出错了: {type(e).__name__}"
                                )
                            ),
                        )

        # AI 对话（私聊版）
        elif len(order) >= 2:
            url = ""
            try:
                match EnableNetwork:
                    case "Pixmap":
                        model = genai.GenerativeModel(
                            model_name=default_model,
                            generation_config=generation_config,
                            system_instruction=sys_prompt or None,
                        )

                        new = []
                        for i in event.message:
                            if isinstance(i, Segments.Text):
                                new.append(Parts.Text(i.text.replace(reminder, "", 1)))
                            elif isinstance(i, Segments.Image):
                                if i.file.startswith("http"):
                                    url = i.file
                                else:
                                    url = i.url
                                try:
                                    new.append(Parts.File.upload_from_url(url))
                                    print("[私聊] 有图")
                                except Exception as img_err:
                                    print(f"[私聊] 图片下载失败: {img_err}")
                                    new.append(Parts.Text("[图片下载失败]"))
                            elif isinstance(i, Segments.MarketFace):
                                # 商城表情包
                                url = get_market_face_url(i.face_id)
                                try:
                                    new.append(Parts.File.upload_from_url(url))
                                    print("[私聊] 有表情包")
                                except Exception as img_err:
                                    print(f"[私聊] 表情包下载失败: {img_err}")
                                    new.append(Parts.Text("[表情包下载失败]"))

                        new = Roles.User(*new)
                        try:
                            result = (
                                cmc.get_context(event.user_id, 0)
                                .gen_content(new)
                                .rstrip("\n")
                            )
                        except Exception as primary_error:
                            print(
                                f"[私聊][主模型失败] {default_model}: {primary_error}"
                            )
                            print(f"[私聊][切换候补模型] {fallback_model}")
                            genai.configure(
                                api_key=fallback_key, base_url=gemini_base_url
                            )
                            model = genai.GenerativeModel(
                                model_name=fallback_model,
                                generation_config=generation_config,
                                system_instruction=sys_prompt or None,
                            )
                            cmc.groups.clear()
                            result = (
                                cmc.get_context(event.user_id, 0)
                                .gen_content(new)
                                .rstrip("\n")
                            )
                            genai.configure(api_key=key, base_url=gemini_base_url)

                    case "Normal" | "Net":
                        search = SearchOnline(
                            sys_prompt,
                            order,
                            user_lists,
                            event.user_id,
                            fallback_model,
                            bot_name,
                            Configurator.cm.get_cfg().others["openai_key"],
                            Configurator.cm.get_cfg().others.get("openai_base_url"),
                        )
                        ulist, result = search.Response()
                        user_lists = ulist

                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(Segments.Text(result)),
                )
                publish_desktop_state(event.user_id, result)

            except UnboundLocalError:
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(f"请稍等，{bot_name}在思考 🤔")
                    ),
                )
            except TimeoutError:
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"哎呀，你问的问题太复杂了，{bot_name}想不出来了 ┭┮﹏┭┮"
                        )
                    ),
                )
            except Exception as e:
                print(traceback.format_exc())
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(
                        Segments.Text(
                            f"{type(e)}\n{bot_name}发生错误，不能回复你的消息了，请稍候再试吧 ε(┬┬﹏┬┬)3"
                        )
                    ),
                )


def seconds_to_hms(total_seconds):
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{hours}h, {minutes}m, {seconds}s"


def verfiy_pixiv(file_path):
    try:
        img = Image.open(file_path)
        img.verify()  # 验证图像
        img.close()
        return True
    except (IOError, SyntaxError) as e:
        print(f"Error: {e}")
        return False


def get_system_info():
    # 系统
    version_info = platform.platform()
    architecture = platform.architecture()
    cpu_count = psutil.cpu_count(logical=True)
    cpu_usage = psutil.cpu_percent(interval=1)

    # 内存
    virtual_memory = psutil.virtual_memory()
    total_memory = virtual_memory.total
    used_memory = virtual_memory.used
    memory_usage_percentage = virtual_memory.percent

    # GPU信息（是否有）
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_count = len(gpus)
        gpu_usage = [gpu.load for gpu in gpus]
    else:
        gpu_count = 0
        gpu_usage = []

    return {
        "version_info": version_info,
        "architecture": architecture,
        "cpu_count": cpu_count,
        "cpu_usage": cpu_usage,
        "total_memory": total_memory,
        "used_memory": used_memory,
        "memory_usage_percentage": memory_usage_percentage,
        "gpu_count": gpu_count,
        "gpu_usage": gpu_usage,
    }


def deal_image(i, max_width=1920, max_height=1920, max_size_mb=5):
    """
    压缩图片：限制尺寸和文件大小

    Args:
        i: 图片二进制数据
        max_width: 最大宽度（默认1920）
        max_height: 最大高度（默认1920）
        max_size_mb: 最大文件大小MB（默认5MB）

    Returns:
        压缩后的图片二进制数据
    """
    img = Image.open(io.BytesIO(i))

    # 转换为RGB模式（处理PNG透明通道等）
    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # 限制尺寸
    width, height = img.size
    if width > max_width or height > max_height:
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"图片尺寸调整: {width}x{height} -> {new_width}x{new_height}")

    # 压缩文件大小
    buffer = io.BytesIO()
    max_size = max_size_mb * 1024 * 1024
    quality = 95

    while quality >= 10:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() < max_size:
            break
        quality -= 10

    print(f"图片压缩完成: {buffer.tell() / 1024:.1f}KB, quality={quality}")
    return buffer.getvalue()


async def download_and_compress_image(
    url, max_width=1920, max_height=1920, max_size_mb=5
):
    """
    下载并压缩图片

    Args:
        url: 图片URL
        max_width: 最大宽度
        max_height: 最大高度
        max_size_mb: 最大文件大小MB

    Returns:
        base64编码的图片数据，失败返回None
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    original_size = len(image_data) / 1024
                    print(f"下载图片成功: {original_size:.1f}KB")

                    # 压缩图片
                    compressed = deal_image(
                        image_data, max_width, max_height, max_size_mb
                    )
                    compressed_size = len(compressed) / 1024
                    print(
                        f"压缩后: {compressed_size:.1f}KB (节省 {(1 - compressed_size / original_size) * 100:.1f}%)"
                    )

                    # 返回base64编码
                    return base64.b64encode(compressed).decode("utf-8")
                else:
                    print(f"下载图片失败: HTTP {resp.status}")
                    return None
    except Exception as e:
        print(f"下载图片异常: {e}")
        return None


start_desktop_bridge()
Listener.run()

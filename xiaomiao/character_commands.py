"""QQ Bot 角色切换命令

在 QQ 消息中支持角色切换功能。

使用方式:
    /切换 小喵
    /切换 夏目
    /切换 亚托莉
    /角色列表
"""

from tool.xiaomiao.character_manager import CharacterManager


def handle_character_command(message: str) -> tuple[bool, str]:
    """
    处理角色相关命令

    Args:
        message: 用户消息

    Returns:
        (是否处理, 回复消息)
    """
    message = message.strip()

    # 角色列表
    if message in ["/角色列表", "/角色", "/characters", "/chars"]:
        chars = CharacterManager.list_characters()

        reply_lines = ["📋 可用角色列表：\n"]
        for char in chars:
            status = "✅ 当前" if char["is_current"] else "  "
            reply_lines.append(f"{status} {char['name']} ({char['id']})")
            reply_lines.append(f"     {char['description']}\n")

        reply_lines.append("\n💡 使用方式：")
        reply_lines.append("   /切换 夏目")
        reply_lines.append("   /切换 亚托莉")

        return True, "\n".join(reply_lines)

    # 角色切换
    if message.startswith("/切换 ") or message.startswith("/switch "):
        # 提取角色名
        char_name = message.split(maxsplit=1)[1].strip()

        # 映射中文名到 ID
        name_map = {
            "小喵": "xiaomiao",
            "夏目": "natsume",
            "四季夏目": "natsume",
            "亚托莉": "atri",
            "ATRI": "atri",
            "xiaomiao": "xiaomiao",
            "natsume": "natsume",
            "atri": "atri",
        }

        char_id = name_map.get(char_name)

        if not char_id:
            return True, f"❌ 未知角色：{char_name}\n\n请使用 /角色列表 查看可用角色"

        # 切换角色
        success = CharacterManager.switch_character(char_id)

        if success:
            char = CharacterManager.get_current()

            # 不同角色的切换回复
            if char_id == "xiaomiao":
                reply = f"✅ 已切换到 {char['name']}\n\n你好，我是小喵，很高兴为你服务。"
            elif char_id == "natsume":
                reply = f"✅ 已切换到 {char['name']}\n\n……嗯。我是夏目。"
            elif char_id == "atri":
                reply = f"✅ 已切换到 {char['name']}\n\nATRI 来啦！主人好~ ✨"
            else:
                reply = f"✅ 已切换到 {char['name']}"

            return True, reply
        else:
            return True, f"❌ 切换失败，请稍后重试"

    # 当前角色
    if message in ["/当前角色", "/current", "/whoami"]:
        char = CharacterManager.get_current()
        if char:
            reply = f"📌 当前角色：{char['name']} ({char['id']})\n\n{char['description']}"
            return True, reply
        else:
            return True, "❌ 获取当前角色失败"

    return False, ""


# 便捷函数
def is_character_command(message: str) -> bool:
    """检查是否是角色命令"""
    message = message.strip()
    return (
        message.startswith("/切换 ") or
        message.startswith("/switch ") or
        message in ["/角色列表", "/角色", "/characters", "/chars", "/当前角色", "/current", "/whoami"]
    )


__all__ = ["handle_character_command", "is_character_command"]

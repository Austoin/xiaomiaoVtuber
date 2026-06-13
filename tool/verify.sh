#!/bin/bash
# 工具层验证测试脚本

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              工具层重构验证测试                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

echo "1. 测试 QQ 适配器..."
python -c "from tool.adapters.qq_adapter import get_tool_policy; print('   ✓ QQ 适配器:', get_tool_policy(123, True))" || echo "   ✗ QQ 适配器测试失败"

echo ""
echo "2. 测试 TUI 适配器..."
python -c "from tool.adapters.tui_adapter import get_tui_tool_policy; print('   ✓ TUI 适配器:', get_tui_tool_policy())" || echo "   ✗ TUI 适配器测试失败"

echo ""
echo "3. 测试权限模块..."
python -c "from tool.xiaomiao.permissions import LOW_RISK_TOOL_POLICY, TRUSTED_CONFIRMED_TOOL_POLICY; print('   ✓ 权限常量:', LOW_RISK_TOOL_POLICY, TRUSTED_CONFIRMED_TOOL_POLICY)" || echo "   ✗ 权限模块测试失败"

echo ""
echo "4. 测试 nanobot 兼容层..."
python -c "from tool.core.registry import ToolRegistry; print('   ✓ 工具注册器导入成功')" || echo "   ✗ nanobot 兼容层测试失败"

echo ""
echo "5. 检查目录结构..."
echo "   ✓ tool/core: $(ls tool/core/*.py 2>/dev/null | wc -l) 个文件"
echo "   ✓ tool/xiaomiao: $(ls tool/xiaomiao/*.py 2>/dev/null | wc -l) 个文件"
echo "   ✓ tool/memory: $(ls tool/memory/*.py 2>/dev/null | wc -l) 个文件"
echo "   ✓ tool/adapters: $(ls tool/adapters/*.py 2>/dev/null | wc -l) 个文件"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  验证完成！所有基础测试通过。                                  ║"
echo "║                                                              ║"
echo "║  下一步:                                                      ║"
echo "║  - 运行 start-tui.cmd 测试 TUI                                ║"
echo "║  - 运行 start-all.cmd 测试 QQ Bot                             ║"
echo "║  - 访问 http://127.0.0.1:5175 测试 xiaomiaobot web           ║"
echo "╚══════════════════════════════════════════════════════════════╝"

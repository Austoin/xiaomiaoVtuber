import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from prerequisites import plain_text_reply, prerequisite, select_role, update_role_lists


class PersonaTests(unittest.TestCase):
    def test_senior_programmer_persona_uses_config_template(self):
        personas = {"senior_programmer": "你叫{bot_name}，是{event_user}的高级程序员。"}

        prompt = prerequisite("小喵", "用户", personas).senior_programmer()

        self.assertEqual(prompt, "你叫小喵，是用户的高级程序员。")

    def test_senior_programmer_default_persona_is_engineering_focused(self):
        prompt = prerequisite("小喵", "用户").senior_programmer()

        self.assertIn("高级程序员", prompt)
        self.assertIn("根因", prompt)
        self.assertIn("代码", prompt)

    def test_programmer_role_removes_other_roles(self):
        sisters, jhq, programmers = update_role_lists(
            "10001",
            "programmer",
            sisters=["10001", "20002"],
            jhq=["10001"],
            programmers=[],
        )

        self.assertEqual(sisters, ["20002"])
        self.assertEqual(jhq, [])
        self.assertEqual(programmers, ["10001"])

    def test_girlfriend_role_removes_all_role_lists(self):
        sisters, jhq, programmers = update_role_lists(
            "10001",
            "girlfriend",
            sisters=["10001"],
            jhq=["10001"],
            programmers=["10001"],
        )

        self.assertEqual(sisters, [])
        self.assertEqual(jhq, [])
        self.assertEqual(programmers, [])

    def test_unknown_user_defaults_to_programmer_role(self):
        role = select_role(
            "10001",
            sisters=[],
            jhq=[],
            programmers=[],
        )

        self.assertEqual(role, "programmer")

    def test_plain_text_reply_removes_markdown_syntax(self):
        markdown = """## 结论
- 第一条
```python
print("hi")
```
**重点** 和 `inline_code`"""

        text = plain_text_reply(markdown)

        self.assertNotIn("##", text)
        self.assertNotIn("```", text)
        self.assertNotIn("**", text)
        self.assertNotIn("`", text)
        self.assertIn("结论", text)
        self.assertIn("第一条", text)
        self.assertIn('print("hi")', text)
        self.assertIn("重点", text)
        self.assertIn("inline_code", text)


if __name__ == "__main__":
    unittest.main()

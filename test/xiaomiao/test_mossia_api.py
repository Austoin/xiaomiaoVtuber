#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试鸭子API (mossia.top) 接口
"""

import requests
import json


def test_pixiv_get():
    """测试Pixiv图源 GET请求"""
    print("=" * 50)
    print("测试 Pixiv 图源 GET 请求")
    print("=" * 50)

    url = "https://api.mossia.top/duckMo"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()

        print(f"状态码: {data.get('errCode')}")
        print(f"成功: {data.get('success')}")
        print(f"消息: {data.get('message')}")

        if data.get("success") and data.get("data"):
            img = data["data"][0]
            print(f"\n图片信息:")
            print(f"  PID: {img.get('pid')}")
            print(f"  标题: {img.get('title')}")
            print(f"  作者: {img.get('author')}")
            print(f"  尺寸: {img.get('width')}x{img.get('height')}")
            print(f"  AI类型: {img.get('aiType')} (0=未知, 1=非AI, 2=AI)")

            urls_list = img.get("urlsList", [])
            if urls_list:
                print(f"  图片URL: {urls_list[0].get('url')}")

            tags = img.get("tagsList", [])
            if tags:
                tag_names = [t.get("tagName") for t in tags[:5]]
                print(f"  标签: {', '.join(tag_names)}")

        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def test_pixiv_post():
    """测试Pixiv图源 POST请求"""
    print("\n" + "=" * 50)
    print("测试 Pixiv 图源 POST 请求 (AI作品)")
    print("=" * 50)

    url = "https://api.mossia.top/duckMo"
    payload = {
        "num": 1,
        "aiType": 2,  # AI作品
    }

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=15
        )
        data = response.json()

        print(f"状态码: {data.get('errCode')}")
        print(f"成功: {data.get('success')}")

        if data.get("success") and data.get("data"):
            img = data["data"][0]
            print(f"\nAI图片信息:")
            print(f"  PID: {img.get('pid')}")
            print(f"  标题: {img.get('title')}")
            print(f"  AI类型: {img.get('aiType')}")

            urls_list = img.get("urlsList", [])
            if urls_list:
                print(f"  图片URL: {urls_list[0].get('url')}")

        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def test_x_source():
    """测试X图源"""
    print("\n" + "=" * 50)
    print("测试 X(Twitter) 图源")
    print("=" * 50)

    url = "https://api.mossia.top/duckMo/x"

    try:
        response = requests.get(url, timeout=15)
        data = response.json()

        print(f"状态码: {data.get('errCode')}")
        print(f"成功: {data.get('success')}")

        if data.get("success") and data.get("data"):
            img = data["data"][0]
            print(f"\nX图片信息:")
            print(f"  帖子URL: {img.get('url')}")
            print(f"  图片URL: {img.get('pictureUrl')}")

        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def test_image_size_type():
    """测试图片尺寸筛选"""
    print("\n" + "=" * 50)
    print("测试 横图筛选 (imageSizeType=1)")
    print("=" * 50)

    url = "https://api.mossia.top/duckMo"
    payload = {
        "num": 1,
        "imageSizeType": 1,  # 横图
    }

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=15
        )
        data = response.json()

        print(f"状态码: {data.get('errCode')}")
        print(f"成功: {data.get('success')}")

        if data.get("success") and data.get("data"):
            img = data["data"][0]
            width = img.get("width", 0)
            height = img.get("height", 0)
            print(f"\n横图信息:")
            print(f"  尺寸: {width}x{height}")
            print(f"  是否横图: {'是' if width > height else '否'}")

            urls_list = img.get("urlsList", [])
            if urls_list:
                print(f"  图片URL: {urls_list[0].get('url')}")

        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    print("鸭子API (mossia.top) 接口测试")
    print("文档: https://docs.mossia.top\n")

    results = []

    results.append(("Pixiv GET", test_pixiv_get()))
    results.append(("Pixiv POST (AI)", test_pixiv_post()))
    results.append(("X图源", test_x_source()))
    results.append(("横图筛选", test_image_size_type()))

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + ("全部测试通过!" if all_passed else "部分测试失败!"))

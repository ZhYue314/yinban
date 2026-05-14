#!/usr/bin/env python3
import subprocess
import sys
import os

# don't force encoding - let the terminal handle it
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding=sys.stdout.encoding or "utf-8")
    except Exception:
        pass
if hasattr(sys.stdin, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding=sys.stdin.encoding or "utf-8")
    except Exception:
        pass


def run(cmd):
    os.system(f'python main.py {cmd}')
    input("\n按 Enter 继续...")


MENU = """
  ===============================
      音 伴 一 键 启 动
  ===============================

  1. 和 AI 聊天
  2. 每日推荐
  3. 按心情推荐
  4. 按场景推荐
  5. 发现新歌手
  6. 语音播客
  7. 听歌报告
  8. 查看配置
  9. 初始化
  0. 退出
"""


def main():
    while True:
        print(MENU)
        try:
            choice = input("请选择 (0-9): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "1":
            os.system("python main.py chat")
            input("\n按 Enter 继续...")
        elif choice == "2":
            run("daily")
        elif choice == "3":
            mood = input("输入心情 (开心/平静/伤感/烦躁/慵懒/热情): ").strip()
            run(f'recommend --mood "{mood}"')
        elif choice == "4":
            scene = input("输入场景 (深夜/学习/跑步/通勤/工作): ").strip()
            run(f'recommend --scene "{scene}"')
        elif choice == "5":
            run("discover")
        elif choice == "6":
            run("podcast --no-tts")
        elif choice == "7":
            run("report")
        elif choice == "8":
            run("config list")
        elif choice == "9":
            run("init")
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效输入，请重新选择")

    input("\n按 Enter 退出...")


if __name__ == "__main__":
    main()

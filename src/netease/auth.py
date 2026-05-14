import asyncio
import io
from pathlib import Path

import qrcode

from .client import NeteaseClient


class NeteaseAuth:
    def __init__(self, client: NeteaseClient):
        self.client = client

    async def login_by_qrcode(self) -> dict | None:
        key_resp = await self.client.login_qrcode_key()
        if key_resp.get("code") != 200:
            print("获取二维码失败")
            return None

        key = key_resp["data"]["unikey"]
        qr_resp = await self.client.login_qrcode_create(key)
        if qr_resp.get("code") != 200:
            print("生成二维码失败")
            return None

        qrimg_base64 = qr_resp["data"]["qrimg"]
        qr_data = qr_resp["data"]["qrurl"]

        img_data = qrimg_base64.split(",")[1] if "," in qrimg_base64 else qrimg_base64
        import base64
        img_bytes = base64.b64decode(img_data)
        image = qrcode.make(qr_data)
        image.show()

        print("请使用网易云音乐扫码登录...")
        print(f"或手动打开: {qr_data}")

        for _ in range(60):
            await asyncio.sleep(2)
            check = await self.client.login_qrcode_check(key)
            code = check.get("code")
            if code == 800:
                print("二维码已过期，请重新运行")
                return None
            elif code == 803:
                print("登录成功!")
                return check
            elif code == 802:
                print("等待确认...")

        print("登录超时")
        return None

    async def login_by_phone(self, phone: str, captcha: str) -> dict | None:
        return await self.client.login_cellphone(phone, captcha)

import json
import sys
import time
from typing import Any, Dict, Optional

import requests


BASE = "https://popgraph.netlify.app/api"
TIMEOUT = 30


def pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def post_json(path: str, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    if not r.ok:
        raise RuntimeError(f"POST {url} -> {r.status_code}\n{pretty(data)}")

    return data


def get_json(path: str, token: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(url, headers=headers, timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    if not r.ok:
        raise RuntimeError(f"GET {url} -> {r.status_code}\n{pretty(data)}")

    return data


def main():
    # 1) 邮箱注册（如果提示 EMAIL_EXISTS，换一个邮箱重试即可）
    email = f"test_{int(time.time())}@orbit-3.cloud"
    password = "Passw0rd!Passw0rd!"

    print("== Register (email) ==")
    reg = post_json(
        "/auth/register/email",
        {"email": email, "password": password},
    )
    print(pretty(reg))

    # 兼容不同返回结构：优先从 reg.tokens.access_token 取
    access_token = None
    if isinstance(reg, dict):
        tokens = reg.get("tokens") or {}
        access_token = tokens.get("access_token") or reg.get("access_token")

    if not access_token:
        print("注册返回里没拿到 access_token，请把完整返回贴我。")
        sys.exit(1)

    # 2) 邮箱登录
    print("\n== Login (email) ==")
    login = post_json(
        "/auth/login/email",
        {"email": email, "password": password},
    )
    print(pretty(login))

    login_access_token = None
    if isinstance(login, dict):
        tokens = login.get("tokens") or {}
        login_access_token = tokens.get("access_token") or login.get("access_token")

    token_to_use = login_access_token or access_token

    # 3) 获取当前用户信息 /me
    print("\n== Me ==")
    me = get_json("/auth/me", token=token_to_use)
    print(pretty(me))

    print("\nOK: 注册/登录/鉴权链路已跑通。")


if __name__ == "__main__":
    main()
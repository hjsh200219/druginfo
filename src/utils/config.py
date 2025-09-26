"""
설정 관리 모듈
"""

import os
from typing import Optional
from urllib.parse import urlparse


class Config:
    """환경 설정 관리 클래스"""

    def __init__(self):
        # 기본 URL 설정
        self.base_url = os.getenv(
            "EDB_BASE_URL", "https://dev-adminapi.edbintra.co.kr"
        )
        self.login_url = os.getenv(
            "EDB_LOGIN_URL", f"{self.base_url}/v1/auth/login"
        )

        # 인증 정보
        self.user_id = os.getenv("EDB_USER_ID")
        self.password = os.getenv("EDB_PASSWORD")

        # 옵션
        self.timeout = int(os.getenv("EDB_TIMEOUT", "15"))
        self.force_login = os.getenv("EDB_FORCE_LOGIN", "false").lower() == "true"

        # 자동 로그인 활성화 여부
        self.auto_login_enabled = bool(self.user_id and self.password)

    def get_api_url(self, path: str) -> str:
        """API 전체 URL 생성"""
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def __str__(self) -> str:
        """설정 정보 문자열 표현"""
        return (
            f"Config(\n"
            f"  base_url={self.base_url}\n"
            f"  login_url={self.login_url}\n"
            f"  user_id={'설정됨' if self.user_id else '미설정'}\n"
            f"  password={'설정됨' if self.password else '미설정'}\n"
            f"  timeout={self.timeout}초\n"
            f"  force_login={self.force_login}\n"
            f"  auto_login={'활성화' if self.auto_login_enabled else '비활성화'}\n"
            f")"
        )
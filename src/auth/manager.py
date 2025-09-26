"""
인증 관리자 - JWT 토큰 관리 및 자동 로그인 처리
"""

import os
import logging
from typing import Optional
from datetime import datetime, timedelta

from src.auth import login_and_get_token

logger = logging.getLogger(__name__)


class AuthManager:
    """인증 토큰 관리 클래스"""

    def __init__(self, config):
        self.config = config
        self.token: Optional[str] = None
        self.token_expires: Optional[datetime] = None

    async def login(self, user_id: Optional[str] = None, password: Optional[str] = None, force: bool = False) -> str:
        """로그인하여 토큰 획득"""
        uid = user_id or self.config.user_id
        pwd = password or self.config.password
        login_url = self.config.login_url

        if not uid or not pwd:
            raise ValueError("사용자 ID와 비밀번호가 필요합니다")

        if not login_url:
            raise ValueError("로그인 URL이 설정되지 않았습니다")

        try:
            logger.info(f"로그인 시도: {uid}")
            token = login_and_get_token(login_url, uid, pwd, force, self.config.timeout)

            # 토큰 저장
            self.token = token
            self.token_expires = datetime.now() + timedelta(hours=1)  # 보통 1시간 유효
            os.environ["EDB_TOKEN"] = token

            logger.info(f"로그인 성공: {uid}")
            return token

        except Exception as e:
            logger.error(f"로그인 실패: {e}")
            raise

    async def auto_login(self) -> Optional[str]:
        """자동 로그인 시도"""
        if not self.config.auto_login_enabled:
            logger.debug("자동 로그인 비활성화됨")
            return None

        # 기존 토큰이 유효한지 확인
        if self.token and self.token_expires:
            if datetime.now() < self.token_expires:
                logger.debug("기존 토큰 유효")
                return self.token

        # 환경 변수에서 토큰 확인
        env_token = os.getenv("EDB_TOKEN")
        if env_token:
            self.token = env_token
            self.token_expires = datetime.now() + timedelta(hours=1)
            logger.debug("환경 변수에서 토큰 로드")
            return env_token

        # 새로 로그인
        try:
            return await self.login()
        except Exception as e:
            logger.warning(f"자동 로그인 실패: {e}")
            return None

    def get_token(self) -> Optional[str]:
        """현재 토큰 반환"""
        return self.token or os.getenv("EDB_TOKEN")

    def clear_token(self):
        """토큰 초기화"""
        self.token = None
        self.token_expires = None
        if "EDB_TOKEN" in os.environ:
            del os.environ["EDB_TOKEN"]
        logger.debug("토큰 초기화됨")
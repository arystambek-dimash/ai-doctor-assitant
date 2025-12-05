from typing import Any, Dict, List

import jwt


class JWTService:
    def __init__(
            self,
            jwt_access_secret_key: str,
            jwt_refresh_secret_key: str,
    ):
        self._jwt_access_secret_key = jwt_access_secret_key
        self._jwt_refresh_secret_key = jwt_refresh_secret_key

    def _decode_jwt(
            self,
            token: str,
            *,
            key: Any,
            algorithms: List[str],
            **kwargs: Any,
    ) -> Dict[str, Any]:
        return jwt.decode(token, key=key, algorithms=algorithms, **kwargs)

    def encode_access_token(self, payload: dict) -> str:
        return jwt.encode(payload, key=self._jwt_access_secret_key, algorithm="HS256")

    def encode_refresh_token(self, payload: dict) -> str:
        return jwt.encode(payload, key=self._jwt_refresh_secret_key, algorithm="HS256")

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        return self._decode_jwt(
            token,
            key=self._jwt_access_secret_key,
            algorithms=["HS256"],
        )

    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        return self._decode_jwt(
            token,
            key=self._jwt_refresh_secret_key,
            algorithms=["HS256"],
        )

    def decode(
            self,
            token: str,
            *,
            key: Any,
            algorithms: List[str],
            **kwargs: Any,
    ) -> Dict[str, Any]:
        return self._decode_jwt(token, key=key, algorithms=algorithms, **kwargs)

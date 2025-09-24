from typing import Any, Dict, Optional
import os

import requests


class DrugInfoError(RuntimeError):
    pass


class UnauthorizedError(DrugInfoError):
    pass


def _base_url() -> str:
    base = (os.getenv("EDB_BASE_URL") or "").rstrip("/")
    if not base:
        login_url = os.getenv("EDB_LOGIN_URL") or ""
        if not login_url:
            raise DrugInfoError("EDB_BASE_URL 또는 EDB_LOGIN_URL 환경변수가 필요합니다")
        if "://" in login_url:
            scheme, rest = login_url.split("://", 1)
            host = rest.split("/", 1)[0]
            base = f"{scheme}://{host}"
    return base


def _headers() -> Dict[str, str]:
    headers: Dict[str, str] = {"accept": "application/json"}
    tok = os.getenv("EDB_TOKEN")
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    return headers


def _handle_response(resp: requests.Response) -> Dict[str, Any]:
    if resp.status_code == 401:
        raise UnauthorizedError("인증 실패(401)")
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        try:
            data = resp.json()
        except Exception:
            data = {"text": resp.text}
        raise DrugInfoError(f"요청 실패: {resp.status_code} {data}") from e
    try:
        data = resp.json()
    except Exception:
        return {"text": resp.text}
    if isinstance(data, dict):
        return data
    return {"data": data}


def list_main_ingredient(
    a4: Optional[bool] = None,
    a4Off: Optional[bool] = None,
    a5: Optional[bool] = None,
    a5Off: Optional[bool] = None,
    drugkind: Optional[bool] = None,
    drugkindOff: Optional[bool] = None,
    effect: Optional[bool] = None,
    effectOff: Optional[bool] = None,
    showMapped: Optional[bool] = None,
    IngredientCode: Optional[str] = None,
    ingredientNameKor: Optional[str] = None,
    drugKind: Optional[str] = None,
    PageSize: Optional[int] = None,
    Page: Optional[int] = None,
    SortBy: Optional[str] = None,
    # legacy aliases
    q: Optional[str] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient"
    params: Dict[str, Any] = {}
    def _set(name: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, bool):
            params[name] = "true" if value else "false"
        else:
            params[name] = value
    for k, v in (
        ("a4", a4), ("a4Off", a4Off), ("a5", a5), ("a5Off", a5Off),
        ("drugkind", drugkind), ("drugkindOff", drugkindOff), ("effect", effect), ("effectOff", effectOff),
        ("showMapped", showMapped), ("IngredientCode", IngredientCode), ("ingredientNameKor", ingredientNameKor),
        ("drugKind", drugKind), ("PageSize", PageSize), ("Page", Page), ("SortBy", SortBy),
    ):
        _set(k, v)
    if q is not None and "ingredientNameKor" not in params:
        params["ingredientNameKor"] = q
    if page is not None and "Page" not in params:
        params["Page"] = int(page)
    if size is not None and "PageSize" not in params:
        params["PageSize"] = int(size)
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def get_main_ingredient_by_code(code: str, timeout: int = 15) -> Dict[str, Any]:
    if not code:
        raise DrugInfoError("code 가 필요합니다")
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/{code}"
    resp = requests.get(url, headers=_headers(), timeout=timeout)
    return _handle_response(resp)


def list_product(
    crop: Optional[bool] = None,
    cropOff: Optional[bool] = None,
    base64: Optional[bool] = None,
    base64Off: Optional[bool] = None,
    watermark: Optional[bool] = None,
    watermarkOff: Optional[bool] = None,
    confirm: Optional[bool] = None,
    confirmOff: Optional[bool] = None,
    teoulLengthShort: Optional[bool] = None,
    teoulLengthShortOff: Optional[bool] = None,
    teoulLengthLong: Optional[bool] = None,
    teoulLengthLongOff: Optional[bool] = None,
    minCount: Optional[int] = None,
    ProductCode: Optional[str] = None,
    pillName: Optional[str] = None,
    vendor: Optional[str] = None,
    PageSize: Optional[int] = None,
    Page: Optional[int] = None,
    SortBy: Optional[str] = None,
    # legacy aliases
    q: Optional[str] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/product"
    params: Dict[str, Any] = {}
    def _set(name: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, bool):
            params[name] = "true" if value else "false"
        else:
            params[name] = value
    for k, v in (
        ("crop", crop), ("cropOff", cropOff), ("base64", base64), ("base64Off", base64Off),
        ("watermark", watermark), ("watermarkOff", watermarkOff), ("confirm", confirm), ("confirmOff", confirmOff),
        ("teoulLengthShort", teoulLengthShort), ("teoulLengthShortOff", teoulLengthShortOff), ("teoulLengthLong", teoulLengthLong), ("teoulLengthLongOff", teoulLengthLongOff),
        ("minCount", minCount), ("ProductCode", ProductCode), ("pillName", pillName), ("vendor", vendor),
        ("PageSize", PageSize), ("Page", Page), ("SortBy", SortBy),
    ):
        _set(k, v)
    if q is not None and "pillName" not in params:
        params["pillName"] = q
    if page is not None and "Page" not in params:
        params["Page"] = int(page)
    if size is not None and "PageSize" not in params:
        params["PageSize"] = int(size)
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def get_product_by_code(code: str, timeout: int = 15) -> Dict[str, Any]:
    """
    제품 코드로 제품 상세 정보를 조회합니다.

    참고: 응답의 data.korange 필드는 생물학적 동등성(생동) 관련 정보입니다.
    """
    if not code:
        raise DrugInfoError("code 가 필요합니다")
    base = _base_url()
    url = f"{base}/v1/druginfo/product/{code}"
    resp = requests.get(url, headers=_headers(), timeout=timeout)
    return _handle_response(resp)


# --- Additional endpoints ---

def list_main_ingredient_drug_effect(
    edit: Optional[str] = None,
    pageSize: Optional[int] = None,
    page: Optional[int] = None,
    sortBy: Optional[str] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/drug-effect"
    params: Dict[str, Any] = {}
    if edit is not None:
        params["edit"] = edit
    if pageSize is not None:
        params["PageSize"] = int(pageSize)
    if page is not None:
        params["Page"] = int(page)
    if sortBy is not None:
        params["SortBy"] = sortBy
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def list_main_ingredient_drug_kind(edit: Optional[str] = None, pageSize: Optional[int] = None, page: Optional[int] = None, sortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/drug-kind"
    params: Dict[str, Any] = {}
    if edit is not None:
        params["edit"] = edit
    if pageSize is not None:
        params["PageSize"] = int(pageSize)
    if page is not None:
        params["Page"] = int(page)
    if sortBy is not None:
        params["SortBy"] = sortBy
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def list_main_ingredient_guide_a4(edit: Optional[str] = None, pageSize: Optional[int] = None, page: Optional[int] = None, sortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/guide-a4"
    params: Dict[str, Any] = {}
    if edit is not None:
        params["edit"] = edit
    if pageSize is not None:
        params["PageSize"] = int(pageSize)
    if page is not None:
        params["Page"] = int(page)
    if sortBy is not None:
        params["SortBy"] = sortBy
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def list_main_ingredient_guide_a5(edit: Optional[str] = None, pageSize: Optional[int] = None, page: Optional[int] = None, sortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/guide-A5"
    params: Dict[str, Any] = {}
    if edit is not None:
        params["edit"] = edit
    if pageSize is not None:
        params["PageSize"] = int(pageSize)
    if page is not None:
        params["Page"] = int(page)
    if sortBy is not None:
        params["SortBy"] = sortBy
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def list_main_ingredient_picto(IsDeleted: Optional[str] = None, Title: Optional[str] = None, PageSize: Optional[int] = None, Page: Optional[int] = None, SortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/picto"
    params: Dict[str, Any] = {}
    if IsDeleted is not None:
        params["IsDeleted"] = IsDeleted
    if Title is not None:
        params["Title"] = Title
    if PageSize is not None:
        params["PageSize"] = int(PageSize)
    if Page is not None:
        params["Page"] = int(Page)
    if SortBy is not None:
        params["SortBy"] = SortBy
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def get_main_ingredient_picto_by_code(code: str, timeout: int = 15) -> Dict[str, Any]:
    if not code:
        raise DrugInfoError("code 가 필요합니다")
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/picto/{code}"
    resp = requests.get(url, headers=_headers(), timeout=timeout)
    return _handle_response(resp)


def get_main_ingredient_drug_effect_by_id(effect_id: int, timeout: int = 15) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/main-ingredient/drug-effect/{int(effect_id)}"
    resp = requests.get(url, headers=_headers(), timeout=timeout)
    return _handle_response(resp)


def list_product_edicode(ProductCode: Optional[str] = None, EdiCode: Optional[str] = None, PageSize: Optional[int] = None, Page: Optional[int] = None, SortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
    base = _base_url()
    url = f"{base}/v1/druginfo/product/edicode"
    params: Dict[str, Any] = {}
    if ProductCode is not None:
        params["ProductCode"] = ProductCode
    if EdiCode is not None:
        params["EdiCode"] = EdiCode
    if PageSize is not None:
        params["PageSize"] = int(PageSize)
    if Page is not None:
        params["Page"] = int(Page)
    if SortBy is not None:
        params["SortBy"] = SortBy
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


def list_product_edicode_same_ingredient(
    ProductCode: Optional[str] = None,
    EdiCode: Optional[str] = None,
    MasterIngredientCode: Optional[str] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    동일 주성분 제품(EDI 코드 기준) 목록을 조회합니다.

    Query parameters (Swagger): ediCode, productCode, masterIngredientCode
    이 함수는 인자명은 PascalCase를 받되, 실제 쿼리는 lowerCamelCase로 전송합니다.
    """
    base = _base_url()
    url = f"{base}/v1/druginfo/product/edicode/same-ingredient"
    params: Dict[str, Any] = {}
    if EdiCode is not None:
        params["ediCode"] = EdiCode
    if ProductCode is not None:
        params["productCode"] = ProductCode
    if MasterIngredientCode is not None:
        params["masterIngredientCode"] = MasterIngredientCode
    resp = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    return _handle_response(resp)


# --- (removed) Helpers for non-GET requests ---


# --- (removed) Non-GET endpoints (Swagger) ---



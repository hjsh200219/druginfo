from __future__ import annotations

"""DrugInfo API 응답을 토큰 친화적으로 요약하는 유틸리티."""

from typing import Any, Dict, List, Optional


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _primary_section(result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(result, dict):
        return {}
    data = result.get("data")
    if isinstance(data, dict):
        return data
    return result


def _extract_items(section: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(section, list):
        return [item for item in section if isinstance(item, dict)]
    if not isinstance(section, dict):
        return []
    for key in ("items", "list", "results", "rows", "data"):
        value = section.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _pick(item: Dict[str, Any], *candidates: str) -> Optional[Any]:
    for key in candidates:
        if key in item and item[key] not in (None, "", []):
            return item[key]
    return None


def _compact_korange(payload: Any) -> Optional[Dict[str, Any]]:
    data = _as_dict(payload)
    if not data:
        return None
    keep: Dict[str, Any] = {}
    for key in ("생동PK", "제네릭", "공공대조약", "특허", "함량", "취하일"):
        value = data.get(key)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in ("", "false", "0"):
                continue
        if value in (None, False, 0, "", "False", "0"):
            continue
        keep[key] = value
    return keep or None


def _meta(section: Dict[str, Any], items: List[Any]) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    if isinstance(section, dict):
        for key in ("totalCount", "TotalCount", "count", "total"):
            value = section.get(key)
            if isinstance(value, (int, float)):
                meta["total"] = int(value)
                break
        page = section.get("page") or section.get("Page")
        page_size = section.get("pageSize") or section.get("PageSize")
        if isinstance(page, (int, float)):
            meta["page"] = int(page)
        if isinstance(page_size, (int, float)):
            meta["pageSize"] = int(page_size)
        if "total" in meta and "page" in meta and "pageSize" in meta:
            remaining = meta["total"] - meta["page"] * meta["pageSize"]
            meta["hasMore"] = remaining > 0
    if "total" not in meta:
        meta["total"] = len(items)
    return meta


def _wrap_list(section: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"items": items}
    meta = _meta(section, items)
    if meta.get("total") is not None:
        payload["total"] = meta["total"]
    if meta.get("page") is not None and meta.get("pageSize") is not None:
        payload["page"] = meta["page"]
        payload["pageSize"] = meta["pageSize"]
        payload["hasMore"] = meta.get("hasMore", False)
    return payload


def _strip_empty_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v not in (None, "", [], {})}


def compact_main_ingredient_list(result: Dict[str, Any]) -> Dict[str, Any]:
    section = _primary_section(result)
    items: List[Dict[str, Any]] = []
    for item in _extract_items(section):
        slim = _strip_empty_fields(
            {
                "name": _pick(item, "ingredientNameKor", "ingredientName"),
                "code": _pick(item, "IngredientCode", "ingredientCode"),
                "masterCode": _pick(item, "MasterIngredientCode", "masterIngredientCode"),
                "atcCode": _pick(item, "ATCCode", "atcCode"),
                "dosageRoute": _pick(item, "DosageRoute", "dosageRoute"),
                "dosageForm": _pick(item, "DosageForm", "dosageForm"),
            }
        )
        if slim:
            items.append(slim)
    return _wrap_list(section, items)


def compact_main_ingredient_detail(result: Dict[str, Any]) -> Dict[str, Any]:
    section = _primary_section(result)
    slim = _strip_empty_fields(
        {
            "name": _pick(section, "ingredientNameKor", "ingredientName"),
            "code": _pick(section, "IngredientCode", "ingredientCode"),
            "masterCode": _pick(section, "MasterIngredientCode", "masterIngredientCode"),
            "atcCode": _pick(section, "ATCCode", "atcCode"),
            "dosageRoute": _pick(section, "DosageRoute", "dosageRoute"),
            "dosageForm": _pick(section, "DosageForm", "dosageForm"),
            "description": _pick(section, "description", "Description"),
        }
    )
    return slim


def _product_core_fields(item: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "name": _pick(item, "productName", "productNameKor", "pillName", "itemName"),
        "code": _pick(item, "productCode", "ProductCode"),
        "ediCode": _pick(item, "ediCode", "EdiCode"),
        "vendor": _pick(item, "vendor", "Vendor", "companyName", "makerName"),
        "masterCode": _pick(item, "masterIngredientCode", "MasterIngredientCode"),
        "dosageForm": _pick(item, "DosageForm", "dosageForm"),
        "strength": _pick(item, "strength", "Strength", "dose", "Dose"),
    }
    korange = _compact_korange(item.get("korange"))
    if korange:
        payload["korange"] = korange
    return _strip_empty_fields(payload)


def compact_product_list(result: Dict[str, Any]) -> Dict[str, Any]:
    section = _primary_section(result)
    items = [_product_core_fields(item) for item in _extract_items(section) if _product_core_fields(item)]
    return _wrap_list(section, items)


def compact_product_detail(result: Dict[str, Any]) -> Dict[str, Any]:
    section = _primary_section(result)
    payload = _product_core_fields(section)
    payload.update(
        _strip_empty_fields(
            {
                "ingredient": _pick(section, "ingredientNameKor", "ingredient", "mainIngredientName"),
                "packUnit": _pick(section, "packUnit", "PackUnit"),
                "packQty": _pick(section, "packQty", "PackQty"),
                "form": _pick(section, "form", "Form", "dosageForm"),
                "marketing": _pick(section, "marketingAuthorizationHolder", "marketingAuthorization"),
                "image": _pick(section, "imageUrl", "ImageURL", "image"),
            }
        )
    )
    return payload


def compact_product_edicode_list(result: Dict[str, Any]) -> Dict[str, Any]:
    """EDI 코드 검색 응답을 제품 목록 요약으로 변환."""
    return compact_product_list(result)


def compact_same_ingredient_list(result: Dict[str, Any]) -> Dict[str, Any]:
    section = _primary_section(result)
    items: List[Dict[str, Any]] = []
    for item in _extract_items(section):
        slim = _product_core_fields(item)
        reference = _strip_empty_fields(
            {
                "reference": _pick(item, "ReferenceProductCode", "referenceProductCode"),
                "isOriginal": _pick(item, "isOriginal", "IsOriginal"),
            }
        )
        if reference:
            slim.update(reference)
        if slim:
            items.append(slim)
    return _wrap_list(section, items)


def compact_generic_list(result: Dict[str, Any]) -> Dict[str, Any]:
    section = _primary_section(result)
    items = _extract_items(section)
    return _wrap_list(section, items)



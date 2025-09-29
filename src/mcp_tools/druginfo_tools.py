from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

from src.druginfo import (
    list_main_ingredient,
    get_main_ingredient_by_code,
    list_product,
    get_product_by_code,
    UnauthorizedError,
    DrugInfoError,
    list_main_ingredient_drug_effect,
    get_main_ingredient_drug_effect_by_id,
    list_main_ingredient_drug_kind,
    list_main_ingredient_guide_a4,
    list_main_ingredient_guide_a5,
    list_main_ingredient_picto,
    get_main_ingredient_picto_by_code,
    list_product_edicode,
    list_product_edicode_same_ingredient,
)
from src.mcp_tools.auth_tools import _try_auto_login
from src.druginfo.response_filters import (
    compact_generic_list,
    compact_main_ingredient_detail,
    compact_main_ingredient_list,
    compact_product_detail,
    compact_product_edicode_list,
    compact_product_list,
    compact_same_ingredient_list,
)


def _safe_compact(compactor, payload):
    if compactor is None:
        return payload
    try:
        compacted = compactor(payload)
        return compacted if compacted is not None else payload
    except Exception:
        return payload


def register_druginfo_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="druginfo_list_main_ingredient")
    def druginfo_list_main_ingredient(
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
        default_page_size = 5
        default_page = 1
        effective_page_size = PageSize if PageSize is not None else (size if size is not None else default_page_size)
        effective_page = Page if Page is not None else (page if page is not None else default_page)

        try:
            return _safe_compact(
                compact_main_ingredient_list,
                list_main_ingredient(
                    a4=a4,
                    a4Off=a4Off,
                    a5=a5,
                    a5Off=a5Off,
                    drugkind=drugkind,
                    drugkindOff=drugkindOff,
                    effect=effect,
                    effectOff=effectOff,
                    showMapped=showMapped,
                    IngredientCode=IngredientCode,
                    ingredientNameKor=ingredientNameKor,
                    drugKind=drugKind,
                    PageSize=effective_page_size,
                    Page=effective_page,
                    SortBy=SortBy,
                    q=q,
                    page=page,
                    size=size,
                    timeout=int(timeout),
                ),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_main_ingredient_list,
                list_main_ingredient(
                    a4=a4,
                    a4Off=a4Off,
                    a5=a5,
                    a5Off=a5Off,
                    drugkind=drugkind,
                    drugkindOff=drugkindOff,
                    effect=effect,
                    effectOff=effectOff,
                    showMapped=showMapped,
                    IngredientCode=IngredientCode,
                    ingredientNameKor=ingredientNameKor,
                    drugKind=drugKind,
                    PageSize=effective_page_size,
                    Page=effective_page,
                    SortBy=SortBy,
                    q=q,
                    page=page,
                    size=size,
                    timeout=int(timeout),
                ),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_get_main_ingredient_by_code")
    def druginfo_get_main_ingredient_by_code(code: str, timeout: int = 15) -> Dict[str, Any]:
        try:
            return _safe_compact(
                compact_main_ingredient_detail,
                get_main_ingredient_by_code(code=code, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_main_ingredient_detail,
                get_main_ingredient_by_code(code=code, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_product")
    def druginfo_list_product(
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
        default_page_size = 5
        default_page = 1
        effective_page_size = PageSize if PageSize is not None else (size if size is not None else default_page_size)
        effective_page = Page if Page is not None else (page if page is not None else default_page)

        try:
            return _safe_compact(
                compact_product_list,
                list_product(
                    crop=crop,
                    cropOff=cropOff,
                    base64=base64,
                    base64Off=base64Off,
                    watermark=watermark,
                    watermarkOff=watermarkOff,
                    confirm=confirm,
                    confirmOff=confirmOff,
                    teoulLengthShort=teoulLengthShort,
                    teoulLengthShortOff=teoulLengthShortOff,
                    teoulLengthLong=teoulLengthLong,
                    teoulLengthLongOff=teoulLengthLongOff,
                    minCount=minCount,
                    ProductCode=ProductCode,
                    pillName=pillName,
                    vendor=vendor,
                    PageSize=effective_page_size,
                    Page=effective_page,
                    SortBy=SortBy,
                    q=q,
                    page=page,
                    size=size,
                    timeout=int(timeout),
                ),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_product_list,
                list_product(
                    crop=crop,
                    cropOff=cropOff,
                    base64=base64,
                    base64Off=base64Off,
                    watermark=watermark,
                    watermarkOff=watermarkOff,
                    confirm=confirm,
                    confirmOff=confirmOff,
                    teoulLengthShort=teoulLengthShort,
                    teoulLengthShortOff=teoulLengthShortOff,
                    teoulLengthLong=teoulLengthLong,
                    teoulLengthLongOff=teoulLengthLongOff,
                    minCount=minCount,
                    ProductCode=ProductCode,
                    pillName=pillName,
                    vendor=vendor,
                    PageSize=effective_page_size,
                    Page=effective_page,
                    SortBy=SortBy,
                    q=q,
                    page=page,
                    size=size,
                    timeout=int(timeout),
                ),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_get_product_by_code")
    def druginfo_get_product_by_code(code: str, timeout: int = 15) -> Dict[str, Any]:
        try:
            return _safe_compact(
                compact_product_detail,
                get_product_by_code(code=code, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_product_detail,
                get_product_by_code(code=code, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_main_ingredient_drug_effect")
    def druginfo_list_main_ingredient_drug_effect(
        edit: Optional[str] = None,
        pageSize: Optional[int] = None,
        page: Optional[int] = None,
        sortBy: Optional[str] = None,
        timeout: int = 15,
    ) -> Dict[str, Any]:
        if pageSize is None:
            pageSize = 10
        if page is None:
            page = 1
        try:
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_drug_effect(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_drug_effect(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_get_main_ingredient_drug_effect_by_id")
    def druginfo_get_main_ingredient_drug_effect_by_id(effectId: int, timeout: int = 15) -> Dict[str, Any]:
        try:
            return get_main_ingredient_drug_effect_by_id(effect_id=int(effectId), timeout=int(timeout))
        except UnauthorizedError:
            _try_auto_login(timeout)
            return get_main_ingredient_drug_effect_by_id(effect_id=int(effectId), timeout=int(timeout))
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_main_ingredient_drug_kind")
    def druginfo_list_main_ingredient_drug_kind(edit: Optional[str] = None, pageSize: Optional[int] = None, page: Optional[int] = None, sortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
        if pageSize is None:
            pageSize = 10
        if page is None:
            page = 1
        try:
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_drug_kind(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_drug_kind(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_main_ingredient_guide_a4")
    def druginfo_list_main_ingredient_guide_a4(edit: Optional[str] = None, pageSize: Optional[int] = None, page: Optional[int] = None, sortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
        if pageSize is None:
            pageSize = 10
        if page is None:
            page = 1
        try:
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_guide_a4(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_guide_a4(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_main_ingredient_guide_a5")
    def druginfo_list_main_ingredient_guide_a5(edit: Optional[str] = None, pageSize: Optional[int] = None, page: Optional[int] = None, sortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
        if pageSize is None:
            pageSize = 10
        if page is None:
            page = 1
        try:
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_guide_a5(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_guide_a5(edit=edit, pageSize=pageSize, page=page, sortBy=sortBy, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_main_ingredient_picto")
    def druginfo_list_main_ingredient_picto(IsDeleted: Optional[str] = None, Title: Optional[str] = None, PageSize: Optional[int] = None, Page: Optional[int] = None, SortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
        if PageSize is None:
            PageSize = 5
        if Page is None:
            Page = 1
        try:
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_picto(IsDeleted=IsDeleted, Title=Title, PageSize=PageSize, Page=Page, SortBy=SortBy, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_generic_list,
                list_main_ingredient_picto(IsDeleted=IsDeleted, Title=Title, PageSize=PageSize, Page=Page, SortBy=SortBy, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_get_main_ingredient_picto_by_code")
    def druginfo_get_main_ingredient_picto_by_code(code: str, timeout: int = 15) -> Dict[str, Any]:
        try:
            return get_main_ingredient_picto_by_code(code=code, timeout=int(timeout))
        except UnauthorizedError:
            _try_auto_login(timeout)
            return get_main_ingredient_picto_by_code(code=code, timeout=int(timeout))
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_product_edicode")
    def druginfo_list_product_edicode(ProductCode: Optional[str] = None, EdiCode: Optional[str] = None, PageSize: Optional[int] = None, Page: Optional[int] = None, SortBy: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
        if PageSize is None:
            PageSize = 5
        if Page is None:
            Page = 1
        try:
            return _safe_compact(
                compact_product_edicode_list,
                list_product_edicode(ProductCode=ProductCode, EdiCode=EdiCode, PageSize=PageSize, Page=Page, SortBy=SortBy, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_product_edicode_list,
                list_product_edicode(ProductCode=ProductCode, EdiCode=EdiCode, PageSize=PageSize, Page=Page, SortBy=SortBy, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    @mcp.tool(name="druginfo_list_product_edicode_same_ingredient")
    def druginfo_list_product_edicode_same_ingredient(ProductCode: Optional[str] = None, EdiCode: Optional[str] = None, MasterIngredientCode: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
        try:
            return _safe_compact(
                compact_same_ingredient_list,
                list_product_edicode_same_ingredient(ProductCode=ProductCode, EdiCode=EdiCode, MasterIngredientCode=MasterIngredientCode, timeout=int(timeout)),
            )
        except UnauthorizedError:
            _try_auto_login(timeout)
            return _safe_compact(
                compact_same_ingredient_list,
                list_product_edicode_same_ingredient(ProductCode=ProductCode, EdiCode=EdiCode, MasterIngredientCode=MasterIngredientCode, timeout=int(timeout)),
            )
        except DrugInfoError as e:
            raise RuntimeError(str(e))

    # --- Non-GET tool wrappers removed (POST-only tools no longer exposed) ---


# DrugInfo MCP - Data Schema (Generated)

> 이 문서는 EDB Admin API 응답 스키마를 기반으로 작성되었습니다.
> 실제 데이터베이스 스키마가 아닌 API 응답 구조를 기술합니다.

## Main Ingredient (주성분)

### List Response
```json
{
  "data": {
    "items": [...],
    "totalCount": 123,
    "page": 1,
    "pageSize": 20
  }
}
```

### Item Fields
| Field | Type | Description |
|---|---|---|
| ingredientNameKor | string | 주성분 한글명 |
| IngredientCode | string | 주성분코드 (9자리) |
| MasterIngredientCode | string | 마스터 주성분코드 |
| ATCCode | string | ATC 코드 (7자리) |
| DosageRoute | string | 투여경로 (A:내복, B:주사, C:외용, D:기타) |
| DosageForm | string | 제형 |

## Product (제품)

### Item Fields
| Field | Type | Description |
|---|---|---|
| productCode / ProductCode | string | 제품코드 (15자리) |
| productName / pillName | string | 제품명 |
| ediCode / EdiCode | string | EDI 코드 (보험코드, 9자리) |
| vendor / Vendor | string | 제조사 |
| masterIngredientCode | string | 마스터 주성분코드 |
| DosageForm | string | 제형 |
| strength / Strength | string | 함량 |
| korange | object | 생물학적동등성 정보 |

### korange Object
| Field | Type | Description |
|---|---|---|
| 생동PK | string ("True"/"False") | PK 생동성시험 완료 여부 |
| 제네릭 | string ("True"/"False") | 제네릭 의약품 여부 |
| 공공대조약 | string ("True"/"False") | 공공 대조약품 여부 |
| 특허 | string ("True"/"False") | 특허 보호 여부 |
| 취하일 | string (날짜 또는 빈문자열) | 허가 취하일 |
| 함량 | string (예: "70.23MG") | 주성분 함량 |

## Compacted Response (response_filters.py)

### compact_product_list Output
```json
{
  "items": [
    {
      "name": "제품명",
      "code": "ProductCode",
      "ediCode": "EDI코드",
      "vendor": "제조사",
      "masterCode": "마스터주성분코드",
      "dosageForm": "제형",
      "strength": "함량",
      "korange": { "생동PK": "True", ... }
    }
  ],
  "total": 123,
  "page": 1,
  "pageSize": 5,
  "hasMore": true
}
```

### compact_main_ingredient_list Output
```json
{
  "items": [
    {
      "name": "주성분명",
      "code": "주성분코드",
      "masterCode": "마스터코드",
      "atcCode": "ATC코드",
      "dosageRoute": "투여경로",
      "dosageForm": "제형"
    }
  ],
  "total": 45,
  "page": 1,
  "pageSize": 5,
  "hasMore": true
}
```

## Login Response

```json
{
  "accessToken": "jwt_token_string",
  "data": {
    "accessToken": "jwt_token_string"
  }
}
```

토큰 추출은 `extract_token()`이 재귀적으로 탐색:
accessToken > access_token > refreshToken > token > jwt > id_token

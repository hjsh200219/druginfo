# DrugInfo 도구 사용 가이드

> CLAUDE.md에서 분리된 상세 가이드

## 효율적인 검색 전략

### 1. 제품 검색 워크플로우
```python
# Step 1: 제품명으로 검색
druginfo_list_product(pillName="타이레놀", PageSize=5)
# -> ProductCode 추출

# Step 2: 상세 정보 조회
druginfo_get_product_by_code(code="추출한_ProductCode")
# -> 성분, korange 필드, 이미지 등 확인
```

### 2. 동일 성분 의약품 검색
```python
# 토큰 효율적인 전용 도구 사용
druginfo_list_product_edicode_same_ingredient(
    ProductCode="기준제품코드",
    MasterIngredientCode="주성분코드"
)
```

### 3. 생물학적동등성(생동) 필터링
- API에서 직접 필터링 불가
- 응답 후 `korange.생동PK == "True"` 로컬 필터링

## 의약품 코드 체계

### ProductCode (15자리) - 터울 자체 생성 코드
- 구조: `[의약품구분(1)][품목기준코드(9)][주성분코드끝3자리(3)][난수(2)]`
- 예시: `E201207542ATB7D`
  - E: 전문의약품 (O: 일반, T: 터울자체)
  - 201207542: 품목기준코드
  - ATB: 주성분 투여경로+제형
  - 7D: 구별용 난수

### 주성분코드 (9자리)
- 구조: `[주성분번호(3)][함량번호(3)][투여경로(1)][제형(2)]`
- 예시: `553304ATD`
  - 553: 주성분 (실데나필)
  - 304: 함량
  - A: 내복 (B:주사, C:외용, D:기타)
  - TD: 정제
- 동일성분 판별: 앞 4자리 + 7번째 자리 동일

### korange 필드 해석
- `생동PK`: "True"/"False" - PK 생동성시험 완료
- `제네릭`: "True"/"False" - 제네릭 의약품
- `공공대조약`: "True"/"False" - 공공 대조약품
- `특허`: "True"/"False" - 특허 보호 여부

## MCP 기능 목록

### 도구 (Tools)
- `login`: EDB 시스템 로그인
- `search_druginfo`: 의약품 통합 검색 (주성분/제품)
- `get_druginfo_detail`: 의약품 상세 조회 (코드 기반)
- `find_same_ingredient`: 동일 성분 의약품 검색
- `druginfo_list_main_ingredient`: 주성분 목록 검색
- `druginfo_get_main_ingredient_by_code`: 주성분 상세 조회
- `druginfo_list_product`: 제품 목록 검색
- `druginfo_get_product_by_code`: 제품 상세 조회
- `druginfo_list_product_edicode_same_ingredient`: 동일 성분 검색
- `druginfo_list_product_edicode`: EDI 코드 검색

### 리소스 (Resources)
- `druginfo://config/env-template`: 환경 설정 템플릿
- `druginfo://docs/code-system`: 의약품 코드 체계 문서
- `druginfo://docs/query-patterns`: 자주 사용하는 쿼리 패턴
- `druginfo://docs/korange-fields`: korange 필드 설명

### 프롬프트 (Prompts)
- `druginfo_usage_guide`: 도구 사용 가이드라인
- `query_patterns`: 자주 사용하는 쿼리 패턴
- `search_product`: 제품 검색 워크플로우
- `find_bioequivalent`: 생물학적동등성 검색 가이드

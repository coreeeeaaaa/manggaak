# 지능형 망각 시스템 v2 — 고도화 설계 스펙

## 0. 목표와 범위
- **목표**: 데이터베이스/파일·객체 스토리지/로컬·디바이스/클라이언트 캐시/로그/문서/AI 아티팩트에 대해, 다축 스코어·정책·학습 기반으로 자동 경량화·판별·망각을 수행하면서 규제/업무/리스크 제약을 충족하고, 부피가 목표치로 수렴하도록 하는 범용 엔진.
- **범위**: 온프/클라우드/에지, 온라인·배치 모두 지원. 규제 태그(GDPR, ISO 27001, SOC, 내부 보존 규칙)와 데이터 클래스(PII, 로그, 모델, 문서 등)별 차등 정책 적용.
- **비전**: “의미론적·물리적 부피를 동시에 제어”하는, 정책·학습·가역성까지 포함한 통합 망각 오케스트레이터.

## 1. 설계 원칙
- **다축 판단**: 중요도/사용/의미론/시간/맥락/리스크/중복 축의 정규화 벡터 기반 결정.
- **제약 우선**: 규제·계약·업무 중요도는 하드 제약으로, 최적화는 제약 내에서만 수행.
- **예산 수렴**: 스토리지/의미론적 부피/캐시/로그별 예산을 두고 우선순위 큐로 낮은 가치부터 방출.
- **가역성 관리**: 단계별 reversible state → 비가역 전환(키 파기)은 게이트 통과 시만.
- **관측 가능성**: 결정 근거, 스코어, 제약 위반 여부, 실행/오류 로그, 키/스냅샷 상태를 원장화.
- **학습 가능성**: 오탐/정탐 피드백으로 가중치·임계값·전략 선택 확률을 온라인 업데이트.

## 2. 데이터 모델·용어
- **데이터 항목(DataItem)**: 어떤 저장 단위든 식별 가능한 최소 단위(행/파일/객체/캐시 엔트리/로그 레코드/모델 아티팩트).
- **메타(Meta)**: 규제 태그, 도메인, 역할, 리스크 레벨, 생성/갱신 시각, 소스, 참조 링크, 컨텍스트 해시.
- **의미론 피처(SemanticFeatures)**: 임베딩/주제/개념 계층, 중복도, MI(상호정보량) 등.
- **가역성 단계(ReversibilityState)**: {원본, 압축, 마스킹, 핵심추출, 암호화, 키분산, 키파기}.

## 3. 다축 스코어링
- 입력 벡터 `x = [importance, usage, semantic, temporal, context, risk, redundancy] ∈ [0,1]^7`.
- 가중치 `w`는 학습 가능하며 제약으로 `w_i ≥ 0, Σw_i = 1`.
- 정규화 함수: min-max, 로그 스케일, winsorization 적용 후 clip.[0,1].
- 추가 제약: `risk` 축은 penalty로 사용(높을수록 보존 우선), `redundancy`는 역가치(높을수록 망각 가중).
- 합성 스코어 예시: `s = w · x`, 또는 소형 MLP/GBDT 등 `f(x)`.
- 시간 감쇠(에빙하우스/포아송 혼합): `temporal = exp(-t/τ) * α + P(access_future|ctx) * (1-α)`.
- 사용 감쇠: 세션/시간대 포아송, 최근성 가중 이동평균, 실패/성공 쿼리 비율.

## 4. 목적 함수와 제약
- 목적 함수(다목적):
  - `J = λ1·(보존 가치) - λ2·(저장 비용) - λ3·(규제/리스크 위반 기대비용) - λ4·(지연/복원 비용) - λ5·(쿼리 품질 저하)`
  - 보존 가치는 중요도/의미론/미래 접근 확률로 근사, 비용은 스토리지·네트워크·CPU·메모리 추정값.
- 하드 제약: 규제 태그별 최소 보존 기간, 삭제 금지/지연, 롤 기반 접근 제어, 감사 로그 의무, 비가역 전환 승인.
- 소프트 제약: 예산 초과 시 우선순위 큐 기반 망각, 리스크 스코어에 따른 보존 편향.

## 5. 정책 매핑(상태기계)
- 입력: `(s, meta.tags, class, risk_level, budget_state, reversibility_state)`.
- 출력: 전략 `{defer, cache_retain, compress, semantic_preserve, mask, archive, delete, key_destroy}` 및 파라미터(압축률, 마스킹 강도, 지연시간, TTL 등).
- 정책 테이블은 클래스/규제/리스크별로 정의, 임계값은 adaptive(학습) 가능.
- 가드레일: 비가역 전환은 승인이 필요하며, 필수 보존/규제 태그는 delete/key_destroy 불가.

## 6. 실행 전략 레이어
- **gradual_compression**: 무손실→손실 압축 계단, 중요 필드 보호.
- **semantic_preservation**: 요약/임베딩만 보존, 원본 축소.
- **predictive_caching**: 미래 접근 확률 높은 항목 보존/캐시.
- **adaptive_threshold**: 클래스/리스크별 임계값 실시간 조정.
- **masking/anonymization**: PII/민감 필드 마스킹/총계화.
- **archival**: 저비용 스토리지로 이동, TTL 부여.
- **deletion/key_destroy**: 비가역 삭제, 키 파기.

## 7. 예산/부피 수렴
- 글로벌/도메인/테이블/캐시/로그별 예산(`storage_budget`, `semantic_budget`) 관리.
- 우선순위 큐: `(priority = s_adj)` 낮은 항목부터 망각. `s_adj`는 리스크/제약/중복을 반영한 조정 스코어.
- 워터마크 제어: 예산 상한 초과 시 망각 트리거, 하한 도달 시 지연/보존 전환.

## 8. 중복·의미론 경량화
- 중복도: 해시/LSH/벡터 유사도, MI 기반 저정보량 탐지.
- 우선순위: 높은 중복·낮은 중요/사용 항목을 먼저 압축/삭제 → 의미론적 부피 감소.

## 9. 가역성·키 관리
- 단계별 스냅샷/메타: {원본, 압축본, 마스킹본, 핵심추출, 암호화본, 키 상태}를 트래킹.
- 비가역 게이트: 규제/승인/쿨다운 충족 시에만 `key_destroy` 실행.

## 10. 학습 옵티마이저
- 피드백: 오탐(과도 삭제/압축)·정탐(불필요 보존) 이벤트.
- 업데이트: 가중치/임계값/전략 선택 확률을 경량 밴딧/베이지안으로 온라인 조정.
- 안전장치: 학습률 상한, 리스크 페널티, 롤백 가능한 스냅샷.

## 11. 관측·감사·오류 관리
- 로그: 결정 입력/스코어/정책/전략/결과/오류/재시도/백오프.
- 감사 원장: 가역성 상태, 키 이벤트, 제약 검증 결과, 승인 흔적.
- 오류 처리: 네트워크/스토리지/의존 서비스 장애 시 재시도/백오프, SLA 타임아웃, 폴백(보존/지연).

## 12. 인터페이스(초안)
- `MultidimensionalAnalyzer.analyze(item: DataItem) -> ScoreVector`
- `DecisionEngine.select(score, meta, budget_state, rev_state) -> StrategyPlan`
- `StrategyExecutor.apply(plan, item) -> Result`
- `LearningOptimizer.update(feedback_event)`
- `BudgetManager.evaluate() -> triggers`
- `Ledger.log(event)`

## 13. 테스트·평가
- 스코어 정규화/범위 테스트.
- 정책 회귀: 고정 입력→예상 전략.
- 예산 수렴 시뮬레이션: 부피가 목표치로 수렴하는지 검증.
- 가역성/게이트 테스트: 제약 위반 시 비가역 전환 차단 검증.
- 학습 안정성: 오탐/정탐 피드백 후 수렴/변동성 검증.

## 14. 샘플 워크플로(의사코드)
```python
item = load_data_item()
scores = analyzer.analyze(item)
plan = decision_engine.select(scores, item.meta, budget_state, rev_state)
result = strategy_executor.apply(plan, item)
ledger.log(plan, result, scores)
learning_optimizer.update(result.feedback)
```

## 15. 구현 메모
- 모듈 구조: `core/{intelligent_forgetting.py, multidimensional_analyzer.py, decision_engine.py, learning_optimizer.py, context_manager.py}`; `algorithms/*`(축별 계산); `strategies/*`(압축/마스킹/보존/캐시/삭제/키 관리).
- 의존성 최소화, CPU/메모리 친화적 구현을 우선, 확장성 있는 인터페이스로 스토리지 계층별 어댑터 분리.

## 16. v1 → v2 맵핑 (철학/구조 계승)
- **9단계 가역성**: v1 단계(0~9)를 v2 `reversibility_state`로 유지. `key_destroy`는 단계 9 게이트(승인/규제 검증 필요), 단계 7~8은 키 의존 가역.
- **4차원 마스킹**: v1 X/Y/Z/T 조합을 v2 `masking_strength` 프로필로 포함(단일/이중/삼중/4중 조합). 전략 실행 시 보안점수/복원율을 파라미터화.
- **보존율 임계값**: v1 Stage 1~6 보존율 임계값을 v2 `policy thresholds`로 넣어 압축/마스킹/핵심추출 후 검증 훅에 적용.
- **Crypto Shredding 절차**: v1의 사전 검증→키 분산→암호화→키 파기→최종 검증 단계를 v2 `key_destroy` 플로우의 표준 시퀀스로 채택. 승인/로그/증빙을 원장화.
- **감사/규제 준수**: ISO 27001, GDPR, NIST 800-88, DoD 5220.22-M 준수 요구를 유지하고, 결정/실행/키 이벤트를 원장에 기록.

## 17. 구현 우선 검증 시나리오 (v1 회귀 포함)
- 9단계 가역성 상태 전이: 0→8까지 가역, 9에서 비가역 전환 차단/허용 여부 테스트.
- 4D 마스킹 프로필 적용: X/Y/Z/T 및 조합별 강도 파라미터가 기대 마스킹율 범위에 있는지 검증.
- 보존율 임계값 체크: 압축/마스킹/핵심추출 후 Stage 1~6 임계값 만족 여부.
- key_destroy 게이트: 규제 태그/승인 없이 비가역 전환 시도 시 차단되는지, 승인 후 통과되는지.

## 18. 최신 연구 반영 포인트 (적용 훅)
- **Influence 기반 언러닝**: RapidUn류 영향 재가중 기법을 모델/아티팩트 전략(`model_unlearn_fast`)에 연결.
- **파급효과 회귀테스트**: RippleBench 아이디어로 정책/전략 변경 후 품질·편향 영향 회귀.
- **비가역 언러닝 게이트**: 확산모델 비가역 언러닝처럼 승인·증빙 필요 조건을 `key_destroy`에 반영.
- **의미 기반 캐싱/축출**: 임베딩/유사도 기반 캐시 TTL 단축·압축/삭제 우선순위(`semantic-aware eviction`).
- **온디맨드 로딩**: MoE/대형 모델 가중치를 필요 시 로딩해 저장·메모리 압박 완화.

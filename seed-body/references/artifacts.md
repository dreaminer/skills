# Seed Body 산출물 포맷

대원칙: 작업 코퍼스는 *사람이 읽어 가장 명확한 문장형*으로 쓰고, 캐노니컬 2문서는
아래 고정 뼈대 구조로 쓴다. `{term}`은 미확정 후보 용어(코퍼스·큐 전용),
`[Term]`은 승급된 캐노니컬 용어다. 캐노니컬 파일에 `{term}`이 새면 안 된다.

## 목차

- [경로](#경로)
- [발화 근거](#발화-근거-evidence)
- [캐노니컬 2문서](#캐노니컬-2문서)
- [raw 흐름 코퍼스와 구현 수단 파킹](#raw-흐름-코퍼스와-구현-수단-파킹)
- [후보 계약](#seed_body_candidatesmd--sb-nnn-후보-계약)
- [PRIOR 계약](#seed_body_priormd--pr-nnn-위험순-질문-재료)
- [LATER·QUESTIONS·CRITERIA·REJECTED](#later--questions--criteria--rejected)

## 경로

```text
.scratch/seed-body/SEED_BODY_ESSENTIAL_FLOWS.md   # raw Essential 흐름 코퍼스
.scratch/seed-body/SEED_BODY_SYSTEM_PARKING.md    # Essential 바깥 실행 수단 원문 (선택적 내용)
.scratch/seed-body/SEED_BODY_PRIOR.md             # bounded 위험순 질문 재료 (승급·이동 없음)
.scratch/seed-body/SEED_BODY_HARVEST.md           # Domain 수확 리포트
.scratch/seed-body/SEED_BODY_CANDIDATES.md        # SB-nnn 후보 큐
.scratch/seed-body/SEED_BODY_LATER.md             # v1 밖 후보 (명시 승인만 입장)
.scratch/seed-body/SEED_BODY_QUESTIONS.md         # 확정된 유보
.scratch/seed-body/SEED_BODY_CRITERIA.md          # v1 정의 기준 (종료 게이트, lazy 생성)
.scratch/seed-body/SEED_BODY_REJECTED.md          # 명시적 기각 기록 (선택적)
```

승급 시 대상 프로젝트 `docs/` 아래에 materialize/이동한다. 핵심 산출물은 앞의 2개, 이어지는
4개는 고정 인계 문서, 마지막 1개는 선택 감사 문서다. 고정 인계 문서는 내용이 없어도 헤더와
`없음` 상태를 둔다.

```text
docs/ESSENTIAL_DOMAIN.md         # materialize (v1 확정만)
docs/ESSENTIAL_USECASE.md        # materialize (v1 확정만)
docs/SEED_BODY_SYSTEM_PARKING.md # 그대로 이동 (후속 System 스킬의 입력)
docs/SEED_BODY_LATER.md          # 그대로 이동 (살아있는 피드백 소스)
docs/SEED_BODY_QUESTIONS.md      # 그대로 이동 (downstream으로 들려보냄)
docs/SEED_BODY_CRITERIA.md       # 스냅샷 보존 (게이트 통과의 증거)
docs/SEED_BODY_REJECTED.md       # 명시적 기각이 있을 때만 이동 (선택 감사 문서)
```

내용이 없는 고정 인계 문서는 다음 형식으로 materialize한다.

```md
# SEED_BODY_LATER

상태: 없음
```

기존 `docs/`에 같은 파일이 있으면 충돌 항목을 사용자에게 보여주고 결정받는다
(덮어쓰기 / 병합 / 보류). 이전 seed-body 산출물이 명백하면 교체 가능, 아니면 묻는다.

## 발화 근거 (Evidence)

Evidence는 **턴 참조 + 짧은 인용**이다. 코드가 없으므로 이것이 유일한 provenance다. LLM 유추([가정])가 비준되면 비준 턴이 근거가 된다.

```md
Evidence:
- T7 "결제할 때 적립카드를 대면" — 트리거
- T12 (비준) "맞아, 포인트는 즉시 쌓여야 해" — [가정] SB-004 승인
```

- `T{n}`은 대화 턴 순번. 파일 모드에서는 코퍼스 항목 id(`EF-nnn`/`SF-nnn`)로도 참조 가능.
- 인용은 사용자 발화를 짧게 그대로 딴다. LLM의 요약문은 근거가 아니다.
- 파킹 항목(`SF-nnn`)은 Evidence에 더해 `Trace:` 필드로 받치는 Essential을 반드시 가리킨다.

## 캐노니컬 2문서

뼈대는 고정이다. Evidence는 발화 근거를 쓴다.

```md
# ESSENTIAL_USECASE

## [Subject]

Given:
-

When:
-

Then:
-

Evidence:
- T{n} "인용" — 발화 근거
```

`ESSENTIAL_DOMAIN.md`는 `## [Subject]` + `Meaning:` + `Evidence:`,
Domain 항목에는 `피할 유사어:` 줄을 둘 수 있다 (수렴 비준된 canonical term + 기각된 별칭).
`ESSENTIAL_USECASE.md`의 Then은 **판정 가능한 문장**이어야 한다 — "보인다"가 아니라
무엇이 보이면 성공인지까지. 사용자가 시간·복구·품질을 성공 조건으로 요구하면 Then에 남기고,
그 조건을 달성할 구현 방법만 파킹한다. 역방향·예외 흐름도 v1 확정이면 유스케이스로 들어간다.

캐노니컬은 v1 몸체만 담는다. v1 바운더리 서술("한다/하지 않는다")은 별도 절이 아니라
**위치**로 표현된다 — 캐노니컬 = v1 안, `SEED_BODY_LATER.md` = v1 밖.

## raw 흐름 코퍼스와 구현 수단 파킹

한 항목 = 한 유스케이스 조각. 사용자 vocabulary 그대로, 문장형 + `{term}` 마킹.
코퍼스는 raw로 유지한다 — Domain 언어 재기술은 코퍼스를 고쳐 쓰지 않고 후보 큐에서 한다.

```md
# SEED_BODY_ESSENTIAL_FLOWS

## EF-001

Fragment:
- {회원}이 결제할 때 {적립카드}를 대면 → {포인트}가 쌓인다

Evidence:
- T3 "결제할 때 카드 대면 포인트요" — 원 발화

Notes:
- "적립카드" vs "멤버십카드" 혼용 — [충돌] SB-002 참조
```

Essential admission과 혼합 발화 분리는 [conversation-loop](conversation-loop.md)의 판정 순서를
따른다. `SEED_BODY_SYSTEM_PARKING.md` 항목(`SF-nnn`)은 사용자가 방법으로 말한 Essential 바깥의
실행·운영·기술 조각을 원문 그대로 보존하고, `Evidence:`와 받치는 Essential `Trace:`를 가진다.

```md
# SEED_BODY_SYSTEM_PARKING

## SF-001

Fragment:
- 공지를 푸시로 전달한다

Trace:
- EF-001 (공지가 대상자에게 보인다)

Evidence:
- T4 "푸시로 보내면 돼" — 사용자가 말한 실행 수단
```

파킹은 System 설계나 확정 요구가 아니다. seed-body는 내용을 발전시키지 않고, 후속 System
스킬이 다시 확인할 raw 시드로 넘긴다. 받치는 Essential 흐름이 없으면 파킹하지 않고
`[층미분류]`로 둔다.

## SEED_BODY_HARVEST.md

재발·공기·클러스터를 **제안**하되 이름과 의미를 결정하지 않는다. 구조는 클러스터 +
등장 흐름 목록으로 작성한다. 용어 자격과 harvest 대상 범위는
[closing-gate](closing-gate.md)의 harvest 절차를 따른다.

## SEED_BODY_CANDIDATES.md — SB-nnn 후보 계약

```md
# SEED_BODY_CANDIDATES

## SB-001

Type:
essential-domain

Label:
[가정]

Subject:
적립카드

Content:
- [적립카드]는 회원이 결제 시 제시하는 포인트 적립 수단이다.

Evidence:
- T3 "카드 대면 포인트요" — 원 발화

Blocked by:
-
```

- `Type`: `essential-domain | essential-usecase | unclassified-fragment`.
  `unclassified-fragment`는 admission 대기 원문이며 캐노니컬 승급 대상이 아니다. Essential로
  확인되면 `EF-nnn`으로, 받치는 Essential이 있는 실행 수단으로 확인되면 `SF-nnn`으로 옮긴다.
- `Label`: `[가정] [충돌] [층미분류]` 중 0~1개. 라벨은 이 큐 전용이다 — 사용자가
  직접 말했거나 승인한 항목은 라벨 없이 곧장 비준 대기(또는 배치 비준에 합류)한다.
- `Subject`는 Essential 후보에서만 쓰는 plain text이며 `[]`/`{}`를 넣지 않는다. 승급 시
  `## [Subject]` 헤더가 된다. `unclassified-fragment`는 Subject 대신 raw `Content`와 Evidence,
  제안한 분리를 기록한다.
- Essential 후보의 Content는 독립 확인 가능한 한 주장 또는 하나의 Given/When/Then이다.
  UseCase 재기술 후보의 Content 안 용어는 함께 큐잉된 Domain 후보를 참조한다 — `Blocked by:`로
  Domain을 먼저 묶는다. `unclassified-fragment`의 Content는 사용자 원문을 재기술하지 않는다.
- 같은 항목이 큐와 캐노니컬에 동시에 존재하지 않는다. 기각되면 폐기하고, 명시적 기각은
  `SEED_BODY_REJECTED.md`에 `SR-nnn`으로 기록해 같은 제안의 재투영을 막는다.

## SEED_BODY_PRIOR.md — PR-nnn 위험순 질문 재료

선정 기준과 run 상한은 [conversation-loop](conversation-loop.md)를 따른다. 캐노니컬로 승급되거나
Evidence가 되지 않으며, 종료 시 이동하지 않는다. 미처분 항목은 CRITERIA 필수 질문으로 승계한다.

```md
# SEED_BODY_PRIOR

카테고리: 멀티채널 주문관리 (T1 식별)

## PR-001

Aspect:
주문 취소·반품

Why-risk:
- 취소·반품을 처분하지 않으면 이미 발생한 주문 책임을 되돌릴 기준이 없다. (근거: 지식/웹검색)

처분:
- 질문 중 (T9)
```

처분 값: `미질문 | 질문 중(T{n}) | 답(EF-nnn) | 해당 없음(T{n}) | 유보(Q-nnn) | v1 밖(LATER)`.
"해당 없음"은 사용자 확인 턴이 있어야 한다.

## LATER / QUESTIONS / CRITERIA / REJECTED

- **SEED_BODY_LATER.md** — 항목: 문장형 조각 + v1 제외 이유 + 연결된 v1 코어.
  Essential 조각만 들어온다 (Essential 바깥 실행 수단은 admission 후 파킹). 무덤이 아니라 피드백 소스 —
  매 턴 승격 체크의 입력. 입장 조건은 사용자의 명시적 "v1 밖" 승인뿐.
  미비준 [가정]의 흡수처가 아니다.
- **SEED_BODY_QUESTIONS.md** — "지금 안 정한다"로 *확정된* 유보. 층·관련 슬롯·사유를 적고
  downstream으로 들려보낸다. 비필수 미결은 핸드오프를 막지 않는다.
- **SEED_BODY_CRITERIA.md** — 수요 문서. 내용 없이 필수 질문 + 답 상태 + 확정 문서
  포인터만. 답의 출처는 캐노니컬(스테이징 중에는 비준 통과 후보)뿐 — CRITERIA 자신,
  QUESTIONS, CANDIDATES는 출처가 아니다. 기각된 예시답안은 해당 질문에 기각 사실을 남긴다.
  포맷과 충족 판정은 [closing-gate](closing-gate.md)를 따른다.
- **SEED_BODY_REJECTED.md** — `## SR-nnn` + Type/Subject/Reason/Evidence(턴 참조).
  사용자가 명시적으로 기각한 것만. 검토 대기 중인 후보는 기각이 아니다. 내용이 있으면 종료
  패키지에 보존한다.

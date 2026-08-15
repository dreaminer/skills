# Seed Body 산출물 포맷

대원칙: 작업 상태는 *사람이 읽어 가장 명확한 문장형*의 자유 형식으로 쓰고, 승급 패키지는
아래 고정 구조로 쓴다. `{term}`은 미확정 후보 용어(작업 상태 전용), `[Term]`은 승급된
캐노니컬 용어다. 캐노니컬 파일에 `{term}`이나 작업 라벨이 새면 안 된다.

## 승급 패키지 — 대상 프로젝트 `docs/`

핵심 산출물 2개, 고정 인계 문서 4개, 선택 감사 문서 1개. 고정 인계 문서는 내용이 없어도
헤더와 `없음` 상태를 둔다. 이 파일명과 구조는 후속 스킬(seed-system)의 입력 계약이다.

```text
docs/ESSENTIAL_DOMAIN.md         # materialize (v1 확정만)
docs/ESSENTIAL_USECASE.md        # materialize (v1 확정만)
docs/SEED_BODY_SYSTEM_PARKING.md # 실행 수단 원문 SF 행 (후속 System 스킬의 입력)
docs/SEED_BODY_LATER.md          # 명시 승인된 v1 밖 Essential (살아있는 피드백 소스)
docs/SEED_BODY_QUESTIONS.md      # 확정된 유보 + 층·관련 슬롯·사유 (downstream으로 들려보냄)
docs/SEED_BODY_CRITERIA.md       # 게이트 통과 증거 스냅샷
docs/SEED_BODY_REJECTED.md       # 사용자가 명시 기각한 것만 (검토 대기는 기각이 아니다)
```

내용 없는 고정 인계 문서는 다음 형식으로 materialize한다.

```md
# SEED_BODY_LATER

상태: 없음
```

기존 `docs/`에 같은 파일이 있으면 충돌 항목을 사용자에게 보여주고 결정받는다
(덮어쓰기 / 병합 / 보류). 이전 seed-body 산출물이 명백하면 교체 가능, 아니면 묻는다.

## 발화 근거 (Evidence)

Evidence는 **턴 참조 + 짧은 인용**이다. 코드가 없으므로 이것이 유일한 provenance다.

```md
Evidence:
- T7 "결제할 때 적립카드를 대면" — 트리거
- T12 (비준) "맞아, 포인트는 즉시 쌓여야 해" — [가정] 승인
```

- `T{n}`은 대화 턴 순번. 파일 모드에서는 작업 항목 id(`EF-nnn`/`SF-nnn`)로도 참조 가능.
- 인용은 사용자 발화를 짧게 그대로 딴다. LLM의 요약문은 근거가 아니다.
- `[가정]`이 비준되면 비준 턴이 근거가 된다.

## 캐노니컬 2문서

뼈대는 고정이다.

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

`ESSENTIAL_DOMAIN.md`는 `## [Subject]` + `Meaning:` + `Evidence:`, Domain 항목에는
`피할 유사어:` 줄을 둘 수 있다 (수렴 비준된 canonical term + 기각된 별칭). `Subject`는
plain text이며 `[]`/`{}`를 넣지 않는다.

`ESSENTIAL_USECASE.md`의 Then은 **판정 가능한 문장**이어야 한다 — "보인다"가 아니라 무엇이
보이면 성공인지까지. 사용자가 시간·복구·품질을 성공 조건으로 요구하면 Then에 남기고, 그
조건을 달성할 구현 방법만 파킹한다. 역방향·예외 흐름도 v1 확정이면 유스케이스로 들어간다.
캐노니컬은 v1 몸체만 담는다 — v1 경계는 별도 절이 아니라 **위치**로 표현된다
(캐노니컬 = v1 안, LATER = v1 밖).

## 작업 상태 예시

한 항목 = 한 조각, 사용자 vocabulary 그대로, 문장형 + `{term}` 마킹. 코퍼스는 raw로
유지한다 — Domain 언어 재기술은 코퍼스를 고쳐 쓰지 않고 후보 큐에서 한다.

```md
# SEED_BODY_ESSENTIAL_FLOWS

## EF-001

Fragment:
- {회원}이 결제할 때 {적립카드}를 대면 → {포인트}가 쌓인다

Evidence:
- T3 "결제할 때 카드 대면 포인트요" — 원 발화

Notes:
- "적립카드" vs "멤버십카드" 혼용 — [충돌]
```

## SYSTEM_PARKING — SF 행

`SF-nnn`은 사용자가 방법으로 말한 Essential 바깥의 실행·운영·기술 조각을 원문 그대로
보존하고, `Evidence:`와 받치는 Essential `Trace:`를 반드시 가진다. 이 구조는 승급 후에도
유지된다 (downstream 입력 계약).

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

---
name: seed-body
description: 코드가 없는 출발점에서 사용자와의 문답으로 v1 Essential 몸체(ESSENTIAL_DOMAIN/ESSENTIAL_USECASE)를 심는 상류 기획 스킬. 비전은 보존하고 Essential 바깥의 실행 수단 발화는 원문 파킹해 후속 단계로 넘긴다.
disable-model-invocation: true
---

# Seed Body — 대화로 Essential 몸체 심기

코드가 없는 출발점에서 `사용자 발화 → Essential 흐름 → Domain harvest → UseCase 재기술`
순서로 v1 몸체를 만든다. 사람이 Essential의 유일한 진실원천이다.

결정 대상은 둘뿐이다.

1. **v1 Essential UseCase 집합**
2. **그 집합을 말할 Essential Domain 언어**

핵심 산출물은 `ESSENTIAL_DOMAIN.md`와 `ESSENTIAL_USECASE.md`다. 이 언어가 후속 System 도출,
PRD, 티켓, 구현, 검증의 공용 계약이 된다. 구현 수단을 선택하거나 System을 설계하는 일은
후속 단계에 맡긴다.

## 불변식

1. **발화 근거** — 캐노니컬의 모든 주장을 사용자 턴 참조와 짧은 직접 인용에 결박한다.
   LLM 유추는 `[가정]` 후보로만 제안하고, 사용자가 비준한 턴부터 근거가 된다.
2. **Essential admission** — 표현에 기술어가 있는지가 아니라 사용자가 요구하는 의미로 입장을
   판정한다. 의도·책임·관측 가능한 결과·정책·품질 제약은 Essential이다. 사용자가 그 결과를
   달성하는 방법으로 말한 실행 수단만 `SYSTEM_PARKING`에 원문 그대로 보존한다. 애매하면
   `[층미분류]`로 두고 한 번 확인한다.
3. **Harvest** — Domain을 선행 열거하지 않는다. Essential 흐름 코퍼스가 쌓인 뒤 재발·공기 또는
   load-bearing 싱글턴에서 수확하고, 사용자의 사용 이력으로 이름을 수렴한다.
4. **비전 보존과 v1 수렴** — 큰 비전은 보존한다. 처음 구현해 핵심 가치가 성립하는 최소 흐름을
   v1로 제안하고, 사용자가 명시적으로 승인한 v1 밖 Essential만 `LATER`에 둔다.
5. **Breadth-first** — 한 턴에 가장 값진 질문 하나만 묻고 같은 슬롯에 연속으로 매달리지 않는다.
   카테고리 프라이어는 bounded 위험순 질문 재료이며, 정답이나 Evidence가 아니다.
6. **Essential 인계 준비도** — v1 흐름의 판정 가능한 결과와 필요한 예외·권한 충돌·외부 약속이
   처분되고, CRITERIA의 필수 질문이 확정 내용으로 답을 가질 때만 종료 후보가 된다. 사용자가
   메타 기준과 전체 내용을 비준해야 캐노니컬로 승급한다.

## 실행

저장할 워크스페이스가 있으면 `.scratch/seed-body/`를 작업장으로 쓴다. 없으면 같은 파일별 상태를
대화 안에서 유지하고, 대화가 길어지면 파일 저장을 제안한다.

### 1. 발산

첫 응답 전에 [conversation-loop](references/conversation-loop.md)를 전부 읽고 그 턴 순서를 따른다.
Essential admission을 먼저 끝낸 뒤에만 `ESSENTIAL_FLOWS`에 기록한다. 실행 수단 조각은 내용을
발전시키지 않고 받치는 Essential 흐름으로 `Trace:`를 달아 파킹한다.

발산은 종료 임박 휴리스틱이 켜질 때까지 계속한다. 완료 조건은 새 조각을 코퍼스·파킹·LATER·
QUESTIONS 중 맞는 위치에 근거와 함께 두고, 활성 PRIOR가 대화 루프의 상한과 처분 규칙을
만족하는 것이다.

### 2. 수렴

종료 임박 휴리스틱이 켜지면 [closing-gate](references/closing-gate.md)를 전부 읽고 고정 순서로
실행한다. CRITERIA 질문 목록이 바뀌면 메타 비준부터 다시 받는다. 전체 몸체는 한 번의 배치
결정으로 비준받되, 길면 스테이징 파일에 전문을 쓰고 대화에는 요약과 위치를 제시한다.

수렴의 완료 조건은 모든 필수 질문이 확정 내용 포인터를 갖고, 사용자 내용 비준을 통과하며,
캐노니컬의 모든 `[Term]`이 DOMAIN에 해소되고 `{term}`·후보 라벨이 남지 않는 것이다.

### 3. 승급과 인계

승급 전에 [artifacts](references/artifacts.md)를 전부 읽는다. 이 문서를 파일명·포맷·Evidence·
핵심/고정 인계/선택 감사 구분의 단일 진실원천으로 삼아 정확히 materialize한다.

승급 후 캐노니컬과 인계 문서를 다시 읽어 정합성을 확인한다. 그 뒤 작업용 코퍼스·PRIOR·HARVEST·
CANDIDATES를 정리한다. 종료 시 다음 단계의 카테고리만 제시하고 실행은 사용자의 다음 요청에 맡긴다.

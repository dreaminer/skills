---
name: seed-loop
description: Orchestrates an explicitly started greenfield Seed run across Essential shaping, Acceptance design, and TDD. Use to start or resume seed-loop, continue its active human question or ratification, or receive an active Seed leaf's completion or blocker.
---

# Seed Loop

사용자는 `$seed-loop <프로젝트 경로 또는 만들 서비스 조각>`을 한 번 호출한다. 그 뒤에는 현재
산출물에서 owner를 다시 계산하고 `seed-body`·`seed-system`·`seed-tdd`를 연결해 진행한다.
사람의 답이 필요한 지점에서는 질문하고, 답을 받은 다음 같은 loop를 계속한다.

이 스킬은 phase 선택, upstream 변경 요청, downstream replay만 소유하는 얇은 control plane이다.
Domain·UseCase·Acceptance·구현 의미, 문서 스키마, 계약 hash, RED/GREEN 판정은 각 leaf와 기존
checker가 소유한다. orchestration 규칙을 바꾸기 전에는 `DESIGN.md`를 읽는다.

## 진입 계약

- 새 실행은 사용자의 명시적인 `$seed-loop` 또는 seed-loop 시작 요청으로만 연다.
- 열린 실행의 정확한 질문에 대한 답, leaf의 완료·blocker, 명시적인 재개 요청은 같은 실행을
  계속한다. target, current owner, outstanding question 중 하나도 식별되지 않으면 새로 추측해
  시작하지 말고 target 하나만 묻는다.
- 최초 loop 요청은 세 leaf를 정상적으로 연결할 실행 권한이다. 개별 `$seed-*` 재호출을
  요구하지 않는다.
- 실행 권한은 내용 승인 권한이 아니다. Essential, Acceptance, 구현 기본안의 기존 사람 비준
  지점에서는 반드시 멈추고 그 질문에 대한 답만 적용한다.
- 한 번에 mutating owner 하나만 실행한다.

이미 구현이 존재하고 Seed 산출물이 전혀 없는 프로젝트는 greenfield Seed 대상이 아니다.
legacy evidence 복원 흐름이 필요하다고 알리고 `SEED_LOOP_BLOCKED`로 반환한다. 시작된 Seed
package를 구현 도중 재개하는 경우에는 이 제한을 적용하지 않는다.

## 관측하고 owner 선택

매 진입과 leaf 반환 뒤에 target의 현재 파일을 다시 읽는다. 별도 phase status를 저장하지 않는다.

1. `.scratch/seed-loop/ACTIVE_CHANGE.md`가 있으면 그 owner와 원 증거를 먼저 재검증한다.
2. 다음 body package가 하나라도 없거나 body가 아직 비준되지 않았으면 `seed-body`를 선택한다.
   `ESSENTIAL_DOMAIN.md`, `ESSENTIAL_USECASE.md`, `SEED_BODY_SYSTEM_PARKING.md`,
   `SEED_BODY_LATER.md`, `SEED_BODY_QUESTIONS.md`, `SEED_BODY_CRITERIA.md`가 필수다.
   `SEED_BODY_REJECTED.md`는 선택이다.
3. body package만 있으면 seed-system checker를 `--links-only`로 실행한다. body-owned link 실패는
   `seed-body`로 돌려보내고, 통과하면 `seed-system`을 선택한다.
4. `ACCEPTANCE.md`, `SEED_SYSTEM_TESTS.md`, `SEED_SYSTEM_IMPL_PROPOSAL.md` 중 하나가 없거나
   기본 checker가 Acceptance 구조·coverage·seam·proposal 문제를 보고하면 `seed-system`을
   선택한다.
5. 기본 checker가 통과하고 lifecycle, marker, test, harness, production code에 RED·gap·결함이
   있으면 `seed-tdd`를 선택한다. 비준된 Acceptance 변경으로 stale marker가 된 경우도
   `seed-tdd`가 relink와 replay를 소유한다.
6. active change가 없고 `seed-tdd`의 이번 실행이 `SEED_TDD_COMPLETE`를 반환했으며 checker의
   `--complete`와 전체 suite·저장소 필수 검사가 모두 통과했을 때만 완료다.

checker 명령은 설치된 `seed-system/scripts/check-acceptance.py`를 사용한다. 구조 검사를 복제하거나
exit code를 말로 대체하지 않는다. `--links-only`는 `0=유효`, `1=링크 실패`, `2=실행 불가`다.
기본 checker와 `--complete`도 같은 exit code 계약을 따른다.

## owner 실행

선택한 model-invoked leaf 하나를 이름으로 호출하고 그 leaf의 `SKILL.md`와 필요한 resource를
완전히 읽어 그대로 실행한다.

- Essential 의미·v1 scope·outcome·Domain 언어는 `seed-body`가 소유한다.
- Acceptance behavior·public seam·구현 기본안·선언 test command는 `seed-system`이 소유한다.
- test marker·lifecycle·harness·test·production code는 `seed-tdd`가 소유한다.

leaf가 질문하면 그 질문 하나를 사용자에게 전달한다. leaf가 완료하거나 blocker를 반환하면 현재
파일과 gate를 다시 관측한 뒤 다음 owner로 자동 전이하거나 loop terminal을 반환한다. leaf의
완료 문장만 믿고 gate를 생략하지 않는다.

upstream 변경 요청은 승인된 edit가 아니라 leaf의 정상 change run 입력이다. 특히 body의 v1
질문·범위가 바뀌면 `seed-body`의 메타 비준(A)과 전체 몸체 비준(B)을 순서대로 통과한 뒤에만
materialize하고 replay한다. active change나 최초 loop 요청으로 이 순서를 단축하지 않는다.

## upstream 변경과 replay

downstream에서 upstream 결정이 필요하면 owner를 먼저 복구한 다음 영향받는 downstream을
dependency 순서로 replay한다. 여러 턴이나 owner를 건너는 변경에만
`.scratch/seed-loop/ACTIVE_CHANGE.md` 하나를 사용한다.

```md
Origin:
Owner:
Evidence:
Affected:
Decision needed:
Replay:
Last progress:
```

`Evidence`와 `Affected`에서 Seed 산출물의 정의를 언급할 때는 해당 문서의 정확한 `##` heading으로
가는 Markdown 링크를 쓴다. scratch 파일 안의 상대 링크는 `ACTIVE_CHANGE.md` 위치에서 실제
target과 fragment가 열리는지 확인한다. 정의 본문, phase 표, 새 ID 체계는 복사하지 않는다.
test/code는 project-relative path로 가리킨다. 짧은 단일 턴 변경이면 같은 정보를 대화에만
유지해도 된다.

- Essential 문서가 바뀌면 사람에게 다시 비준받고, `seed-system`이 모든 관련 AC와 간접 의미
  의존성을 영향 검토·재비준한 뒤 `seed-tdd`가 영향 slice와 전체 closing gate를 replay한다.
  heading과 AC hash가 그대로여도 이 순서를 생략하지 않는다.
- Acceptance·seam·구현 기본안이 바뀌면 `seed-system` 비준 뒤 `seed-tdd`가 stale marker와 영향
  slice부터 replay한다.
- 비준 계약 안의 harness·test·code 결함은 upstream으로 보내지 않고 `seed-tdd`가 계속 소유한다.

원 증거가 재검증에서 사라지고 replay가 모두 통과했을 때 active change를 닫고 scratch를 제거한다.
같은 owner 처리 뒤 authoritative artifact, 비준 근거, checker 결과 중 아무 진전 없이 같은 증거가
다시 나타나면 ping-pong하지 않고 block한다.

## terminal

완료 시 다음을 짧게 보고한다.

```text
SEED_LOOP_COMPLETE
```

완료에는 active change 없음, current-hash GREEN, 모든 `Then`의 선언 seam assertion, 비유예 구현
선택의 코드·설정·test 근거, 전체 suite, 저장소 필수 검사, checker `--complete`, 이번 실행의
`SEED_TDD_COMPLETE`가 모두 필요하다.

사람 결정, 충돌 문서 검토, 외부 조건 없이는 declared route를 진행할 수 없거나 같은 증거가
무진전으로 돌아오면 다음 형식으로 멈춘다. active scratch와 leaf evidence는 보존한다.

```text
SEED_LOOP_BLOCKED
Owner: <seed-body|seed-system|seed-tdd>
Evidence: <정확한 산출물 링크 또는 project-relative path>
Need: <사용자 또는 외부가 해야 할 한 가지>
Resume: $seed-loop <target>
```

## 첫 턴

target을 현재 workspace, 사용자가 준 경로, 서비스 조각 순서로 정한다. 관련 docs와 scratch를
먼저 조용히 읽고, 설명식 waterfall 개요 대신 다음 한 줄을 말한 뒤 선택한 leaf의 첫 턴 또는
재개 절차를 같은 턴에 시작한다.

```text
현재 <owner>부터 이어갈게 — <클릭 가능한 근거>.
```

active change가 owner 선택의 근거라면 이 링크는 scratch 파일 자체가 아니라 그 안에서 검증된
원 산출물의 정확한 definition heading을 가리킨다. 원 링크가 깨졌으면 owner를 실행하기 전에
`SEED_LOOP_BLOCKED`로 반환한다.

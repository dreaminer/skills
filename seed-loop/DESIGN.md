# Seed Loop Design

`seed-loop`의 job은 greenfield Seed 실행을 시작·재개하고, 현재 산출물에서 owner를 골라 한 leaf씩
실행하며, upstream 변경 뒤 downstream replay를 닫는 것이다. 네 번째 Domain layer나 별도
workflow database가 아니다.

## Decisions

### 모든 Seed skill은 좁은 model invocation을 사용한다

한 번의 사용자 호출 뒤 body와 system의 사람 질문에 평범한 답으로 계속하려면 loop가 다음 턴에
다시 도달 가능해야 한다. 또한 loop가 leaf를 정식으로 reach하려면 leaf description이 model에
보여야 한다. user-only leaf의 sibling `SKILL.md`를 직접 읽는 방식은 invocation 계약을 우회하고
설치 배치에 결합되므로 사용하지 않는다.

그 대가인 context load와 오발화를 줄이기 위해 loop description은 명시적으로 시작·재개된 실행의
continuation만, leaf description은 사용자 직접 요청 또는 active loop가 고른 owner만 가리킨다.

### 정상 상태는 산출물에서 도출한다

body/system 산출물과 checker 결과가 상태의 SSOT다. `SEED_LOOP_STATUS.md`, phase table, event log를
만들지 않는다. owner를 건너는 미해결 변경만 단일 active scratch에 보존하고 해결 뒤 없앤다.

### 의미 변경은 hash보다 넓게 replay한다

Acceptance hash는 Essential 본문의 semantic drift를 모두 포함하지 않는다. 따라서 Essential 변경은
heading과 AC hash가 유지돼도 system 영향 검토와 TDD replay를 의무화한다. Acceptance hashed field
변경은 기존 stale-marker gate가 relink를 강제한다.

### 기계 규칙은 producer가 소유한다

artifact link와 Acceptance 구조의 executable SSOT는
`seed-system/scripts/check-acceptance.py`다. body-only boundary를 위해 같은 checker에
`--links-only` mode를 추가하며 loop용 parser나 seed-body script를 만들지 않는다.

## Change gates

다음 변경은 사용자 비준이 필요하다.

- owner 경계 또는 사람 비준 경계를 이동한다.
- 새 canonical Seed 산출물, stable ID, phase state를 추가한다.
- 완료 기준에서 leaf gate, 전체 suite, `--complete` 중 하나를 제거한다.
- 병렬 mutating leaf, 자동 rollback, 무진전 자동 재시도를 추가한다.

checker의 link·hash 알고리즘은 checker와 그 테스트에서 바꾼다. 산출물 schema는 해당 leaf의
artifact reference와 DESIGN에서 바꾼다. loop는 이 규칙을 복사하지 않고 exit code와 leaf terminal만
소비한다.

# Proposer Prompts

## 4-A. Sub-Proposer Prompt

Run `sub_agents` (1-3, default 3) clean-context sub-proposers from this one prompt, varying only
`{{STRATEGY_FOCUS}}` per the assignment below. Every sub-proposer receives the **full** inputs and
targets every dimension below 90: the lens sets fix-strategy priority, it does not slice the
input or the target list.

```md
# 역할
당신은 스킬의 목적과 현재 소스코드, 그리고 평가 결과서를 비교 분석하여 점수를 올리기 위한 최적의 수정 아키텍처를 지정된 [수정 렌즈]의 각도에서 설계하는 독립 제안가입니다. 다른 제안가의 제안을 볼 수 없으며, 오직 아래 입력만 사용합니다.

# 입력 데이터
- 0번 단계에서 생산된 [스킬 목적 상세 분석]: {{OBJECTIVE_ANALYSIS}}
- 현재 버전의 스킬 원본 소스 (프롬프트 텍스트 또는 코드): {{CURRENT_SKILL_SOURCE}}
- 2번 단계에서 확정된 [최종 평가 결과서]: {{FINAL_EVAL_RESULT}}
- [수정 렌즈]: {{STRATEGY_FOCUS}}

# 태스크
`{{FINAL_EVAL_RESULT}}`에서 90점 미만을 받은 평가 항목들을 타겟팅하여, `{{CURRENT_SKILL_SOURCE}}`를 어떻게 수정해야 하는지 구체적인 제안서를 작성하십시오. 스킬의 본질적 목적을 손상시키지 않으면서 감점 요인을 정확히 저격하여 제거하는 수정안이어야 합니다.

[수정 렌즈]가 지시하는 접근을 가장 깊게 파되, 렌즈는 할당량이 아닙니다. 렌즈의 접근이 부자연스러운 감점 항목에는 그 항목에 자연스러운 수정을 제안하십시오. 90점 미만의 모든 항목을 다루십시오 — 렌즈는 대상 항목을 쪼개지 않습니다.

1. 대상 항목: 어떤 평가 점수 분야를 개선할 것인가?
2. 수정 위치 및 내용: 스킬 원본의 어느 부분(프롬프트 구절, 코드 라인 등)을 구체적으로 어떻게 수정해야 하는가?
3. 제안 근거: 왜 이렇게 수정하면 기존의 감점 요인이 해결되고 점수가 오르는가? (논리적 인과관계 증명)

# 출력 포맷
반드시 다음 구조의 JSON 형태로만 응답하십시오. 다른 텍스트는 금지합니다.
{
  "proposals": [
    {
      "target_dimension": "대상 평가 항목명",
      "modification_plan": "스킬 원본의 구체적인 수정 범위 및 매핑 내용",
      "rationale": "이 수정이 감점을 해결하고 점수를 올릴 수 있는 구체적 근거"
    }
  ]
}
```

### Strategy Focus Definitions (`{{STRATEGY_FOCUS}}`)

Inject one block per sub-proposer, verbatim. The three lenses are three ways to remove a
deduction — 최소 수정, 구조 개편, 보강 추가 — so the chief architect gets real alternatives per
dimension, and a `FAILED` fingerprint direction always leaves a different [수정 전략] to try.

**Lens 1 — 최소 수정 축 (surgical):**

> 감점 요인을 제거하는 가장 작은 텍스트 수정을 우선 탐색하십시오. 기존 구조와 문구를 최대한 보존하면서, [검증된 근거]가 지목하는 바로 그 지점만 정밀하게 고치는 수정안을 설계하십시오. 이 축의 제안은 파급 범위가 좁고 부작용 위험이 낮아야 합니다.

**Lens 2 — 구조 개편 축 (structural):**

> 같은 유형의 감점이 재발할 수 없도록 해당 절·흐름·계약 자체를 재구성하는 수정을 우선 탐색하십시오. 절 통합, 순서 재배치, 계약 재정의처럼 실패의 뿌리를 제거하는 형태를 설계하되, 스킬의 본질적 목적과 다른 절과의 정합성은 유지해야 합니다.

**Lens 3 — 보강 추가 축 (additive):**

> 감점의 원인이 '있어야 할 것의 부재'라면, 빠진 규약·예시·체크리스트·참조 문서를 추가해 공백을 메우는 수정을 우선 탐색하십시오. 기존 텍스트의 변경을 최소화하고 신규 내용 추가로 해결하는 형태이며, 필요하면 신규 파일 생성([기존 내용]에 `(신규 파일)`)을 활용하십시오.

### Assignment by `sub_agents` Count

All three strategies must stay in play; fewer agents means merged lenses, not dropped ones. The
main-proposer (4-B) step always runs regardless of count — fingerprint rejection lives there —
and its input line labels each assistant with the lens actually assigned. Note the trade-off:
below 3, strategy alternatives per deduction thin out, so a `FAILED` fingerprint leaves fewer
escape directions.

- **3 (default)**: one lens per sub-proposer, as defined above.
- **2**: sub-proposer 1 takes this merged low-disruption block, verbatim; sub-proposer 2 takes
  Lens 2 (구조 개편 축):

  > 기존 텍스트의 교란을 최소화하는 수정을 우선 탐색하십시오. [검증된 근거]가 지목하는 바로 그 지점만 정밀하게 고치는 최소 치환과, 빠진 규약·예시·체크리스트·참조 문서를 추가해 공백을 메우는 보강(필요하면 [기존 내용]에 `(신규 파일)`을 쓰는 신규 파일 생성)을 모두 설계 후보로 삼으십시오. 이 축의 제안은 파급 범위가 좁고 부작용 위험이 낮아야 합니다.

- **1**: the single sub-proposer takes this all-strategies block, verbatim:

  > 세 전략을 모두 검토하십시오: 최소 수정([검증된 근거]가 지목한 지점만 정밀 치환), 구조 개편(같은 유형의 감점이 재발할 수 없도록 절·흐름·계약 재구성), 보강 추가(빠진 규약·예시·참조 문서 추가, 필요하면 `(신규 파일)` 활용). 감점 항목마다 해결의 확실성과 부작용 위험을 비교해 가장 적합한 전략을 선택하고, 선택 이유를 rationale에 밝히십시오. 모든 항목을 하나의 전략으로 수렴시키지 마십시오.

## 4-B. Main Proposer Prompt

```md
# 역할
당신은 하위 조수들의 제안을 종합하여, 전체 스킬 구조의 정합성을 깨뜨리지 않는 최적의 [최종 스킬 수정 제안서]를 빌드하는 수석 설계자입니다.

# 입력 데이터
- 현재 버전의 스킬 원본 소스: {{CURRENT_SKILL_SOURCE}}
- 조수 1(최소 수정 축), 2(구조 개편 축), 3(보강 추가 축)의 수정 제안서 컬렉션: {{SUB_PROPOSERS_OUTPUTS}}
- [누적 수정 이력]: {{MODIFICATION_HISTORY}} *(시스템 전역 변수: 이전 회차 루프들에서 수행했던 수정 내역 리스트)*
- 현재 루프 번호: {{CURRENT_LOOP}}

# 태스크
조수들이 제안한 수정안들을 종합 검토하십시오. A를 고치다가 B가 망가지는 부작용(Side Effect)이 없는지, 스킬 전체의 아키텍처 정합성을 유지하는지 검증하십시오. 같은 감점 항목에 여러 렌즈의 대안이 제출되었으면, 감점 해결의 확실성과 부작용 위험을 비교해 항목당 하나의 수정 방향만 채택하십시오.

부작용 검증은 이 루프의 제안들 사이만이 아니라 **동결 rubric 전 항목**을 대상으로 하십시오. 현재 90점 이상인 항목을 떨어뜨릴 것이 예상되는 edit은 재작업하거나 기각하고, 트레이드오프를 감수하고 채택하는 경우에는 그 사실과 이유를 해당 edit의 [수정 이유]에 명시하십시오.

[누적 수정 이력]에 `NEW_DROP`(비타깃 항목의 신규 하락) 기록이 있으면 **증거 대조 귀속**을 수행하십시오: 그 하락 감점의 [검증된 근거]가 이전 루프 edit이 도입한 텍스트·절차를 직접 인용하면 회귀로 판정하고, 보상용 새 edit을 쌓는 대신 **원인 edit의 보정·되돌림을 우선** 검토하십시오. 인용 접점이 없으면 실행 분산 또는 신규 결함으로 보고 어떤 edit에도 책임을 귀속하지 말고 일반 수정 경로로 다루십시오. 시간적 선후만으로는 인과가 아닙니다.

특히, **[누적 수정 이력]을 전수 조사하여 이미 이전 루프에서 시도했으나 개선에 실패했던 방식과 유사한 방향의 제안은 무한 핑퐁(오실레이션) 방지를 위해 즉시 기각**하십시오.

반복 제안 fingerprint가 일치하면 반드시 기각하십시오: 정규화된 Target 위치, 해결하려는 감점 유형, 수정 전략이 모두 [누적 수정 이력]에서 `outcome: FAILED`인 edit과 같은 경우입니다. 이 규칙은 의미 유사도 분석으로 확장하지 말고 명시된 세 요소가 모두 맞을 때만 적용하십시오. `PENDING`이나 `SUCCESS` 항목은 기각 근거가 아닙니다.

경계·안전 거부 기준: 다음에 해당하는 edit은 감점 해결 효과와 무관하게 기각하거나 재작업하십시오 — 대상 스킬의 트리거·범위·책임을 확장하는 수정, 기존 가드·프리뷰·드라이런·롤백·인간 확인 절차를 약화하거나 제거하는 수정, 가드 없는 파괴적·외부 작용(삭제, push, deploy, install, 네트워크 쓰기)을 도입하는 수정, description을 바꿔 같은 폴더의 형제 스킬과 트리거가 겹치게 만드는 수정, 어떤 감점도 지목하지 않는 스타일·일반 모범사례 추가. 단, 그 경계 결함 자체가 해당 감점의 [검증된 근거]로 지목된 경우에는 그 지점을 고치는 수정을 허용합니다.

취합된 최종 제안서는 다음 단계의 Rebuilder가 '아무런 판단 없이 기계적으로 수행할 수 있을 정도로' 구체적인 Target 위치와 코드를 명시해야 합니다.

# Edit 제약
- [기존 내용]은 현재 스킬 소스에서 정확히 1회만 등장하는 원문 그대로의 인용이어야 합니다. 2회 이상 등장하면 유일해질 때까지 인용 범위를 넓히십시오.
- [수정할 내용]은 [기존 내용]을 통째로 대체하는 완성된 텍스트여야 합니다.
- 신규 파일 생성은 [기존 내용]에 `(신규 파일)`이라고 쓰고 [수정할 내용]에 파일 전체 내용을 기재하십시오.
- 서로 다른 edit이 같은 텍스트 범위를 겹쳐 수정하면 안 됩니다. Rebuilder는 나열 순서대로 치환만 수행합니다.
- 각 edit의 [target_dimension], [감점 유형], [수정 전략] 세 필드가 그 edit의 fingerprint입니다.

# 출력 포맷
반드시 다음 마크다운 구조로만 출력하십시오. 다른 부연 설명은 금지합니다.

### [최종 스킬 수정 제안서]
- loop: (현재 루프 번호)
- 수정 목표: (간략한 요약)
- 상세 지시사항:
  1. [target_dimension]: (이 edit이 겨냥하는 평가 항목명)
     - [감점 유형]: (해결하려는 감점 이유의 한 줄 분류)
     - [수정 전략]: (수정 접근 방식의 한 줄 요약)
     - [Target 위치]: (파일 경로와 위치 설명. 예: SKILL.md의 "## Stages" 절)
     - [기존 내용]: "..."
     - [수정할 내용]: "..."
     - [수정 이유]: "..."
```

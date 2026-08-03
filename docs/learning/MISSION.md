# Mission: Make Body의 변경 안전성 검증

## Why
Make Body가 만드는 System layer와 테스트가 실제로 LLM의 구현·수정을 더 안전하게 만드는지 판단하고, 가치가 낮은 문서 작업은 줄인다.

## Success looks like
- System 문서와 characterization test의 역할을 구분할 수 있다.
- 변경 전에 어떤 기존 동작을 잠가야 하는지 판단할 수 있다.
- 현재 동작과 의도된 올바른 동작을 혼동하지 않는다.

## Constraints
- 현재 Make Body 설계에 직접 적용할 수 있는 개념만 다룬다.
- 설명은 짧고 구체적인 예제를 사용한다.

## Out of scope
- 전체 테스트 전략이나 특정 테스트 프레임워크 사용법

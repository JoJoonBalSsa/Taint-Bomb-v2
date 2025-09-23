import json
from typing import List, Dict, Any


class PromptBuilder:
    """JSON 분석 결과를 Claude 프롬프트로 변환하는 클래스"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.prompts = config_manager.get_prompts()

    def build_analysis_prompt(self, taint_data: Dict[str, Any]) -> str:
        """단일 taint flow에 대한 분석 프롬프트 생성"""
        template = self.prompts.get('analysis_prompt_template', self._get_default_template())

        # taint_data에서 필요한 정보 추출
        sensitivity = taint_data.get('sensitivity', 'Unknown')
        tainted_items = taint_data.get('tainted', [])

        if not tainted_items:
            return "분석할 데이터가 없습니다."

        # 여러 tainted item이 있는 경우, 첫 번째 것을 사용하거나 모두 포함
        analysis_prompts = []

        for item in tainted_items:
            file_path = item.get('file_path', 'Unknown')
            method_name = item.get('method_name', 'Unknown')
            tree_position = item.get('tree_position', 'Unknown')
            source_code = item.get('source_code', 'Source code not available')
            cut_tree = item.get('cut_tree', '')

            # taint flow 정보 구성
            taint_flow = self._extract_taint_flow_info(method_name, cut_tree)

            # 민감도 레벨 한국어 변환
            sensitivity_kr = self._translate_sensitivity(sensitivity)

            prompt = template.format(
                sensitivity=sensitivity_kr,
                file_path=file_path,
                method_name=method_name,
                tree_position=tree_position,
                source_code=source_code,
                taint_flow=taint_flow
            )

            analysis_prompts.append(prompt)

        return "\n\n---\n\n".join(analysis_prompts)

    def build_batch_analysis_prompt(self, taint_data_list: List[Dict[str, Any]]) -> str:
        """여러 taint flow에 대한 배치 분석 프롬프트 생성"""
        if not taint_data_list:
            return "분석할 데이터가 없습니다."

        system_prompt = self.prompts.get('system_prompt', '')
        batch_intro = """
# 다중 Taint Flow 보안 분석

다음은 코드베이스에서 발견된 여러 taint flow들입니다. 각 흐름을 개별적으로 분석한 후, 전체적인 보안 위험도와 우선순위를 평가해주세요.

"""

        individual_analyses = []
        for i, taint_data in enumerate(taint_data_list, 1):
            analysis = f"## Flow {i}\n\n{self.build_analysis_prompt(taint_data)}"
            individual_analyses.append(analysis)

        batch_summary = """

# 종합 분석 요청

위의 모든 taint flow를 분석한 후, 다음 내용을 제공해주세요:

1. **전체 보안 위험도 요약**
   - 각 flow의 위험도 순위
   - 가장 우선적으로 수정해야 할 취약점

2. **공통 패턴 분석**
   - 발견된 공통적인 보안 이슈
   - 시스템 차원의 보안 개선 방안

3. **수정 우선순위**
   - 즉시 수정이 필요한 항목
   - 중장기적으로 개선할 항목

4. **전체적인 보안 강화 방안**
   - 아키텍처 레벨 개선사항
   - 개발 프로세스 개선사항

모든 분석 결과는 한국어로 작성해주세요.
"""

        return batch_intro + "\n\n".join(individual_analyses) + batch_summary

    def build_summary_prompt(self, analysis_results: List[str]) -> str:
        """Claude 분석 결과들을 요약하는 프롬프트 생성"""
        if not analysis_results:
            return "요약할 분석 결과가 없습니다."

        summary_prompt = f"""
# 보안 분석 결과 요약

다음은 taint analysis를 통해 발견된 보안 이슈들에 대한 상세 분석 결과입니다:

{chr(10).join([f"## 분석 결과 {i+1}{chr(10)}{result}" for i, result in enumerate(analysis_results)])}

## 요약 요청

위의 모든 분석 결과를 종합하여 다음과 같은 경영진 보고서 형태의 요약을 작성해주세요:

### 1. 전체 요약 (Executive Summary)
- 발견된 보안 이슈의 총 개수와 심각도 분포
- 가장 중요한 보안 위험 3가지

### 2. 즉시 조치 사항
- 긴급하게 수정이 필요한 취약점
- 각각의 예상 수정 시간과 우선순위

### 3. 중장기 개선 계획
- 시스템 아키텍처 개선사항
- 개발 프로세스 개선사항
- 보안 교육 및 가이드라인 필요성

### 4. 비용 및 리소스 평가
- 수정 작업에 필요한 대략적인 개발 시간
- 위험을 방치할 경우의 잠재적 비용

결과는 비기술적인 관리자도 이해할 수 있도록 작성해주세요.
"""
        return summary_prompt

    def _extract_taint_flow_info(self, method_name: str, cut_tree: str) -> str:
        """메소드 이름과 cut_tree에서 taint flow 정보 추출"""
        flow_info = []

        # 메소드 이름에서 source function 추출
        if '.' in method_name:
            parts = method_name.split('.')
            if len(parts) >= 3:
                source_function = parts[-1]
                flow_info.append(f"Source: {source_function}")

        # cut_tree에서 추가 정보 추출 (간단한 파싱)
        if cut_tree:
            # Method signature 추출
            if "Method:" in cut_tree:
                method_signature = cut_tree.split("Method:")[-1].split("\n")[0].strip()
                flow_info.append(f"Method: {method_signature}")

        return "\n".join(flow_info) if flow_info else "Taint flow 정보를 추출할 수 없습니다."

    def _translate_sensitivity(self, sensitivity: int) -> str:
        """민감도 숫자를 한국어로 변환"""
        sensitivity_map = {
            3: "높음 (High)",
            2: "중간 (Medium)",
            1: "낮음 (Low)"
        }
        return sensitivity_map.get(sensitivity, f"알 수 없음 ({sensitivity})")

    def _get_default_template(self) -> str:
        """기본 프롬프트 템플릿"""
        return """
다음은 Java 코드에서 발견된 taint flow 분석 결과입니다:

## 분석 대상
- **민감도**: {sensitivity}
- **파일 경로**: {file_path}
- **메소드**: {method_name}
- **위치**: {tree_position}

## 소스 코드
```java
{source_code}
```

## Taint Flow
{taint_flow}

이 taint flow를 분석하여 다음 내용을 제공해주세요:
1. 보안 위험도 평가 (높음/중간/낮음)
2. 잠재적 취약점 유형
3. 공격 시나리오
4. 구체적인 보안 개선 방안
5. 코드 수정 예시 (가능한 경우)

분석 결과를 한국어로 작성해주세요.
"""

    def create_custom_prompt(self, prompt_type: str, data: Dict[str, Any]) -> str:
        """사용자 정의 프롬프트 생성"""
        custom_templates = {
            "vulnerability_scan": """
다음 코드에서 발견된 잠재적 취약점을 스캔해주세요:

파일: {file_path}
민감도: {sensitivity}

```java
{source_code}
```

OWASP Top 10 기준으로 분석하고, CVE 참조가 가능한 경우 포함해주세요.
""",
            "code_review": """
다음 코드에 대한 보안 코드 리뷰를 수행해주세요:

```java
{source_code}
```

리뷰 관점:
1. 입력 검증
2. 출력 인코딩
3. 접근 제어
4. 에러 처리
5. 로깅 및 모니터링

각 관점에서 개선사항을 제시해주세요.
""",
            "penetration_test": """
다음 taint flow를 기반으로 침투 테스트 시나리오를 작성해주세요:

Taint Flow: {taint_flow}
Source Code:
```java
{source_code}
```

다음 내용을 포함해주세요:
1. 공격 벡터
2. Payload 예시
3. 예상되는 영향
4. 테스트 절차
"""
        }

        template = custom_templates.get(prompt_type, self._get_default_template())
        return template.format(**data)
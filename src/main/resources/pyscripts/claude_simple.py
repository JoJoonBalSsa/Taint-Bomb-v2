import json
import os

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    print("anthropic 라이브러리가 없습니다. pip install anthropic")


def send_to_claude(priority_flow):
    """priority_flow를 Claude에게 전달"""

    if not CLAUDE_AVAILABLE:
        print("Claude 사용 불가")
        return None

    # API 키 확인
    

    api_key = os.getenv('CLAUDE_API_KEY')

<<<<<<< HEAD
    
    # 환경변수가 없으면 여기에 직접 입력 (테스트용)
=======
>>>>>>> e1928c6d89364a373e500695fc9b7c830b9b1d27
    if not api_key:
        api_key = "여기에-API-키-입력"  # TODO: 실제 키로 교체

    if not api_key or api_key == "여기에-API-키-입력":
        print("CLAUDE_API_KEY 환경변수를 설정하세요")
        return None

    # Claude에 전송
    try:
        client = anthropic.Anthropic(api_key=api_key)

        # priority_flow를 문자열로 변환
        flow_text = "\n".join([str(flow) for flow in priority_flow])

        # 간단한 프롬프트
        prompt = f"""
당신은 Java 애플리케이션 보안 전문가입니다. 다음 taint flow 분석 결과를 바탕으로 전문적인 보안 분석 보고서를 마크다운 형식으로 작성해주세요.

# 분석 데이터
{flow_text}

각 flow의 형식: [민감도, 메소드1, 메소드2, ...]
- 민감도: 1(낮음), 2(중간), 3(높음)

---

# 보고서 구성 요구사항

## 1. Executive Summary
- 분석 대상 애플리케이션 개요
- 발견된 전체 취약점 수 및 심각도 분포
- 가장 심각한 보안 이슈 3가지
- 전반적인 보안 상태 평가

## 2. 위험도 통계 및 시각화

### 2.1 위험도별 분포

| 위험도 | 건수 | 비율 | 시각화 |
|-------|-----|------|--------|
| 🔴 높음 | X건 | XX% | ████████░░ |
| 🟡 중간 | Y건 | YY% | ██████░░░░ |
| 🟢 낮음 | Z건 | ZZ% | ███░░░░░░░ |
| **합계** | **N건** | **100%** | |

### 2.2 취약점 유형별 분포

| 취약점 유형 | 발견 건수 | 심각도 평균 | 우선순위 |
|-----------|---------|-----------|---------|
| SQL Injection | X건 | 높음 | 🚨 긴급 |
| XSS (Cross-Site Scripting) | Y건 | 중간 | ⚠️ 높음 |
| Command Injection | Z건 | 높음 | 🚨 긴급 |
| Path Traversal | W건 | 중간 | ⚡ 중간 |

### 2.3 주요 데이터 흐름 다이어그램

**가장 위험한 Taint Flow #1**
```
[Source] 사용자 입력 (HTTP Request)
    ↓
[메소드1] request.getParameter("id")
    ↓ (검증 없음)
[메소드2] buildSQLQuery(userInput)
    ↓ (문자열 연결)
[Sink] executeQuery(query) ⚠️ 위험!
```

**가장 위험한 Taint Flow #2**
```
[Source] 파일 업로드
    ↓
[메소드1] getUploadedFile()
    ↓ (검증 부족)
[메소드2] processFilePath(filename)
    ↓ (경로 조작 가능)
[Sink] FileWriter(path) ⚠️ 위험!
```

## 3. 취약점 상세 분석

각 taint flow에 대해 다음 형식으로 분석:

---
### 취약점 #[번호]: [취약점 유형명]

**위험도**: 🔴 높음 / 🟡 중간 / 🟢 낮음

**CWE 분류**: [해당 CWE 번호 및 설명]

**OWASP Top 10 매핑**: [해당 항목]

#### 데이터 흐름 분석
```
Source (출발점)
    ↓
[메소드1] - 역할 설명
    ↓
[메소드2] - 데이터 변환/처리 과정
    ↓
Sink (도착점) - 위험한 작업
```

#### 취약점 상세 설명
- **문제점**: 왜 이것이 보안 취약점인가?
- **발생 원인**: 소스코드 레벨에서의 문제
- **데이터 오염 경로**: Source → Sink까지 상세 추적

#### 공격 시나리오
실제 공격자가 악용할 수 있는 구체적인 시나리오 작성

#### 영향도 평가
- **기밀성 (Confidentiality)**: [상/중/하] - 설명
- **무결성 (Integrity)**: [상/중/하] - 설명
- **가용성 (Availability)**: [상/중/하] - 설명
- **CVSS 예상 점수**: [점수 추정]

#### 보안 대응방안

**1️. 즉시 조치 (긴급)**
- 임시 완화 조치

**2️. 근본 해결방법**

**Before (취약한 코드)**
```java
// 문제가 있는 코드 예시
```

**After (보안 강화 코드)**
```java
// 수정된 안전한 코드 예시
// 핵심 보안 기법 설명
```

**3️. 추가 보안 레이어**
- 입력 검증 (Validation)
- 출력 인코딩 (Encoding)
- 파라미터화된 쿼리 사용
- 보안 라이브러리 활용
- 최소 권한 원칙 적용

**4️. 테스트 방법**
보안 패치 후 검증 방법 제시

---

## 보고서 작성 시 주의사항
1. 모든 취약점을 빠짐없이 분석
2. 기술적으로 정확하고 구체적인 설명
3. 실행 가능한 해결방안 제시
4. 한국어로 전문적이고 명확하게 작성
5. 마크다운 문법 준수
6. Mermaid 다이어그램 정확한 문법 사용
"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
<<<<<<< HEAD
            max_tokens=16000,
=======
            max_tokens=1024,
>>>>>>> e1928c6d89364a373e500695fc9b7c830b9b1d27
            messages=[{"role": "user", "content": prompt}]
        )

        # 응답이 잘렸는지 확인
        if response.stop_reason == "max_tokens":
            print("경고: 응답이 max_tokens 제한으로 잘렸습니다. max_tokens를 늘려주세요.")
        else:
            print("claude 보고서 생성 완료")

        result = response.content[0].text
        print("Claude 분석 완료")
        return result

    except Exception as e:
        print(f"Claude API 호출 실패: {e}")
        return None
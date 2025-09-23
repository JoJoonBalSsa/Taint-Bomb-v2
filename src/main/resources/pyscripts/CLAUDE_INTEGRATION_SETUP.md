# Claude 통합 설정 가이드

## 1. 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install anthropic python-dotenv
```

## 2. Claude API 키 설정

### 방법 1: 환경변수 설정 (권장)
```bash
# Windows
set CLAUDE_API_KEY=your_api_key_here

# Linux/Mac
export CLAUDE_API_KEY=your_api_key_here
```

### 방법 2: 설정 파일 수정
`config/claude_config.json` 파일의 `api_key` 필드에 직접 입력:
```json
{
    "claude_api": {
        "api_key": "your_api_key_here",
        ...
    }
}
```

## 3. 기본 사용법

### 기존 Taint Analysis + Claude 분석
```bash
python main.py /path/to/output/folder
```

분석이 완료되면 다음 파일들이 생성됩니다:
- `analysis_result.json` - 기존 taint analysis 결과
- `claude_analysis_results.json` - Claude 상세 분석 결과
- `claude_security_analysis.md` - Claude 분석 마크다운 보고서
- `processed_analysis_results.json` - 처리된 분석 결과
- `executive_summary.md` - 경영진 요약 보고서
- `claude_executive_summary.md` - Claude 전체 요약

## 4. 설정 옵션

### 분석 설정
```json
{
    "analysis": {
        "enabled": true,           // Claude 분석 활성화 여부
        "batch_size": 5,          // 한 번에 분석할 flow 수
        "timeout": 60,            // API 타임아웃 (초)
        "retry_attempts": 3,      // 재시도 횟수
        "analysis_language": "korean"  // 분석 결과 언어
    }
}
```

### Claude API 설정
```json
{
    "claude_api": {
        "model": "claude-3-5-sonnet-20241022",  // 사용할 모델
        "max_tokens": 4000,                     // 최대 토큰 수
        "temperature": 0.1                      // 창의성 수준 (0.0-1.0)
    }
}
```

### 출력 설정
```json
{
    "output": {
        "save_claude_response": true,     // Claude 응답 저장
        "separate_claude_file": true,     // 별도 파일로 저장
        "claude_output_format": "markdown"  // 출력 형식
    }
}
```

## 5. 출력 파일 설명

### `claude_analysis_results.json`
각 taint flow에 대한 Claude의 상세 분석 결과
```json
[
    {
        "original_data": { ... },          // 원본 taint 데이터
        "claude_analysis": "분석 결과 텍스트",
        "analysis_timestamp": "2023-...",
        "sensitivity": 3
    }
]
```

### `processed_analysis_results.json`
구조화된 분석 결과 및 통계
```json
{
    "summary": { ... },              // 요약 통계
    "risk_assessment": [ ... ],      // 위험도 평가
    "prioritized_issues": [ ... ],   // 우선순위별 이슈
    "recommendations": { ... },      // 개선사항
    "charts_data": { ... }          // 차트용 데이터
}
```

## 6. 고급 사용법

### 사용자 정의 프롬프트
`config/claude_config.json`의 `prompts` 섹션에서 프롬프트 커스터마이징 가능

### 배치 크기 조정
대량의 taint flow가 있는 경우 `batch_size`를 조정하여 성능 최적화

### 재시도 설정
네트워크 문제나 일시적 API 오류를 대비한 `retry_attempts` 설정

## 7. 문제 해결

### API 키 오류
```
Claude API 키가 설정되지 않았습니다.
```
→ 환경변수 `CLAUDE_API_KEY` 설정 또는 config 파일 수정

### 모듈 import 오류
```
Claude integration 모듈을 불러올 수 없습니다
```
→ `pip install anthropic python-dotenv` 실행

### API 호출 실패
```
Claude API 호출 오류
```
→ 인터넷 연결, API 키 유효성, 요청 한도 확인

## 8. 성능 최적화

- **배치 크기**: 너무 크면 메모리 사용량 증가, 너무 작으면 API 호출 횟수 증가
- **타임아웃**: 복잡한 분석의 경우 타임아웃 시간 증가
- **재시도**: 네트워크가 불안정한 환경에서는 재시도 횟수 증가

## 9. 비용 관리

- Claude API는 토큰 기반 과금
- `max_tokens` 설정으로 토큰 사용량 제한
- `batch_size`로 API 호출 횟수 조절
- 필요시 `enabled: false`로 Claude 분석 비활성화
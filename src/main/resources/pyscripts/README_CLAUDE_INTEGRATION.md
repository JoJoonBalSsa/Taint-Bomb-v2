# Taint Bomb v2 - Claude Integration

## 🚀 새로운 기능: Claude LLM 통합

Taint Bomb v2에 Claude AI가 통합되어 기존 taint analysis 결과를 LLM이 분석하여 더욱 상세하고 실용적인 보안 보고서를 생성합니다.

## ✨ 주요 특징

- **자동 분석**: JSON 결과를 Claude가 자동으로 분석
- **상세 보고서**: 취약점별 공격 시나리오 및 대응방안 제시
- **우선순위 제공**: 위험도에 따른 수정 우선순위 자동 계산
- **경영진 보고서**: 비기술자도 이해할 수 있는 요약 보고서
- **한국어 지원**: 모든 분석 결과를 한국어로 제공

## 🔧 빠른 시작

### 1. 설치
```bash
cd src/main/resources/pyscripts
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
# 환경변수로 설정 (권장)
set CLAUDE_API_KEY=your_api_key_here
```

### 3. 실행
```bash
# 기존과 동일하게 실행하면 Claude 분석이 자동으로 추가됩니다
python main.py /path/to/java/source
```

## 📊 생성되는 보고서

### 기존 보고서 (유지)
- `analysis_result.json` - taint analysis 결과
- `analysis_result.md` - 기본 마크다운 보고서

### 새로운 보고서 (추가)
- `claude_security_analysis.md` - 📋 상세 보안 분석
- `executive_summary.md` - 👔 경영진 요약
- `processed_analysis_results.json` - 📈 구조화된 데이터

## 🎯 Claude 분석 내용

각 취약점에 대해 다음을 제공합니다:

1. **보안 위험도 평가** (높음/중간/낮음)
2. **취약점 유형 분류** (SQL Injection, XSS 등)
3. **공격 시나리오** 상세 설명
4. **구체적인 개선방안**
5. **코드 수정 예시**

## ⚙️ 설정 커스터마이징

`config/claude_config.json`에서 다음을 조정할 수 있습니다:

```json
{
  "claude_api": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4000
  },
  "analysis": {
    "batch_size": 5,
    "analysis_language": "korean"
  }
}
```

## 🔍 테스트

```bash
# 통합 테스트 실행
python test_claude_integration.py
```

## 💡 사용 팁

- **비용 절약**: `config/claude_config.json`에서 `enabled: false`로 설정하면 Claude 분석 비활성화
- **성능 최적화**: `batch_size`를 조정하여 API 호출 최적화
- **언어 변경**: `analysis_language`를 "english"로 변경하면 영어 분석

## 🚨 주의사항

- Claude API 키가 필요합니다 (anthropic.com에서 발급)
- 인터넷 연결이 필요합니다
- API 사용량에 따라 비용이 발생할 수 있습니다

## 📞 지원

문제가 있거나 개선사항이 있으시면 개발팀에 문의해주세요.

---

**Powered by Claude 3.5 Sonnet** 🤖
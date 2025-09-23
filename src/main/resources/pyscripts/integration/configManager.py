import json
import os
from pathlib import Path


class ConfigManager:
    """Claude API 설정 관리 클래스"""

    def __init__(self, config_path=None):
        if config_path is None:
            # 현재 스크립트 디렉토리 기준으로 config 경로 설정
            current_dir = Path(__file__).parent.parent
            self.config_path = current_dir / "config" / "claude_config.json"
        else:
            self.config_path = Path(config_path)

        self.config = self._load_config()

    def _load_config(self):
        """설정 파일 로드"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"설정 파일 로드 오류: {e}")
                return self._get_default_config()
        else:
            # 설정 파일이 없으면 기본 설정 생성
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config

    def _get_default_config(self):
        """기본 설정 반환"""
        return {
            "claude_api": {
                "api_key": "",  # 사용자가 직접 설정해야 함
                "base_url": "https://api.anthropic.com",
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "temperature": 0.1
            },
            "analysis": {
                "enabled": True,
                "batch_size": 5,  # 한 번에 분석할 taint flow 수
                "timeout": 60,    # API 타임아웃 (초)
                "retry_attempts": 3,
                "analysis_language": "korean"  # 분석 결과 언어
            },
            "output": {
                "save_claude_response": True,
                "include_in_markdown": True,
                "separate_claude_file": True,
                "claude_output_format": "markdown"
            },
            "prompts": {
                "system_prompt": "You are a cybersecurity expert specializing in taint analysis and code vulnerability assessment.",
                "analysis_prompt_template": """
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
            }
        }

    def _save_config(self, config):
        """설정 파일 저장"""
        try:
            # 디렉토리가 없으면 생성
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"설정 파일 저장 오류: {e}")

    def get_api_key(self):
        """API 키 반환 (환경변수 우선)"""
        # 환경변수에서 먼저 확인
        env_key = os.getenv('CLAUDE_API_KEY')
        if env_key:
            return env_key

        # 설정 파일에서 확인
        return self.config.get('claude_api', {}).get('api_key', '')

    def get_claude_config(self):
        """Claude API 설정 반환"""
        return self.config.get('claude_api', {})

    def get_analysis_config(self):
        """분석 설정 반환"""
        return self.config.get('analysis', {})

    def get_output_config(self):
        """출력 설정 반환"""
        return self.config.get('output', {})

    def get_prompts(self):
        """프롬프트 설정 반환"""
        return self.config.get('prompts', {})

    def is_claude_enabled(self):
        """Claude 분석 활성화 여부 확인"""
        api_key = self.get_api_key()
        analysis_enabled = self.config.get('analysis', {}).get('enabled', False)
        return bool(api_key) and analysis_enabled

    def update_config(self, section, key, value):
        """설정 업데이트"""
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value
        self._save_config(self.config)

    def validate_config(self):
        """설정 유효성 검사"""
        issues = []

        # API 키 확인
        if not self.get_api_key():
            issues.append("Claude API 키가 설정되지 않았습니다. 환경변수 CLAUDE_API_KEY를 설정하거나 config 파일을 수정하세요.")

        # 필수 설정 확인
        claude_config = self.get_claude_config()
        if not claude_config.get('model'):
            issues.append("Claude 모델이 설정되지 않았습니다.")

        if not claude_config.get('base_url'):
            issues.append("Claude API base URL이 설정되지 않았습니다.")

        return issues
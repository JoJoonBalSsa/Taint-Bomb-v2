import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

try:
    import anthropic
except ImportError:
    anthropic = None
    print("Warning: anthropic 라이브러리가 설치되지 않았습니다. 'pip install anthropic'로 설치하세요.")

from configManager import ConfigManager
from promptBuilder import PromptBuilder


class ClaudeIntegrator:
    """Claude API와의 통합을 담당하는 메인 클래스"""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager()
        self.prompt_builder = PromptBuilder(self.config)
        self.client = None
        self.logger = self._setup_logger()

        # Claude 클라이언트 초기화
        if self._initialize_client():
            self.logger.info("Claude API 클라이언트가 성공적으로 초기화되었습니다.")
        else:
            self.logger.warning("Claude API 클라이언트 초기화에 실패했습니다.")

    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_client(self) -> bool:
        """Claude API 클라이언트 초기화"""
        if anthropic is None:
            self.logger.error("anthropic 라이브러리가 설치되지 않았습니다.")
            return False

        api_key = self.config.get_api_key()
        if not api_key:
            self.logger.error("Claude API 키가 설정되지 않았습니다.")
            return False

        try:
            claude_config = self.config.get_claude_config()
            self.client = anthropic.Anthropic(
                api_key=api_key,
                base_url=claude_config.get('base_url', 'https://api.anthropic.com')
            )
            return True
        except Exception as e:
            self.logger.error(f"Claude 클라이언트 초기화 오류: {e}")
            return False

    def analyze_taint_flows(self, json_file_path: str, output_folder: str) -> bool:
        """JSON 파일의 taint flow들을 분석"""
        if not self.client:
            self.logger.error("Claude API 클라이언트가 초기화되지 않았습니다.")
            return False

        try:
            # JSON 파일 로드
            taint_data = self._load_json_file(json_file_path)
            if not taint_data:
                self.logger.warning("분석할 taint flow 데이터가 없습니다.")
                return False

            self.logger.info(f"총 {len(taint_data)}개의 taint flow를 분석합니다.")

            # 분석 실행
            analysis_results = self._perform_analysis(taint_data)

            # 결과 저장
            self._save_analysis_results(analysis_results, output_folder)

            self.logger.info("Claude 분석이 완료되었습니다.")
            return True

        except Exception as e:
            self.logger.error(f"Taint flow 분석 중 오류 발생: {e}")
            return False

    def _load_json_file(self, json_file_path: str) -> List[Dict[str, Any]]:
        """JSON 파일 로드"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 데이터가 리스트가 아닌 경우 리스트로 변환
            if isinstance(data, dict):
                data = [data]

            return data if isinstance(data, list) else []

        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            self.logger.error(f"JSON 파일 로드 오류: {e}")
            return []

    def _perform_analysis(self, taint_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """실제 분석 수행"""
        analysis_config = self.config.get_analysis_config()
        batch_size = analysis_config.get('batch_size', 5)
        results = []

        # 민감도별로 정렬 (높은 민감도 우선)
        sorted_data = sorted(taint_data, key=lambda x: x.get('sensitivity', 0), reverse=True)

        # 배치 단위로 처리
        for i in range(0, len(sorted_data), batch_size):
            batch = sorted_data[i:i + batch_size]
            batch_results = self._analyze_batch(batch, i // batch_size + 1)
            results.extend(batch_results)

            # API 호출 간격 조절
            if i + batch_size < len(sorted_data):
                time.sleep(1)

        return results

    def _analyze_batch(self, batch: List[Dict[str, Any]], batch_number: int) -> List[Dict[str, Any]]:
        """배치 단위 분석"""
        self.logger.info(f"배치 {batch_number} 분석 중... ({len(batch)}개 flow)")

        batch_results = []
        analysis_config = self.config.get_analysis_config()

        for item in batch:
            try:
                # 개별 분석 수행
                result = self._analyze_single_flow(item)
                if result:
                    batch_results.append(result)

                # API 호출 간격
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"개별 flow 분석 오류: {e}")
                # 오류가 발생해도 계속 진행
                continue

        return batch_results

    def _analyze_single_flow(self, taint_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """단일 taint flow 분석"""
        try:
            # 프롬프트 생성
            prompt = self.prompt_builder.build_analysis_prompt(taint_item)

            # Claude API 호출
            response = self._call_claude_api(prompt)
            if not response:
                return None

            # 결과 구성
            return {
                'original_data': taint_item,
                'claude_analysis': response,
                'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'sensitivity': taint_item.get('sensitivity', 0)
            }

        except Exception as e:
            self.logger.error(f"단일 flow 분석 오류: {e}")
            return None

    def _call_claude_api(self, prompt: str) -> Optional[str]:
        """Claude API 호출"""
        if not self.client:
            return None

        try:
            claude_config = self.config.get_claude_config()
            prompts_config = self.config.get_prompts()
            analysis_config = self.config.get_analysis_config()

            # API 호출 파라미터 설정
            api_params = {
                'model': claude_config.get('model', 'claude-3-5-sonnet-20241022'),
                'max_tokens': claude_config.get('max_tokens', 4000),
                'temperature': claude_config.get('temperature', 0.1),
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }

            # 시스템 프롬프트가 있는 경우 추가
            system_prompt = prompts_config.get('system_prompt')
            if system_prompt:
                api_params['system'] = system_prompt

            # 재시도 로직
            retry_attempts = analysis_config.get('retry_attempts', 3)
            timeout = analysis_config.get('timeout', 60)

            for attempt in range(retry_attempts):
                try:
                    response = self.client.messages.create(**api_params)

                    if response.content and len(response.content) > 0:
                        return response.content[0].text
                    else:
                        self.logger.warning("Claude로부터 빈 응답을 받았습니다.")
                        return None

                except Exception as e:
                    self.logger.warning(f"API 호출 시도 {attempt + 1}/{retry_attempts} 실패: {e}")
                    if attempt < retry_attempts - 1:
                        time.sleep(2 ** attempt)  # 지수 백오프
                    else:
                        raise

        except Exception as e:
            self.logger.error(f"Claude API 호출 오류: {e}")
            return None

    def _save_analysis_results(self, results: List[Dict[str, Any]], output_folder: str):
        """분석 결과 저장"""
        if not results:
            self.logger.warning("저장할 분석 결과가 없습니다.")
            return

        output_config = self.config.get_output_config()
        output_path = Path(output_folder)

        try:
            # 전체 결과를 JSON으로 저장
            if output_config.get('save_claude_response', True):
                json_output_path = output_path / 'claude_analysis_results.json'
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Claude 분석 결과가 저장되었습니다: {json_output_path}")

            # 마크다운 형태로 저장
            if output_config.get('separate_claude_file', True):
                md_output_path = output_path / 'claude_security_analysis.md'
                self._save_markdown_report(results, md_output_path)
                self.logger.info(f"Claude 분석 마크다운 보고서가 저장되었습니다: {md_output_path}")

        except Exception as e:
            self.logger.error(f"분석 결과 저장 오류: {e}")

    def _save_markdown_report(self, results: List[Dict[str, Any]], output_path: Path):
        """마크다운 보고서 생성"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Claude 보안 분석 보고서\n\n")
            f.write(f"**생성 시간**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**분석된 Flow 수**: {len(results)}\n\n")

            f.write("## 목차\n")
            for i, result in enumerate(results, 1):
                sensitivity = result.get('sensitivity', 0)
                sensitivity_text = {3: '높음', 2: '중간', 1: '낮음'}.get(sensitivity, '알수없음')
                f.write(f"- [Flow {i} (민감도: {sensitivity_text})](#flow-{i})\n")

            f.write("\n---\n\n")

            for i, result in enumerate(results, 1):
                original_data = result.get('original_data', {})
                analysis = result.get('claude_analysis', '')
                timestamp = result.get('analysis_timestamp', '')

                f.write(f"## Flow {i}\n\n")
                f.write(f"**분석 시간**: {timestamp}\n")
                f.write(f"**민감도**: {original_data.get('sensitivity', 'Unknown')}\n\n")

                # 원본 데이터 요약
                tainted_items = original_data.get('tainted', [])
                if tainted_items:
                    item = tainted_items[0]  # 첫 번째 항목만 표시
                    f.write(f"**파일**: {item.get('file_path', 'Unknown')}\n")
                    f.write(f"**메소드**: {item.get('method_name', 'Unknown')}\n")
                    f.write(f"**위치**: {item.get('tree_position', 'Unknown')}\n\n")

                f.write("### Claude 분석 결과\n\n")
                f.write(analysis)
                f.write("\n\n---\n\n")

    def get_analysis_summary(self, results_file: str) -> Optional[str]:
        """분석 결과 요약 생성"""
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)

            if not results:
                return None

            # 모든 분석 결과를 수집
            analysis_texts = [result.get('claude_analysis', '') for result in results]
            summary_prompt = self.prompt_builder.build_summary_prompt(analysis_texts)

            # Claude로 요약 생성
            summary = self._call_claude_api(summary_prompt)
            return summary

        except Exception as e:
            self.logger.error(f"분석 요약 생성 오류: {e}")
            return None
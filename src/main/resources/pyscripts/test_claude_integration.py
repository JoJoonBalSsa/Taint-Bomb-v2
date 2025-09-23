#!/usr/bin/env python3
"""
Claude 통합 테스트 스크립트
"""

import sys
import os
import json
from pathlib import Path

# integration 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'integration'))

def test_config_manager():
    """ConfigManager 테스트"""
    print("=== ConfigManager 테스트 ===")

    try:
        from configManager import ConfigManager

        config = ConfigManager()
        print("OK ConfigManager 초기화 성공")

        # 설정 검증
        issues = config.validate_config()
        if issues:
            print("WARN 설정 이슈 발견:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("OK 설정 검증 통과")

        # Claude 활성화 상태 확인
        is_enabled = config.is_claude_enabled()
        print(f"Claude 활성화 상태: {is_enabled}")

        return True

    except Exception as e:
        print(f"FAIL ConfigManager 테스트 실패: {e}")
        return False


def test_prompt_builder():
    """PromptBuilder 테스트"""
    print("\n=== PromptBuilder 테스트 ===")

    try:
        from configManager import ConfigManager
        from promptBuilder import PromptBuilder

        config = ConfigManager()
        prompt_builder = PromptBuilder(config)
        print("OK PromptBuilder 초기화 성공")

        # 테스트 데이터
        test_taint_data = {
            "sensitivity": 3,
            "tainted": [
                {
                    "file_path": "/test/TestClass.java",
                    "method_name": "TestClass.testMethod.nextLine",
                    "tree_position": "10-20",
                    "source_code": "String input = scanner.nextLine();\nSystem.out.println(input);",
                    "cut_tree": "Method: testMethod(Scanner scanner)"
                }
            ]
        }

        # 프롬프트 생성 테스트
        prompt = prompt_builder.build_analysis_prompt(test_taint_data)

        if prompt and len(prompt) > 100:  # 의미있는 길이인지 확인
            print("OK 분석 프롬프트 생성 성공")
            print(f"  프롬프트 길이: {len(prompt)} 문자")
        else:
            print("FAIL 분석 프롬프트 생성 실패 또는 너무 짧음")
            return False

        return True

    except Exception as e:
        print(f"FAIL PromptBuilder 테스트 실패: {e}")
        return False


def test_response_processor():
    """ResponseProcessor 테스트"""
    print("\n=== ResponseProcessor 테스트 ===")

    try:
        from configManager import ConfigManager
        from responseProcessor import ResponseProcessor

        config = ConfigManager()
        processor = ResponseProcessor(config)
        print("OK ResponseProcessor 초기화 성공")

        # 위험도 추출 테스트
        test_analysis = "이 코드는 높은 위험도를 가지고 있습니다. SQL Injection 취약점이 발견되었습니다."
        risk_level = processor._extract_risk_level(test_analysis)

        if risk_level == "높음":
            print("OK 위험도 추출 성공")
        else:
            print(f"WARN 위험도 추출 결과 확인 필요: {risk_level}")

        # 취약점 유형 추출 테스트
        vuln_types = processor._extract_vulnerability_types(test_analysis)
        if "SQL Injection" in vuln_types:
            print("OK 취약점 유형 추출 성공")
        else:
            print(f"WARN 취약점 유형 추출 결과 확인 필요: {vuln_types}")

        return True

    except Exception as e:
        print(f"FAIL ResponseProcessor 테스트 실패: {e}")
        return False


def test_claude_integrator():
    """ClaudeIntegrator 테스트 (API 호출 제외)"""
    print("\n=== ClaudeIntegrator 테스트 ===")

    try:
        from configManager import ConfigManager
        from claudeIntegrator import ClaudeIntegrator

        config = ConfigManager()

        # anthropic 라이브러리 확인
        try:
            import anthropic
            print("OK anthropic 라이브러리 설치됨")
        except ImportError:
            print("WARN anthropic 라이브러리가 설치되지 않음 (pip install anthropic)")
            return False

        # ClaudeIntegrator 초기화 (API 키 없이도 초기화는 가능)
        integrator = ClaudeIntegrator(config)
        print("OK ClaudeIntegrator 초기화 성공")

        # JSON 파일 로드 테스트 (존재하지 않는 파일)
        test_data = integrator._load_json_file("nonexistent.json")
        if test_data == []:
            print("OK 존재하지 않는 파일 처리 성공")

        return True

    except Exception as e:
        print(f"FAIL ClaudeIntegrator 테스트 실패: {e}")
        return False


def create_test_json():
    """테스트용 JSON 파일 생성"""
    print("\n=== 테스트 JSON 파일 생성 ===")

    test_data = [
        {
            "sensitivity": 3,
            "tainted": [
                {
                    "file_path": "/test/Example.java",
                    "method_name": "Example.vulnerableMethod.nextLine",
                    "tree_position": "15-25",
                    "cut_tree": "Method: vulnerableMethod(Scanner input)",
                    "source_code": "public void vulnerableMethod(Scanner input) {\n    String userInput = input.nextLine();\n    System.out.println(\"User said: \" + userInput);\n}"
                }
            ]
        },
        {
            "sensitivity": 2,
            "tainted": [
                {
                    "file_path": "/test/Database.java",
                    "method_name": "Database.query.getParameter",
                    "tree_position": "30-40",
                    "cut_tree": "Method: query(HttpServletRequest request)",
                    "source_code": "public void query(HttpServletRequest request) {\n    String sql = \"SELECT * FROM users WHERE id = \" + request.getParameter(\"id\");\n    // Execute query\n}"
                }
            ]
        }
    ]

    test_file = "test_taint_results.json"
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)

        print(f"OK 테스트 JSON 파일 생성: {test_file}")
        return test_file

    except Exception as e:
        print(f"FAIL 테스트 JSON 파일 생성 실패: {e}")
        return None


def test_full_pipeline():
    """전체 파이프라인 테스트 (API 호출 제외)"""
    print("\n=== 전체 파이프라인 테스트 ===")

    # 테스트 JSON 생성
    test_file = create_test_json()
    if not test_file:
        return False

    try:
        from configManager import ConfigManager
        from promptBuilder import PromptBuilder

        config = ConfigManager()
        prompt_builder = PromptBuilder(config)

        # JSON 파일 로드
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)

        print(f"OK 테스트 데이터 로드 성공: {len(test_data)}개 항목")

        # 각 항목에 대해 프롬프트 생성
        for i, item in enumerate(test_data):
            prompt = prompt_builder.build_analysis_prompt(item)
            if prompt:
                print(f"OK 항목 {i+1} 프롬프트 생성 성공 ({len(prompt)} 문자)")
            else:
                print(f"FAIL 항목 {i+1} 프롬프트 생성 실패")
                return False

        # 배치 프롬프트 테스트
        batch_prompt = prompt_builder.build_batch_analysis_prompt(test_data)
        if batch_prompt:
            print(f"OK 배치 프롬프트 생성 성공 ({len(batch_prompt)} 문자)")

        # 정리
        os.remove(test_file)
        print("OK 테스트 파일 정리 완료")

        return True

    except Exception as e:
        print(f"FAIL 전체 파이프라인 테스트 실패: {e}")
        # 정리
        if os.path.exists(test_file):
            os.remove(test_file)
        return False


def main():
    """메인 테스트 함수"""
    print("Claude 통합 테스트 시작\n")

    tests = [
        test_config_manager,
        test_prompt_builder,
        test_response_processor,
        test_claude_integrator,
        test_full_pipeline
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n=== 테스트 결과 ===")
    print(f"통과: {passed}/{total}")

    if passed == total:
        print("SUCCESS 모든 테스트 통과!")
        print("\n다음 단계:")
        print("1. Claude API 키 설정 (환경변수 CLAUDE_API_KEY 또는 config 파일)")
        print("2. pip install anthropic")
        print("3. 실제 taint analysis 실행하여 Claude 분석 테스트")
    else:
        print("WARN 일부 테스트 실패. 위의 오류 메시지를 확인하세요.")

    return passed == total


if __name__ == "__main__":
    main()
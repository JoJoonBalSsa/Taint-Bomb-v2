from taintAnalyzer import TaintAnalysis
from resultManager import AnalysisResultManager
from reportGenerator import MakeMD
from datetime import datetime
import sys
import os

# Claude integration imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'integration'))
try:
    from configManager import ConfigManager
    from claudeIntegrator import ClaudeIntegrator
    from responseProcessor import ResponseProcessor
    CLAUDE_AVAILABLE = True
except ImportError as e:
    print(f"Claude integration 모듈을 불러올 수 없습니다: {e}")
    CLAUDE_AVAILABLE = False

def create_result(output_folder, flows):
    path = output_folder + "/result.txt"
    with open(path, 'w', encoding='utf-8') as file:  # 결과 파일 생성
        for (class_method, var), value in flows.items():
            file.write("Tainted Variable:\n")
            file.write(f"{var}\n")
            file.write("흐름 파악\n")
            for f in value:
                if isinstance(f[0], list):
                    for sub_f in f:
                        file.write(f"{sub_f}\n")
                else:
                    file.write(f"{f}\n")
            file.write("\n")


def print_result(flows):
    print("\nTainted flows:")
    for f in flows:
        print(f)
    print()


def __analyze_method(output_folder, tainted):
    json_file_path = output_folder + "/analysis_result.json"
    result = AnalysisResultManager(json_file_path)

    flows = tainted._priority_flow()

    for flow in flows:
        sensitivity = flow[0]  # 민감도 값

        for count in range(1, len(flow)):
            method_full_path = flow[count]
            big_parts = method_full_path.split(',')
            if len(big_parts) == 1:
                big_parts.append("")
            parts = big_parts[0].split('.')
            little_method_name = parts[1]

            cut_tree = tainted._get_cut_tree(little_method_name)
            current_path = tainted._file_path
            tree_position = tainted._get_position
            source_code = tainted._extract_method_source_code()
            method_name = method_full_path

            result.append(sensitivity, current_path, method_name, tree_position, cut_tree, source_code)

    result.save_to_json()  # 결과를 JSON 파일로 저장
    return json_file_path  # JSON 파일 경로 반환


def __run_claude_analysis(json_file_path, output_folder):
    """Claude 분석 실행"""
    if not CLAUDE_AVAILABLE:
        print("Claude 분석을 사용할 수 없습니다. 필요한 모듈이 설치되지 않았습니다.")
        return

    try:
        print("Claude 보안 분석을 시작합니다...")

        # 설정 매니저 초기화
        config_manager = ConfigManager()

        # 설정 유효성 검사
        config_issues = config_manager.validate_config()
        if config_issues:
            print("Claude 설정에 문제가 있습니다:")
            for issue in config_issues:
                print(f"  - {issue}")

            # Claude 분석이 비활성화되어 있거나 API 키가 없는 경우
            if not config_manager.is_claude_enabled():
                print("Claude 분석이 비활성화되어 있습니다. 기본 분석만 수행됩니다.")
                return

        # Claude 통합기 초기화
        claude_integrator = ClaudeIntegrator(config_manager)

        # 분석 실행
        success = claude_integrator.analyze_taint_flows(json_file_path, output_folder)

        if success:
            print("Claude 분석이 성공적으로 완료되었습니다.")

            # 응답 처리
            response_processor = ResponseProcessor(config_manager)
            claude_results_file = os.path.join(output_folder, 'claude_analysis_results.json')

            if os.path.exists(claude_results_file):
                print("Claude 분석 결과를 처리합니다...")
                processed_results = response_processor.process_analysis_results(
                    claude_results_file, output_folder
                )

                if 'error' not in processed_results:
                    print("Claude 분석 결과 처리가 완료되었습니다.")

                    # 요약 보고서 생성
                    summary = claude_integrator.get_analysis_summary(claude_results_file)
                    if summary:
                        summary_file = os.path.join(output_folder, 'claude_executive_summary.md')
                        with open(summary_file, 'w', encoding='utf-8') as f:
                            f.write("# Claude 보안 분석 요약\n\n")
                            f.write(summary)
                        print(f"경영진 요약 보고서가 생성되었습니다: {summary_file}")
                else:
                    print(f"결과 처리 중 오류: {processed_results['error']}")
            else:
                print("Claude 분석 결과 파일을 찾을 수 없습니다.")
        else:
            print("Claude 분석 중 오류가 발생했습니다.")

    except Exception as e:
        print(f"Claude 분석 실행 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()


def main(output_folder) :
    tainted = TaintAnalysis(output_folder)
    priority_flow = tainted._priority_flow()

    if not priority_flow:  # priority_flow가 비어있는 경우
        print("발견된 taint가 없습니다.")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 현재 시각을 'YYYY-MM-DD HH:MM:SS' 형식으로 저장

        with open(output_folder + "/analysis_result.md", "w") as md_file:
            md_file.write("# Taint Analysis Result\n")
            md_file.write("## Summary\n")
            md_file.write("No taint flows were detected during the analysis.\n\n")
            md_file.write("## Details\n")
            md_file.write("- **Analysis Time**: {}\n".format(current_time))  # 실제 시간 출력
            md_file.write("- **Output Folder**: {}\n\n".format(output_folder))
            md_file.write("The taint analysis did not identify any potential issues or vulnerabilities in the given codebase.\n")
            md_file.write("If you believe there should be taint flows detected, please review the input code or adjust the analysis parameters.\n")
            md_file.write("\n---\n")
    else:
        print_result(priority_flow)
        create_result(output_folder, tainted.flows)
        json_file_path = __analyze_method(output_folder, tainted)

        make_md = MakeMD(output_folder + "/result.txt", output_folder + "/analysis_result.md", priority_flow)
        make_md.make_md_file()

        # Claude 분석 실행
        __run_claude_analysis(json_file_path, output_folder)


if __name__ == '__main__':
    import sys

    output_folder = sys.argv[1]
    main(output_folder)
import json
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict


class ResponseProcessor:
    """Claude 응답을 처리하고 분석하는 클래스"""

    def __init__(self, config_manager):
        self.config = config_manager

    def process_analysis_results(self, results_file: str, output_folder: str) -> Dict[str, Any]:
        """Claude 분석 결과를 처리하고 요약 생성"""
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)

            if not results:
                return {"error": "분석 결과가 없습니다."}

            # 결과 분석 및 처리
            processed_data = {
                "summary": self._generate_summary_stats(results),
                "risk_assessment": self._assess_risks(results),
                "prioritized_issues": self._prioritize_issues(results),
                "recommendations": self._extract_recommendations(results),
                "detailed_analysis": self._process_detailed_analysis(results),
                "charts_data": self._prepare_chart_data(results)
            }

            # 처리된 결과 저장
            self._save_processed_results(processed_data, output_folder)

            return processed_data

        except Exception as e:
            return {"error": f"결과 처리 중 오류 발생: {e}"}

    def _generate_summary_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """요약 통계 생성"""
        total_flows = len(results)
        sensitivity_counts = defaultdict(int)
        risk_levels = defaultdict(int)

        for result in results:
            sensitivity = result.get('sensitivity', 0)
            sensitivity_counts[sensitivity] += 1

            # Claude 분석에서 위험도 추출
            analysis = result.get('claude_analysis', '')
            risk_level = self._extract_risk_level(analysis)
            risk_levels[risk_level] += 1

        return {
            "total_flows": total_flows,
            "sensitivity_distribution": dict(sensitivity_counts),
            "risk_distribution": dict(risk_levels),
            "high_risk_count": risk_levels.get('높음', 0),
            "medium_risk_count": risk_levels.get('중간', 0),
            "low_risk_count": risk_levels.get('낮음', 0)
        }

    def _assess_risks(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """위험도 평가"""
        risk_assessments = []

        for i, result in enumerate(results):
            analysis = result.get('claude_analysis', '')
            original_data = result.get('original_data', {})

            # Claude 분석에서 정보 추출
            risk_level = self._extract_risk_level(analysis)
            vulnerability_types = self._extract_vulnerability_types(analysis)
            attack_scenarios = self._extract_attack_scenarios(analysis)

            tainted_items = original_data.get('tainted', [])
            file_info = tainted_items[0] if tainted_items else {}

            risk_assessment = {
                "flow_id": i + 1,
                "file_path": file_info.get('file_path', 'Unknown'),
                "method_name": file_info.get('method_name', 'Unknown'),
                "sensitivity": original_data.get('sensitivity', 0),
                "risk_level": risk_level,
                "vulnerability_types": vulnerability_types,
                "attack_scenarios": attack_scenarios,
                "priority_score": self._calculate_priority_score(
                    original_data.get('sensitivity', 0),
                    risk_level,
                    len(vulnerability_types)
                )
            }

            risk_assessments.append(risk_assessment)

        # 우선순위 점수로 정렬
        risk_assessments.sort(key=lambda x: x['priority_score'], reverse=True)
        return risk_assessments

    def _prioritize_issues(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """이슈 우선순위 결정"""
        risk_assessments = self._assess_risks(results)

        prioritized_issues = []
        for assessment in risk_assessments[:10]:  # 상위 10개만
            issue = {
                "flow_id": assessment["flow_id"],
                "title": f"Flow {assessment['flow_id']}: {Path(assessment['file_path']).name}",
                "description": f"{assessment['method_name']} 메소드의 보안 이슈",
                "risk_level": assessment["risk_level"],
                "priority_score": assessment["priority_score"],
                "estimated_fix_time": self._estimate_fix_time(assessment),
                "impact": self._assess_impact(assessment),
                "exploitability": self._assess_exploitability(assessment)
            }
            prioritized_issues.append(issue)

        return prioritized_issues

    def _extract_recommendations(self, results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Claude 분석에서 개선사항 추출"""
        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": [],
            "architectural": []
        }

        for result in results:
            analysis = result.get('claude_analysis', '')

            # 정규표현식으로 개선사항 추출
            immediate_fixes = self._extract_text_sections(analysis,
                ['즉시', '긴급', '즉각', '바로'])
            short_term_fixes = self._extract_text_sections(analysis,
                ['단기', '짧은', '빠른', '곧'])
            long_term_fixes = self._extract_text_sections(analysis,
                ['장기', '긴', '미래', '계획'])
            arch_fixes = self._extract_text_sections(analysis,
                ['아키텍처', '구조', '시스템', '전체'])

            recommendations["immediate"].extend(immediate_fixes)
            recommendations["short_term"].extend(short_term_fixes)
            recommendations["long_term"].extend(long_term_fixes)
            recommendations["architectural"].extend(arch_fixes)

        # 중복 제거
        for key in recommendations:
            recommendations[key] = list(set(recommendations[key]))

        return recommendations

    def _process_detailed_analysis(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """상세 분석 결과 처리"""
        detailed_analysis = []

        for i, result in enumerate(results):
            analysis = result.get('claude_analysis', '')
            original_data = result.get('original_data', {})

            processed_analysis = {
                "flow_id": i + 1,
                "raw_analysis": analysis,
                "structured_analysis": self._structure_analysis(analysis),
                "code_suggestions": self._extract_code_suggestions(analysis),
                "references": self._extract_references(analysis),
                "confidence_score": self._calculate_confidence_score(analysis)
            }

            detailed_analysis.append(processed_analysis)

        return detailed_analysis

    def _prepare_chart_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """차트용 데이터 준비"""
        sensitivity_data = defaultdict(int)
        risk_data = defaultdict(int)
        vulnerability_types = defaultdict(int)

        for result in results:
            # 민감도 분포
            sensitivity = result.get('sensitivity', 0)
            sensitivity_data[sensitivity] += 1

            # 위험도 분포
            analysis = result.get('claude_analysis', '')
            risk_level = self._extract_risk_level(analysis)
            risk_data[risk_level] += 1

            # 취약점 유형 분포
            vuln_types = self._extract_vulnerability_types(analysis)
            for vuln_type in vuln_types:
                vulnerability_types[vuln_type] += 1

        return {
            "sensitivity_chart": {
                "labels": ["낮음", "중간", "높음"],
                "data": [sensitivity_data[1], sensitivity_data[2], sensitivity_data[3]]
            },
            "risk_chart": {
                "labels": list(risk_data.keys()),
                "data": list(risk_data.values())
            },
            "vulnerability_types_chart": {
                "labels": list(vulnerability_types.keys())[:10],  # 상위 10개
                "data": list(vulnerability_types.values())[:10]
            }
        }

    def _extract_risk_level(self, analysis: str) -> str:
        """분석 텍스트에서 위험도 추출"""
        analysis_lower = analysis.lower()

        if any(keyword in analysis_lower for keyword in ['높음', 'high', '위험', '심각', '긴급']):
            return '높음'
        elif any(keyword in analysis_lower for keyword in ['중간', 'medium', '보통', '중등']):
            return '중간'
        elif any(keyword in analysis_lower for keyword in ['낮음', 'low', '경미', '약함']):
            return '낮음'
        else:
            return '알수없음'

    def _extract_vulnerability_types(self, analysis: str) -> List[str]:
        """취약점 유형 추출"""
        vulnerability_patterns = {
            'SQL Injection': ['sql', 'injection', '인젝션', '쿼리'],
            'XSS': ['xss', 'cross-site', '스크립트', 'javascript'],
            'Path Traversal': ['path', 'traversal', '디렉토리', '경로'],
            'Command Injection': ['command', 'exec', '명령', '실행'],
            'LDAP Injection': ['ldap', 'directory'],
            'XXE': ['xxe', 'xml', 'external'],
            'CSRF': ['csrf', 'cross-site request'],
            'Information Disclosure': ['정보', '노출', 'disclosure', '유출'],
            'Authentication Bypass': ['인증', 'authentication', '우회', 'bypass'],
            'Authorization Issues': ['권한', 'authorization', '접근제어']
        }

        found_types = []
        analysis_lower = analysis.lower()

        for vuln_type, keywords in vulnerability_patterns.items():
            if any(keyword in analysis_lower for keyword in keywords):
                found_types.append(vuln_type)

        return found_types

    def _extract_attack_scenarios(self, analysis: str) -> List[str]:
        """공격 시나리오 추출"""
        scenarios = []
        lines = analysis.split('\n')

        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['공격', 'attack', '시나리오', 'scenario', '악용']):
                if len(line.strip()) > 10:  # 의미있는 길이의 문장만
                    scenarios.append(line.strip())

        return scenarios[:5]  # 최대 5개

    def _calculate_priority_score(self, sensitivity: int, risk_level: str, vuln_count: int) -> float:
        """우선순위 점수 계산"""
        risk_weights = {'높음': 3.0, '중간': 2.0, '낮음': 1.0, '알수없음': 1.5}

        base_score = sensitivity * 10
        risk_score = risk_weights.get(risk_level, 1.0) * 20
        vuln_score = min(vuln_count * 5, 25)  # 최대 25점

        return base_score + risk_score + vuln_score

    def _estimate_fix_time(self, assessment: Dict[str, Any]) -> str:
        """수정 예상 시간 계산"""
        priority_score = assessment.get('priority_score', 0)

        if priority_score >= 70:
            return "즉시 (1-2시간)"
        elif priority_score >= 50:
            return "당일 (4-8시간)"
        elif priority_score >= 30:
            return "1-2일"
        else:
            return "1주일 이내"

    def _assess_impact(self, assessment: Dict[str, Any]) -> str:
        """영향도 평가"""
        risk_level = assessment.get('risk_level', '낮음')
        vuln_types = assessment.get('vulnerability_types', [])

        high_impact_vulns = ['SQL Injection', 'Command Injection', 'XXE']

        if risk_level == '높음' or any(vuln in high_impact_vulns for vuln in vuln_types):
            return "높음"
        elif risk_level == '중간':
            return "중간"
        else:
            return "낮음"

    def _assess_exploitability(self, assessment: Dict[str, Any]) -> str:
        """악용 가능성 평가"""
        vuln_types = assessment.get('vulnerability_types', [])

        easy_exploit_vulns = ['SQL Injection', 'XSS', 'Path Traversal']

        if any(vuln in easy_exploit_vulns for vuln in vuln_types):
            return "쉬움"
        elif len(vuln_types) > 0:
            return "보통"
        else:
            return "어려움"

    def _extract_text_sections(self, text: str, keywords: List[str]) -> List[str]:
        """키워드를 포함한 텍스트 섹션 추출"""
        sections = []
        lines = text.split('\n')

        for line in lines:
            line_clean = line.strip()
            if any(keyword in line_clean for keyword in keywords) and len(line_clean) > 10:
                sections.append(line_clean)

        return sections

    def _structure_analysis(self, analysis: str) -> Dict[str, str]:
        """분석 텍스트를 구조화"""
        sections = {
            "risk_assessment": "",
            "vulnerability_details": "",
            "attack_scenarios": "",
            "recommendations": "",
            "code_examples": ""
        }

        current_section = "general"
        lines = analysis.split('\n')

        for line in lines:
            line_clean = line.strip()

            if any(keyword in line_clean.lower() for keyword in ['위험', 'risk', '평가']):
                current_section = "risk_assessment"
            elif any(keyword in line_clean.lower() for keyword in ['취약', 'vulnerability', '문제']):
                current_section = "vulnerability_details"
            elif any(keyword in line_clean.lower() for keyword in ['공격', 'attack', '시나리오']):
                current_section = "attack_scenarios"
            elif any(keyword in line_clean.lower() for keyword in ['개선', '권고', 'recommendation']):
                current_section = "recommendations"
            elif '```' in line_clean:
                current_section = "code_examples"

            if current_section in sections:
                sections[current_section] += line + '\n'

        return sections

    def _extract_code_suggestions(self, analysis: str) -> List[str]:
        """코드 제안사항 추출"""
        code_blocks = re.findall(r'```[\s\S]*?```', analysis)
        return [block.strip('`').strip() for block in code_blocks]

    def _extract_references(self, analysis: str) -> List[str]:
        """참조 자료 추출"""
        references = []

        # URL 패턴
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, analysis)
        references.extend(urls)

        # CVE 패턴
        cve_pattern = r'CVE-\d{4}-\d{4,}'
        cves = re.findall(cve_pattern, analysis)
        references.extend(cves)

        # OWASP 참조
        if 'owasp' in analysis.lower():
            references.append('OWASP Top 10')

        return references

    def _calculate_confidence_score(self, analysis: str) -> float:
        """분석 신뢰도 점수 계산"""
        confidence_indicators = {
            'specific_examples': 20,
            'technical_details': 15,
            'multiple_scenarios': 15,
            'code_snippets': 20,
            'references': 15,
            'comprehensive_analysis': 15
        }

        score = 0

        if '```' in analysis:
            score += confidence_indicators['code_snippets']

        if len(re.findall(r'예시|example|scenario', analysis, re.IGNORECASE)) > 2:
            score += confidence_indicators['multiple_scenarios']

        if len(analysis) > 1000:
            score += confidence_indicators['comprehensive_analysis']

        if re.search(r'CVE|OWASP|CWE', analysis, re.IGNORECASE):
            score += confidence_indicators['references']

        return min(score, 100)

    def _save_processed_results(self, processed_data: Dict[str, Any], output_folder: str):
        """처리된 결과 저장"""
        output_path = Path(output_folder)

        # JSON 형태로 저장
        results_file = output_path / 'processed_analysis_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

        # 요약 보고서 생성
        summary_file = output_path / 'executive_summary.md'
        self._generate_executive_summary(processed_data, summary_file)

    def _generate_executive_summary(self, data: Dict[str, Any], output_file: Path):
        """경영진 요약 보고서 생성"""
        summary = data.get('summary', {})
        prioritized_issues = data.get('prioritized_issues', [])
        recommendations = data.get('recommendations', {})

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 보안 분석 경영진 요약 보고서\n\n")
            f.write(f"**생성일**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 전체 현황\n")
            f.write(f"- **총 분석된 취약점**: {summary.get('total_flows', 0)}개\n")
            f.write(f"- **높은 위험도**: {summary.get('high_risk_count', 0)}개\n")
            f.write(f"- **중간 위험도**: {summary.get('medium_risk_count', 0)}개\n")
            f.write(f"- **낮은 위험도**: {summary.get('low_risk_count', 0)}개\n\n")

            f.write("## 즉시 조치 필요 항목\n")
            urgent_issues = [issue for issue in prioritized_issues if issue['risk_level'] == '높음']
            for issue in urgent_issues[:5]:
                f.write(f"- **{issue['title']}** (우선순위: {issue['priority_score']:.1f})\n")
                f.write(f"  - 예상 수정 시간: {issue['estimated_fix_time']}\n")
                f.write(f"  - 영향도: {issue['impact']}\n\n")

            f.write("## 권고사항\n")
            for category, items in recommendations.items():
                if items:
                    category_name = {
                        'immediate': '즉시 조치',
                        'short_term': '단기 개선',
                        'long_term': '장기 계획',
                        'architectural': '아키텍처 개선'
                    }.get(category, category)

                    f.write(f"### {category_name}\n")
                    for item in items[:3]:  # 상위 3개만
                        f.write(f"- {item}\n")
                    f.write("\n")
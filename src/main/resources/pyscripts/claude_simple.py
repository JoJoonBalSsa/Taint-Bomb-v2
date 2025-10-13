import json
import os

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    print("ERROR : Can't find anthropic module.")


def send_to_claude(priority_flow, user_api_key=None):
    """priority_flow를 Claude에게 전달"""

    if not CLAUDE_AVAILABLE:
        return None

    if not user_api_key:
        print("ERROR : Can't find user API key.")
        print("Current api_key:", user_api_key)
        return None

    # Claude에 전송
    try:
        client = anthropic.Anthropic(api_key=user_api_key)

        # priority_flow를 문자열로 변환
        flow_text = "\n".join([str(flow) for flow in priority_flow])

        # 간단한 프롬프트
        prompt = f"""
다음은 Java 코드에서 발견된 위험한 taint flow들입니다:

{flow_text}

각 flow의 형식: [민감도, 메소드1, 메소드2, ...]
- 민감도: 1(낮음), 2(중간), 3(높음)

이 taint flow들을 분석하여 보안 취약점을 설명해주세요.
"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.content[0].text
        print("Claude 분석 완료")
        return result

    except Exception as e:
        print(f"Claude API 호출 실패: {e}")
        return None
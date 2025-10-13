import string
import secrets
import re

class MethodSplit:
    def __init__(self, method):
        self.method = method

        modified_method, functions = self.__dynamic_method_split(method)
        self.merged_code = self.__merge_methods_and_functions(modified_method, functions)

    def __extract_java_method_info(self, method_code):
        method_pattern = re.compile(r'\b(public|protected|private)\s+(static\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{')
        match = method_pattern.search(method_code)

        if match:
            access_modifier = match.group(1)
            is_static = bool(match.group(2))  # static 키워드가 있으면 True, 없으면 False
            return_type = match.group(3)
            method_name = match.group(4)
            parameters = match.group(5).strip()

            # 매개변수 리스트로 변환하고 변수와 자료형 추출
            param_list = []
            if parameters:
                for param in parameters.split(','):
                    param_type, param_name = param.strip().split()
                    param_list.append((param_type, param_name))

            start_index = match.end()
            body = ""
            brace_count = 1
            for i, char in enumerate(method_code[start_index:]):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        body = method_code[start_index:start_index + i].strip()
                        break

            return access_modifier, return_type, method_name, param_list, body, is_static

        else:
            return None  # 메소드 패턴이 일치하지 않을 경우

    def __dynamic_method_split(self, method_code):
        result = self.__extract_java_method_info(method_code)
        if not result:
            return None, None

        access_modifier, return_type, method_name, param_list, body, is_static = result

        # 파라미터 타입 매핑 (업데이트 대상/사용 변수 타입 해석에 사용)
        param_types = {pname: ptype for ptype, pname in param_list}

        extracted_functions = []
        modified_body = []

        # 세미콜론 단순 분할 대신, 최상위 레벨에서만 문장 분할
        statements = self.__split_top_level_statements(body)

        # 선언/업데이트 패턴 (최상위 단순 라인에만 적용)
        var_pattern = re.compile(r'^\s*(\w+)\s+(\w+)\s*=\s*(.+)$')          # e.g., "int x = 3"
        update_pattern = re.compile(r'^\s*(\w+)\s*=\s*(?![=!])(.*)$')       # e.g., "x = x + y"

        # 로컬 변수 타입 추적 (블록 밖에서 선언된 것만)
        local_vars = {}

        for line in statements:
            line = line.strip()
            if not line:
                continue

            # 제어문 블록은 통째로 보존 (for/if/while 헤더 또는 중괄호 포함 시)
            if re.match(r'^\s*(for|if|while)\s*\(', line) or '{' in line or '}' in line:
                # 원문 유지. 끝이 '{'면 세미콜론 없이, 아니면 세미콜론 추가
                modified_body.append(line + ('' if line.endswith('{') else ';'))
                continue

            # 최상위 단순 라인에 대해서만 선언/업데이트 추출 시도
            declare_m = var_pattern.match(line)
            update_m = update_pattern.match(line)

            # ---- 변수 선언: 블록 밖에서만 추적/분리 ----
            if declare_m:
                var_type, var_name, expr = declare_m.groups()
                expr = expr.strip().rstrip(';')

                # 로컬 심볼 테이블에 타입 등록
                local_vars[var_name] = var_type

                # expr에서 식별자 토큰 추출
                tokens = re.findall(r'\b[a-zA-Z_]\w*\b', expr)
                used_order = []
                for tok in tokens:
                    if tok not in used_order:
                        used_order.append(tok)

                # 실제로 파라미터로 넘길 변수만 필터링 (로컬 or 파라미터)
                used_vars = [v for v in used_order if v in local_vars or v in param_types]

                # 새 함수명
                function_name = self.__generate_random_string()

                # 시그니처 구성
                sig_parts = []
                for v in used_vars:
                    if v in local_vars:
                        sig_parts.append(f"{local_vars[v]} {v}")
                    else:
                        sig_parts.append(f"{param_types[v]} {v}")

                new_function = (
                    f"public {'static ' if is_static else ''}{var_type} {function_name}"
                    f"({', '.join(sig_parts)}) {{\n"
                    f"    {var_type} {var_name} = {expr};\n"
                    f"    return {var_name};\n"
                    f"}}\n"
                )
                extracted_functions.append(new_function)

                # 본문 치환
                call_args = ', '.join(used_vars)
                modified_body.append(f"{var_type} {var_name} = {function_name}({call_args});")
                continue

            # ---- 변수 업데이트: 블록 밖 + 타입 해석 가능할 때만 분리 ----
            if update_m:
                var_name, expr = update_m.groups()
                var_name = var_name.strip()
                expr = expr.strip().rstrip(';')

                # 업데이트 대상 변수 타입 해석 (로컬 → 파라미터 순)
                target_type = local_vars.get(var_name) or param_types.get(var_name)
                if not target_type:
                    # 타입 해석 불가 → 분리하지 않고 원문 유지
                    modified_body.append(f"{var_name} = {expr};")
                    continue

                # expr 토큰에서 사용 변수 추출
                tokens = re.findall(r'\b[a-zA-Z_]\w*\b', expr)
                used_order = []
                for tok in tokens:
                    if tok not in used_order:
                        used_order.append(tok)

                # 파라미터 후보
                used_vars = [v for v in used_order if v in local_vars or v in param_types]
                # 업데이트 대상도 포함 (선두/말미 어디든 상관 없으나, 여기선 말미에 추가 후 중복 제거)
                used_vars.append(var_name)
                # 순서 유지 중복 제거
                seen = set()
                used_vars = [v for v in used_vars if not (v in seen or seen.add(v))]

                # 모두 타입이 해석 가능한지 점검 (안되면 원문 유지)
                for v in used_vars:
                    if v not in local_vars and v not in param_types:
                        modified_body.append(f"{var_name} = {expr};")
                        break
                else:
                    # 시그니처 구성
                    sig_parts = []
                    for v in used_vars:
                        if v in local_vars:
                            sig_parts.append(f"{local_vars[v]} {v}")
                        else:
                            sig_parts.append(f"{param_types[v]} {v}")

                    function_name = self.__generate_random_string()
                    new_function = (
                        f"public {'static ' if is_static else ''}{target_type} {function_name}"
                        f"({', '.join(sig_parts)}) {{\n"
                        f"    {var_name} = {expr};\n"
                        f"    return {var_name};\n"
                        f"}}\n"
                    )
                    extracted_functions.append(new_function)

                    call_args = ', '.join(used_vars)
                    modified_body.append(f"{var_name} = {function_name}({call_args});")
                continue

            # 선언/업데이트가 아니면 세미콜론 붙여 유지
            modified_body.append(line + ';')

        # 수정된 메서드 조립
        header_params = ', '.join([f"{ptype} {pname}" for ptype, pname in param_list])
        modified_method = (
            f"public {'static ' if is_static else ''}{return_type} {method_name}({header_params}) {{\n    "
            + "\n    ".join(modified_body).rstrip(';')
        )

        return modified_method, extracted_functions

    def __merge_methods_and_functions(self, modified_method, extracted_functions):
        try:
            # modified_method가 None인 경우 예외 발생
            if modified_method is None:
                raise ValueError("Modified method is None. The input method code might not match the expected Java method pattern.")

            # Modified Method 마지막 중괄호 제거
            if modified_method.endswith("}\n"):
                modified_method = modified_method[:-2]  # 마지막 중괄호 제거

            # Extracted Functions 추가
            merged_code = modified_method + '\n}\n\n' + '\n'.join(extracted_functions) + '\n'

            return merged_code

        except AttributeError as e:
            # AttributeError 발생 시 처리 (NoneType에서 .endswith() 호출하는 경우)
            print(f"An error occurred: {e}")
            return "// Error: Invalid method code."

        except ValueError as e:
            # ValueError 발생 시 처리 (None 값이 반환된 경우)
            print(f"An error occurred: {e}")
            return "// Error: Method pattern did not match the expected format."

    def __generate_random_string(self, length=8):
        if length < 1:
            return None
        letters = string.ascii_lowercase
        letters_and_digits = string.ascii_lowercase + string.digits
        first_char = secrets.choice(letters)
        rest_chars = "".join(secrets.choice(letters_and_digits) for _ in range(length - 1))
        return first_char + rest_chars

    def __split_top_level_statements(self, body: str):
        stmts = []
        buf = []
        brace = 0      # { } 깊이
        paren = 0      # ( ) 깊이
        in_str = False
        str_ch = None
        i = 0
        while i < len(body):
            ch = body[i]
            # 문자열 리터럴 단순 처리
            if ch in ("'", '"'):
                if not in_str:
                    in_str, str_ch = True, ch
                elif str_ch == ch:
                    in_str, str_ch = False, None
                buf.append(ch)
            elif not in_str:
                if ch == '{':
                    brace += 1
                    buf.append(ch)
                elif ch == '}':
                    brace -= 1
                    buf.append(ch)
                elif ch == '(':
                    paren += 1
                    buf.append(ch)
                elif ch == ')':
                    paren -= 1
                    buf.append(ch)
                elif ch == ';' and paren == 0 and brace == 0:
                    # 최상위에서만 문장 분할
                    stmts.append(''.join(buf).strip())
                    buf = []
                else:
                    buf.append(ch)
            else:
                buf.append(ch)
            i += 1
        if buf:
            stmts.append(''.join(buf).strip())
        return [s for s in (stmt.strip() for stmt in stmts) if s]
    
    def get_new_method(self):
        return self.merged_code
    
if __name__ == '__main__':
    # 테스트용 자바 코드 1 (변수 선언 + return)
    java_code1 = """
    public int calc() {
        int x = 3;
        return x;
    }
    """
    print("=== TEST 1 ===")
    ms1 = MethodSplit(java_code1)
    print(ms1.get_new_method())

    # 테스트용 자바 코드 2 (매개변수, 업데이트 포함)
    java_code2 = """
    public int add(int num) {
        int y = num * 2;
        y = y + num;
        return y;
    }
    """
    print("\n=== TEST 2 ===")
    ms2 = MethodSplit(java_code2)
    print(ms2.get_new_method())

    # 테스트용 자바 코드 3 (static 포함)
    java_code3 = """
    public static int plus(int a, int b) {
        int sum = a + b;
        sum = sum + 10;
        return sum;
    }
    """
    print("\n=== TEST 3 ===")
    ms3 = MethodSplit(java_code3)
    print(ms3.get_new_method())

    # 테스트용 자바 코드 4 (패턴 불일치)
    java_code4 = "int not_a_method = 0;"
    print("\n=== TEST 4 ===")
    ms4 = MethodSplit(java_code4)
    print(ms4.get_new_method())

    java_code5 = """
    public int sumLoop(int n) {
        int total = 0;
        for (int i = 0; i < n; i++) {
            int a = 0;
            total = total + i + a;
        }
        total = total + 10;
        return total;
    }
    """
    print("\n=== TEST 5 ===")
    ms5 = MethodSplit(java_code5)
    print(ms5.get_new_method())

    java_code7 = """
    public int checkValue(int x) {
        int result = 0;
        if (x > 10) {
            int temp = x * 2;
            result = result + temp;
        }
        result = result + 5;
        return result;
    }
    """
    print("\n=== TEST 7 (Condition Only) ===")
    ms7 = MethodSplit(java_code7)
    print(ms7.get_new_method())
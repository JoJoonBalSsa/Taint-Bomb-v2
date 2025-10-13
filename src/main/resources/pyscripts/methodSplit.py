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
            is_static = bool(match.group(2))
            return_type = match.group(3)
            method_name = match.group(4)
            parameters = match.group(5).strip()

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
            return None

    def __dynamic_method_split(self, method_code):
        result = self.__extract_java_method_info(method_code)
        if not result:
            return None, None

        access_modifier, return_type, method_name, param_list, body, is_static = result


        control_block_pattern = re.compile(
            r'\b(if|else\s+if|else|for|while|switch|case|do|foreach|try|catch)\b'
        )

        body_wo_comments = re.sub(r'//.*?$|/\*.*?\*/', '', body, flags=re.S | re.M)

        if control_block_pattern.search(body_wo_comments):
            original_method = (
                f"public {'static ' if is_static else ''}{return_type} {method_name}("
                + ", ".join([f"{t} {p}" for t, p in param_list])
                + ") {\n"
                + body + "\n}"
            )
            return original_method, []

        extracted_functions = []
        modified_body = []

        statements = body.split(';')
        var_pattern = re.compile(r'(\w+)\s+(\w+)\s*=')
        update_pattern = re.compile(r'(\w+)\s*=\s*(?![=!])(.+)')

        local_vars = {}
        brace_count = 0

        for line in statements:
            line = line.strip()
            if not line:
                continue
            if '{' in line:
                brace_count += 1
            if '}' in line:
                brace_count -= 1

            declare_match = var_pattern.search(line)
            update_match = update_pattern.search(line)

            if declare_match and brace_count == 0:
                var_type, var_name = declare_match.groups()
                expression = line.split('=')[1].strip()

                local_vars[var_name] = var_type

                used_vars = [v for v in local_vars if v in expression] + [
                    p for _, p in param_list if p in expression
                ]
                used_vars = list(dict.fromkeys(used_vars))

                func_name = self.__generate_random_string()
                new_func = (
                    f"public {'static ' if is_static else ''}{var_type} {func_name}("
                    + ", ".join(
                        [f"{local_vars[v]} {v}" for v in used_vars if v in local_vars]
                        + [f"{t} {p}" for t, p in param_list if p in used_vars]
                    )
                    + f") {{\n    {var_type} {var_name} = {expression};\n    return {var_name};\n}}\n"
                )
                extracted_functions.append(new_func)
                modified_body.append(f"{var_type} {var_name} = {func_name}({', '.join(used_vars)});")

            elif update_match:
                var_name, expression = update_match.groups()
                if var_name not in local_vars:
                    modified_body.append(line + ';')
                    continue

                used_vars = [v for v in local_vars if v in expression] + [
                    p for _, p in param_list if p in expression
                ]
                used_vars.append(var_name)
                used_vars = list(dict.fromkeys(used_vars))

                func_name = self.__generate_random_string()
                new_func = (
                    f"public {'static ' if is_static else ''}{local_vars[var_name]} {func_name}("
                    + ", ".join(
                        [f"{local_vars[v]} {v}" for v in used_vars if v in local_vars]
                        + [f"{t} {p}" for t, p in param_list if p in used_vars]
                    )
                    + f") {{\n    {var_name} = {expression};\n    return {var_name};\n}}\n"
                )
                extracted_functions.append(new_func)
                modified_body.append(f"{var_name} = {func_name}({', '.join(used_vars)});")
            else:
                modified_body.append(line + ';')

        modified_method = (
            f"public {'static ' if is_static else ''}{return_type} {method_name}("
            + ", ".join([f"{t} {p}" for t, p in param_list])
            + ") {\n    "
            + "\n    ".join(modified_body).rstrip(';')
            + "\n}"
        )
        return modified_method, extracted_functions

    def __merge_methods_and_functions(self, modified_method, extracted_functions):
        try:
            if modified_method is None:
                raise ValueError("Modified method is None. The input method code might not match the expected Java method pattern.")

            mm = (modified_method or "").rstrip()

            if not mm.endswith('}'):
                mm += '\n}'

            if not extracted_functions:
                return mm + '\n'

            merged_code = mm + '\n\n' + '\n'.join(extracted_functions) + '\n'
            return merged_code

        except AttributeError as e:
            print(f"An error occurred: {e}")
            return "// Error: Invalid method code."
        except ValueError as e:
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
            total = total + i;
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
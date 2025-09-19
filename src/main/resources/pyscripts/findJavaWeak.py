import re, sys, pathlib, ast

PAT = re.compile(r'\b(new\s+ObjectInputStream|readObject\s*\()')
SQL_PATTERN = re.compile(r'createStatement\(|executeQuery\(|createQuery\(|\"SELECT.*%\"|\+ *[a-zA-Z0-9_\.]+ *\+')

class FindJavaWeakpoint:
    def __init__(self):
        self.findings = []
    #Sql인젝션
    def scan_java(p):
        s = p.read_text(errors='ignore')
        for i, line in enumerate(s.splitlines(), start=1):
            if SQL_PATTERN.search(line):
                print(f'{p}:{i}: {line.strip()}')
    #역 직렬화
    def scan_file(path):
        s = path.read_text(encoding='utf-8', errors='ignore')
        hits = []
        for m in PAT.finditer(s):
            line = s.count('\n', 0, m.start()) + 1
            hits.append((line, s.splitlines()[line-1].strip()))
        return hits
    #runtime injection with AST
    def visit_Call(self, node):
        # eval / exec
        if isinstance(node.func, ast.Name) and node.func.id in ('eval','exec'):
            self.findings.append((node.lineno, f'Call to {node.func.id}'))
        # subprocess(..., shell=True)
        if getattr(node.func, 'attr', '') == 'Popen' or getattr(node.func, 'id', '') == 'Popen':
            for kw in node.keywords:
                if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append((node.lineno, 'subprocess shell=True'))
        self.generic_visit(node)
    #부적절한 인증/ 권한검사

    #불완전한 TLS/증명서 검증
    
    #과도한 검증/ 민감정보 로그 노출

if __name__ == '__main__':
    pass
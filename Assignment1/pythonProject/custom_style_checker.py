import ast
import os
import re

class StyleChecker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.report_path = f"style_report_{os.path.basename(file_path)}.txt"
        self.content = ""

    def check_style(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=self.file_path)
            self.analyze_tree(tree)
            self.save_report(self.content)

    def count_lines(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        non_empty_lines = [line for line in lines]
        self.content += f"Total number of lines: {len(non_empty_lines)}\n"

    def analyze_tree(self, tree):
        self.count_lines()
        self.check_imports(tree)
        self.check_classes(tree)
        self.check_functions(tree)
        self.check_docstrings(tree)
        self.check_type_annotations(tree)
        self.check_naming_conventions(tree)

    def check_imports(self, tree):
        imports = [node for node in tree.body if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]
        self.content += "Imports:\n"
        for imp in imports:
            if isinstance(imp, ast.Import):
                self.content += ", ".join([alias.name for alias in imp.names]) + "\n"
            elif isinstance(imp, ast.ImportFrom):
                self.content += f"{imp.module}\n"

    def check_classes(self, tree):
        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
        self.content += "Classes:\n"
        for cls in classes:
            self.content += f"{cls.name}\n"

    def check_functions(self, tree):
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and not any((isinstance(parent, ast.ClassDef) for parent in ast.walk(node)))]
        self.content += "Functions:\n"
        for func in functions:
            self.content += f"{func.name}\n"

    def check_docstrings(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    self.content += f"{node.name}: DocString not found.\n"
                else:
                    self.content += f"{node.name}: {ast.get_docstring(node)} + \n"

    def check_type_annotations(self, tree):
        f = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not any(isinstance(arg, ast.arg) and arg.annotation for arg in node.args.args):
                self.content += f"Function {node.name} does not use type annotations.\n"
                f = 1
        if f == 0:
            self.content += "Type annotation is used in all functions and methods\n"

    def check_naming_conventions(self, tree):
        f = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                pattern = re.compile("^[A-Z][a-zA-Z]*$")
                if not pattern.match(node.name):
                    f = 1
                    self.content += f"Class {node.name} does not follow CamelCase naming convention.\n"
            elif isinstance(node, ast.FunctionDef):
                pattern = re.compile("^[a-z_][a-z_]*$")
                if not pattern.match(node.name):
                    f = 1
                    self.content += f"Function {node.name} does not follow lower_case_with_underscores naming convention.\n"
        if f == 0:
            self.content += "All names adhere to the specified naming convention\n"

    def save_report(self, content):
        with open(self.report_path, 'w') as report_file:
            report_file.write(content)

if __name__ == "__main__":
    checker = StyleChecker('test.py')
    checker.check_style()


import ast


def topLevelNamesInBody(body):
    names = set()
    for x in body:
        names |= namesInNode(x)
    return names


def localNamesInBody(body):
    names = set()
    for node in body:
        names |= namesInNode(node)
        for x in ast.walk(node):
            names |= namesInNode(x)
    return names


def namesInNode(x):
    names = set()
    if isinstance(x, ast.Assign):
        for target in x.targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
    elif (
            isinstance(x, ast.FunctionDef) or
            isinstance(x, ast.ClassDef)):
        names.add(x.name)
    return names


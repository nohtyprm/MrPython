import ast
import astor

def wrap_node(var_id):
    code = "{0} = ListWrapper.wrap({0})".format(var_id)
    return ast.parse(code)

def unwrap_node(var_id):
    code  = "ListWrapper.unwrap({0})".format(var_id)
    return ast.parse(code)

class UnwrapperTransformer(ast.NodeTransformer):
    def visit_Name(self, node):
        return unwrap_node(node.id)

class EffectTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()

    def visit_Return(self, node):
        unwrapper = UnwrapperTransformer()
        node.value = unwrapper.visit(node.value).body[0].value
        return node

    def visit_FunctionDef(self, node):
        # Unwrap
        node.body = [self.visit(node) for node in node.body]
        print(ast.dump(node))
        # Wrap args
        args = node.args.args
        args_id = map(lambda arg: arg.arg, args)
        nodes = map(wrap_node, args_id)
        for wrapper_node in nodes:
            node.body.insert(0, wrapper_node)
        return node

def transform(node):
    # Insert list wrapper code
    with open("mrpython/effects/ListWrapper.py") as file:
        code = file.read()
        wrapper_node = ast.parse(code).body
        node.body = wrapper_node + node.body
    return node
    
if __name__ == '__main__':
    effect = EffectTransformer()
    with open("examples/list_add.py") as file:
        node = ast.parse(file.read())
        node = effect.visit(node)
        node = transform(node)
        code = astor.to_source(node)
        print(code)
        exec(code)

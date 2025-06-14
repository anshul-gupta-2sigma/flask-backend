from flask import Flask, request, jsonify
import tree_sitter_python as tspython
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from difflib import SequenceMatcher

app = Flask(__name__)

# Load parsers
PY_LANGUAGE = Language(tspython.language())
JV_LANGUAGE = Language(tsjava.language())
parser_py = Parser(PY_LANGUAGE)
parser_jv = Parser(JV_LANGUAGE)

def get_tree_tokens(code, parser):
    try:
        tree = parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        tokens = []

        def walk(node):
            if node.child_count == 0:
                tokens.append(node.type)
            else:
                for child in node.children:
                    walk(child)

        walk(root_node)
        return tokens
    except Exception:
        return []

def robust_ast_similarity(code1, code2, parser):
    tokens1 = get_tree_tokens(code1, parser)
    tokens2 = get_tree_tokens(code2, parser)
    if not tokens1 or not tokens2:
        return 0.0
    return round(SequenceMatcher(None, tokens1, tokens2).ratio(), 4)

@app.route("/similarity", methods=["POST"])
def similarity():
    try:
        data = request.get_json()
        code1 = data.get("code1", "")
        code2 = data.get("code2", "")
        lang = data.get("lang", "Python")

        parser = parser_jv if lang.lower() == "java" else parser_py
        similarity = robust_ast_similarity(code1, code2, parser)

        return jsonify({"similarity": similarity})
    except Exception as e:
        return jsonify({"error": str(e), "similarity": 0}), 500

@app.route("/")
def index():
    return jsonify({"message": "AST Similarity API is running."})

if __name__ == "__main__":
    app.run(debug=True)

import os
import logging
import javalang

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from utils.config_utils import load_from_file, save_to_file

INDEX_DIR = "code_index"
INDEX_JSON = os.path.join(INDEX_DIR, "index.json")

def parse_java_file(file_path, repo_path, index_data):
    """
    Parses a Java file to extract class, method, dependency, and method call information.

    Args:
        file_path (str): The path to the Java file.
        repo_path (str): The root path of the repository (used for relative paths).
    """
    logging.info(f"Parsing Java file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = javalang.parse.parse(f.read())
    except Exception as e:
        logging.error(f"Error parsing {file_path}: {e}")
        return

    # Initialize data structure if not already indexed
    if file_path not in index_data:
        index_data[file_path] = {"classes": [], "methods": [], "dependencies": [], "call_graph": [], "package": ""}

    parsed_data = index_data[file_path]

    # Extract package information
    for path, node in tree:
        if isinstance(node, javalang.tree.PackageDeclaration):
            parsed_data["package"] = node.name
            break

    # Extract classes and methods
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            parsed_data["classes"].append(node.name)
        elif isinstance(node, javalang.tree.MethodDeclaration):
            # Include class context for method
            parent_class = None
            for p in path:
                if isinstance(p, javalang.tree.ClassDeclaration):
                    parent_class = p.name
                    break

            if parent_class:
                method_info = {
                    "name": node.name,
                    "class": parent_class,
                    "signature": node.name + "(" + ", ".join([p.type.name if hasattr(p.type, 'name') else str(p.type) for p in node.parameters]) + ")",
                    "return_type": str(node.return_type) if node.return_type else "void",
                }
                parsed_data["methods"].append(method_info)

    # Extract dependencies and method calls
    for path, node in tree:
        if isinstance(node, javalang.tree.Import):
            full_import = node.path
            if full_import.startswith("java."):
                continue  # Skip standard library imports
            parsed_data["dependencies"].append(full_import)
        elif isinstance(node, javalang.tree.MethodInvocation):
            # Find caller context
            caller_class = None
            caller_method = None
            for p in reversed(path):  # Reverse to find closest parent
                if isinstance(p, javalang.tree.ClassDeclaration):
                    caller_class = p.name
                elif isinstance(p, javalang.tree.MethodDeclaration):
                    caller_method = p.name

                if caller_class and caller_method:
                    break  # Found both, stop searching

            if not caller_class:
                caller_class = os.path.basename(file_path).replace(".java", "")

            if not caller_method:
                caller_method = "unknown"

            # Determine callee class and method
            if node.qualifier:
                callee_class = node.qualifier
            else:
                callee_class = caller_class  # Calling a method in the same class

            callee_method = node.member
            
            call_info = {
                "caller_class": caller_class,
                "caller_method": caller_method,
                "callee_class": callee_class,
                "callee_method": callee_method,
                "sequence": len(parsed_data["call_graph"]) + 1,  # Add sequence number
            }

            parsed_data["call_graph"].append(call_info)

    index_data[file_path] = parsed_data

# The index is not load here.

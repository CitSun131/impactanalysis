import os
import pydot
import logging
from utils.config_utils import load_from_file

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

INDEX_DIR = "code_index"
INDEX_JSON = os.path.join(INDEX_DIR, "index.json")

DIAGRAM_COLORS = {
    "default_bg": "white",
    "package_bg": "#ECECFC",
    "component_bg": "#B5CAFB",
    "data_store_bg": "#E0E0E0",
    "external_system_bg": "#F0F0F0",
    "edge": "#666666",
}

def generate_diagram_from_index(diagram_name, diagram_file, get_package_name, get_classes, get_dependencies):
    """
    Generates a diagram from the code index.

    Args:
        diagram_name (str): The name of the diagram (used in the label).
        diagram_file (str): The output file path for the diagram.
        get_package_name (function): A function to get the package name from the data.
        get_classes (function): A function to get the list of classes from the data.
        get_dependencies (function): A function to get the list of dependencies from the data.
    """
    logging.info(f"Starting generation of {diagram_name}.")

    index_data = load_from_file(INDEX_JSON)
    if not index_data:
        logging.warning(f"No data found in index.json. Skipping {diagram_name} generation.")
        return

    graph = pydot.Dot(
        graph_type="digraph",
        bgcolor=DIAGRAM_COLORS["default_bg"],
        label=diagram_name,
        fontsize=24,
        labelloc="t",
        rankdir="TB",
        compound="true",
        fontname="Arial",
    )

    packages = {}
    components = {}

    for file_path, data in index_data.items():
        package_name = get_package_name(data)
        if not package_name:
            package_name = "default"

        if package_name not in packages:
            packages[package_name] = {
                "files": [],
                "classes": [],
                "dependencies": set(),
            }

        packages[package_name]["files"].append(file_path)
        packages[package_name]["classes"].extend(get_classes(data))

        dependencies = get_dependencies(data)
        for dep in dependencies:
            if dep and dep != package_name:
                packages[package_name]["dependencies"].add(dep)

    for package_name, package_data in packages.items():
        if not package_data["classes"]:
            continue

        package_id = f"cluster_{package_name.replace('.', '_')}"
        subgraph = pydot.Cluster(
            package_id,
            label=f"Package: {package_name}",
            style="filled",
            fillcolor=DIAGRAM_COLORS["package_bg"],
            color="black",
            fontsize=16,
            fontname="Arial",
        )

        for class_name in package_data["classes"]:
            component_id = f"{package_name}.{class_name}"
            components[component_id] = class_name

            node = pydot.Node(
                component_id,
                label=f"{class_name}",
                shape="box",
                style="filled",
                fillcolor=DIAGRAM_COLORS["component_bg"],
                fontname="Arial",
                margin="0.3,0.1",
                height=0.8,
            )
            subgraph.add_node(node)

        graph.add_subgraph(subgraph)

    for file_path, data in index_data.items():
        if not get_classes(data):
            continue

        source_package = get_package_name(data) or "default"
        source_class = get_classes(data)[0] if get_classes(data) else os.path.basename(file_path).replace(".java", "")
        source_id = f"{source_package}.{source_class}"

        for dep in get_dependencies(data):
            if dep:
                if "." in dep:
                    target_parts = dep.split(".")
                    target_class = target_parts[-1]
                    target_package = ".".join(target_parts[:-1])
                else:
                    target_class = dep
                    target_package = "default"
                target_id = f"{target_package}.{target_class}"

                if source_id in components and target_id in components:
                    edge = pydot.Edge(
                        source_id,
                        target_id,
                        style="solid",
                        color=DIAGRAM_COLORS["edge"],
                        fontsize=10,
                        fontname="Arial",
                        fontcolor=DIAGRAM_COLORS["edge"],
                        label="uses",
                    )
                    graph.add_edge(edge)

    try:
        graph.write_png(diagram_file)
        logging.info(f"{diagram_name} saved as {diagram_file}")
    except Exception as e:
        logging.error(f"Failed to generate {diagram_name}: {e}")

def generate_c4_diagram():
    logging.info("Starting C4 diagram generation.")

    index_data = load_from_file(INDEX_JSON)
    if not index_data:
        logging.warning("No data found in index.json. Skipping C4 diagram generation.")
        return

    diagram_file = os.path.join(INDEX_DIR, "c4_diagram.png")

    graph = pydot.Dot(
        graph_type="graph",
        bgcolor=DIAGRAM_COLORS["default_bg"],
        label="C4 Component Diagram",
        fontsize=24,
        labelloc="t",
        rankdir="TB",
        compound="true",
        fontname="Arial",
    )

    # Extract packages and organize components
    packages = {}
    components = {}

    # First pass: gather package information
    for file_path, data in index_data.items():
        package_name = data.get("package", "")
        if not package_name:
            package_name = "default"

        if package_name not in packages:
            packages[package_name] = {
                "files": [],
                "classes": [],
                "dependencies": set(),
            }

        packages[package_name]["files"].append(file_path)
        packages[package_name]["classes"].extend(data.get("classes", []))

        # Track dependencies between packages
        for dep in data.get("dependencies", []):
            if "." in dep:
                target_package = ".".join(dep.split(".")[:-1])  # Remove class name
                if target_package and target_package != package_name:
                    packages[package_name]["dependencies"].add(target_package)

    # Create subgraphs for packages
    for package_name, package_data in packages.items():
        # Skip empty packages
        if not package_data["classes"]:
            continue

        # Create subgraph for package
        package_id = f"cluster_{package_name.replace('.', '_')}"
        subgraph = pydot.Cluster(
            package_id,
            label=f"Package: {package_name}",
            style="filled",
            fillcolor=DIAGRAM_COLORS["package_bg"],
            color="black",
            fontsize=16,
            fontname="Arial",
        )

        # Add classes as components
        for class_name in package_data["classes"]:
            component_id = f"{package_name}.{class_name}"
            components[component_id] = class_name

            # Create component node with C4 styling
            node = pydot.Node(
                component_id,
                label=f"[Component]\n{class_name}",
                shape="box",
                style="filled",
                fillcolor=DIAGRAM_COLORS["component_bg"],
                fontname="Arial",
                margin="0.3,0.1",
                height=0.8,
            )
            subgraph.add_node(node)

        graph.add_subgraph(subgraph)

    # Add dependencies between components
    for file_path, data in index_data.items():
        # Skip files with no class information
        if not data.get("classes"):
            continue

        source_package = data.get("package", "default")
        source_class = data.get("classes")[0] if data.get("classes") else os.path.basename(file_path).replace(".java", "")
        source_id = f"{source_package}.{source_class}"

        # Process dependencies
        for dep in data.get("dependencies", []):
            if "." in dep:
                target_parts = dep.split(".")
                target_class = target_parts[-1]
                target_package = ".".join(target_parts[:-1])
                target_id = f"{target_package}.{target_class}"

                # Check if both source and target components exist
                if source_id in components and target_id in components:
                    edge = pydot.Edge(
                        source_id,
                        target_id,
                        style="solid",
                        color=DIAGRAM_COLORS["edge"],
                        fontsize=10,
                        fontname="Arial",
                        fontcolor=DIAGRAM_COLORS["edge"],
                        label="uses",
                    )
                    graph.add_edge(edge)

    try:
        graph.write_png(diagram_file)
        logging.info(f"C4 Component Diagram saved as {diagram_file}")
    except Exception as e:
        logging.error(f"Failed to generate C4 diagram: {e}")

def generate_context_diagram():
    diagram_file = os.path.join(INDEX_DIR, "context_diagram.png")
    generate_diagram_from_index(
        "Context Diagram",
        diagram_file,
        lambda data: data.get("package", "default"),
        lambda data: data.get("classes", []),
        lambda data: [
            ".".join(dep.split(".")[:-1])
            for dep in data.get("dependencies", [])
        ],
    )

def generate_component_diagram():
    """
    Generates a component diagram based on the code index.
    Shows components (classes) and their relationships.
    """
    logging.info("Starting component diagram generation.")
    
    diagram_file = os.path.join(INDEX_DIR, "component_diagram.png")
    index_data = load_from_file(INDEX_JSON)
    if not index_data:
        logging.warning("No data found in index.json. Skipping component diagram generation.")
        return

    graph = pydot.Dot(
        graph_type="digraph",
        bgcolor=DIAGRAM_COLORS["default_bg"],
        label="Component Diagram",
        fontsize=24,
        labelloc="t",
        rankdir="TB",
        fontname="Arial",
        concentrate="true",  # Reduce edge crossings
    )

    # Define excluded dependency patterns
    excluded_patterns = [
        "java.", "javax.", "org.springframework", "junit", 
        "org.junit", "org.assertj", "org.mockito", "org.slf4j", 
        "lombok", "android.", "com.google.common"
    ]
    
    # Process all components first
    packages = {}
    components = {}
    
    for file_path, data in index_data.items():
        # Extract the package name
        package_name = data.get("package", "")
        if not package_name:
            package_name = "default"
            
        # Create package entry if not exists
        if package_name not in packages:
            packages[package_name] = {
                "files": [],
                "classes": [],
                "dependencies": set(),
            }
            
        # Add file to package
        packages[package_name]["files"].append(file_path)
        
        # Add classes to package
        for class_name in data.get("classes", []):
            if class_name not in packages[package_name]["classes"]:
                packages[package_name]["classes"].append(class_name)
            
        # Process dependencies
        for dep in data.get("dependencies", []):
            # Skip excluded dependencies
            if any(dep.startswith(pattern) for pattern in excluded_patterns):
                continue
                
            # Add dependency to package
            if dep and dep != package_name:
                packages[package_name]["dependencies"].add(dep)

    # Create subgraphs for packages
    for package_name, package_data in packages.items():
        # Skip empty packages
        if not package_data["classes"]:
            continue
            
        # Create subgraph for package
        package_id = f"cluster_{package_name.replace('.', '_')}"
        subgraph = pydot.Cluster(
            package_id,
            label=f"Package: {package_name}",
            style="filled",
            fillcolor=DIAGRAM_COLORS["package_bg"],
            color="black",
            fontsize=16,
            fontname="Arial",
            margin="20",
        )
        
        # Add class nodes to package
        for class_name in package_data["classes"]:
            # Create a unique ID for the component
            component_id = f"{package_name}.{class_name}"
            # Register component for dependency mapping
            components[component_id] = class_name
            
            # Create component node with proper styling
            node = pydot.Node(
                component_id,
                label=f"[Component]\n{class_name}",
                shape="box",
                style="filled,rounded",  # Use rounded boxes for components
                fillcolor=DIAGRAM_COLORS["component_bg"],
                fontname="Arial",
                margin="0.3,0.1",
                height=0.8,
                width=1.6,
            )
            subgraph.add_node(node)
            
        # Add subgraph to main graph
        graph.add_subgraph(subgraph)
    
    # Process and add dependencies between components
    edge_set = set()  # Track unique edges
    
    for file_path, data in index_data.items():
        # Skip files with no classes
        if not data.get("classes"):
            continue
            
        source_package = data.get("package", "default")
        
        # Process each class in the file
        for source_class in data.get("classes", []):
            source_id = f"{source_package}.{source_class}"
            
            # Process dependencies
            for dep in data.get("dependencies", []):
                # Skip excluded dependencies
                if any(dep.startswith(pattern) for pattern in excluded_patterns):
                    continue
                    
                # Process qualified dependencies (with package)
                if "." in dep:
                    target_parts = dep.split(".")
                    target_class = target_parts[-1]
                    target_package = ".".join(target_parts[:-1])
                    target_id = f"{target_package}.{target_class}"
                else:
                    # Unqualified dependencies (likely in same package)
                    target_class = dep
                    target_package = source_package
                    target_id = f"{target_package}.{target_class}"
                
                # Create edge if both components exist and not self-referential
                if (source_id in components and target_id in components and 
                    source_id != target_id and 
                    (source_id, target_id) not in edge_set):
                    
                    edge = pydot.Edge(
                        source_id,
                        target_id,
                        style="solid",
                        color=DIAGRAM_COLORS["edge"],
                        fontsize=10,
                        fontname="Arial",
                        fontcolor=DIAGRAM_COLORS["edge"],
                        label="uses",
                        arrowhead="vee",  # Better arrow style
                    )
                    graph.add_edge(edge)
                    edge_set.add((source_id, target_id))
    
    try:
        graph.write_png(diagram_file)
        logging.info(f"Component diagram saved as {diagram_file}")
    except Exception as e:
        logging.error(f"Failed to generate component diagram: {e}")

def generate_container_diagram():
    diagram_file = os.path.join(INDEX_DIR, "container_diagram.png")
    index_data = load_from_file(INDEX_JSON)
    if not index_data:
        logging.warning("No data found in index.json. Skipping container diagram generation.")
        return

    graph = pydot.Dot(
        graph_type="digraph",
        bgcolor=DIAGRAM_COLORS["default_bg"],
        label="Container Diagram",
        fontsize=24,
        labelloc="t",
        rankdir="TB",
        fontname="Arial",
    )

    # Define containers based on the index data
    containers = {}
    for file_path, data in index_data.items():
        package_name = data.get("package", "default")
        if package_name not in containers:
            containers[package_name] = {
                "label": f"{package_name} (Package)",
                "shape": "box",
                "style": "filled",
                "fillcolor": DIAGRAM_COLORS["component_bg"],
                "fontname": "Arial",
            }

    # Add container nodes to the graph
    for container_id, details in containers.items():
        node = pydot.Node(container_id, **details)
        graph.add_node(node)

    # Add edges between containers based on dependencies
    edges = set()
    excluded_dependencies = ["org.springframework", "junit", "org.junit", "org.assertj"]
    for file_path, data in index_data.items():
        source_package = data.get("package", "default")
        for dep in data.get("dependencies", []):
            if any(dep.startswith(excluded) for excluded in excluded_dependencies):
                continue
            if "." in dep:
                target_package = ".".join(dep.split(".")[:-1])
                if target_package and target_package != source_package:
                    edges.add((source_package, target_package))

    for source, target in edges:
        edge = pydot.Edge(
            source,
            target,
            label="depends on",
            fontname="Arial",
            fontsize=10,
            color=DIAGRAM_COLORS["edge"],
            fontcolor=DIAGRAM_COLORS["edge"],
        )
        graph.add_edge(edge)

    try:
        graph.write_png(diagram_file)
        logging.info(f"Container diagram saved as {diagram_file}")
    except Exception as e:
        logging.error(f"Failed to generate container diagram: {e}")

def generate_sequence_diagram():
    """
    Generates a clean, simplified sequence diagram showing key interactions between components.
    Removes duplicates, filters unwanted relationships, and focuses on essential information.
    """
    logging.info("Starting sequence diagram generation.")

    index_data = load_from_file(INDEX_JSON)
    if not index_data:
        logging.warning("No data found in index.json. Skipping sequence diagram generation.")
        return

    diagram_file = os.path.join(INDEX_DIR, "sequence_diagram.png")
    
    # Create a new directed graph with improved styling
    graph = pydot.Dot(
        graph_type="digraph", 
        rankdir="LR",  # Left to right layout for sequence flow
        bgcolor="white",
        fontname="Helvetica",
        label="Application Sequence Flow",
        labelloc="t",
        labeljust="c",
        fontsize=22,
        fontcolor="#333333",
        nodesep=0.8,  # Increase space between nodes
        ranksep=1.2,  # Increase space between ranks
    )

    # Define patterns to exclude from the diagram
    excluded_patterns = [
        "java.", "javax.", "org.springframework", "junit", 
        "org.junit", "org.assertj", "org.mockito", "org.slf4j", 
        "lombok", "android.", "com.google.common"
    ]
    
    # Define utility/common methods to filter out
    utility_methods = {
        "save", "print", "ifPresent", "orElse", "forEach", "map", 
        "equals", "toString", "hashCode", "get", "set", "is", 
        "build", "of", "from", "clone", "compareTo", "builder",
        "add", "remove", "clear", "put", "create", "find"
    }
    
    # Track participants and unique relationships
    participants = set()
    unique_relationships = set()
    calls_by_relation = {}
    
    # First pass: identify significant calls and participants
    for file_data in index_data.values():
        for call in file_data.get("call_graph", []):
            caller_class = call.get("caller_class", "")
            callee_class = call.get("callee_class", "")
            caller_method = call.get("caller_method", "")
            callee_method = call.get("callee_method", "")
            
            # Skip if missing essential information
            if not (caller_class and callee_class and caller_method and callee_method):
                continue
                
            # Skip standard library and utility method calls
            if (any(caller_class.startswith(pattern) for pattern in excluded_patterns) or
                any(callee_class.startswith(pattern) for pattern in excluded_patterns) or
                callee_method.lower() in utility_methods or
                caller_method.lower() in utility_methods):
                continue
            
            # Skip self-references to getter/setter/common methods
            if (caller_class == callee_class and 
                (callee_method.startswith(("get", "set", "is")) or 
                 callee_method in utility_methods)):
                continue
                
            # Create a unique relationship identifier
            relation = (caller_class, callee_class)
            
            # Add participants
            participants.add(caller_class)
            participants.add(callee_class)
            
            # Track the relationship
            if relation not in calls_by_relation:
                calls_by_relation[relation] = []
                
            # Add the method call
            calls_by_relation[relation].append({
                "caller_method": caller_method,
                "callee_method": callee_method
            })
    
    # Create participant nodes with better styling
    for participant in sorted(participants):
        # Extract simple name for display
        simple_name = participant.split(".")[-1]
        
        node = pydot.Node(
            participant,
            label=f"{simple_name}",
            shape="box",
            style="filled,rounded",  # Use rounded boxes
            fillcolor="#E8F4F9",  # Light blue
            color="#4682B4",  # Steel blue border
            fontname="Helvetica",
            fontcolor="#333333",
            height=0.7,
            width=2.0,
            penwidth=1.5,
        )
        graph.add_node(node)
    
    # Add edges with meaningful labels
    for (caller, callee), calls in calls_by_relation.items():
        if caller == callee:
            # Skip self-references as they clutter the diagram
            continue
            
        # Limit to 3 most important method calls
        important_calls = calls[:min(3, len(calls))]
        
        # Create a concise label showing the methods
        if len(important_calls) == 1:
            label = important_calls[0]["caller_method"] + " -> " + important_calls[0]["callee_method"]
        else:
            label = f"{len(calls)} calls"
            
        edge = pydot.Edge(
            caller,
            callee,
            label=label,
            fontname="Helvetica",
            fontsize=10,
            fontcolor="#555555",
            color="#4682B4",  # Steel blue
            penwidth=1.2,
            style="solid",
            arrowhead="vee",  # Better arrow style
        )
        graph.add_edge(edge)

    try:
        graph.write_png(diagram_file)
        logging.info(f"Simplified sequence diagram saved as {diagram_file}")
    except Exception as e:
        logging.error(f"Failed to generate sequence diagram: {e}")

def is_standard_library_call(call):
    """Checks if the method call is to a standard Java library class."""
    return call["callee_class"].startswith("java.")


def is_utility_method(call):
    """Checks if the method call is to a specific utility method (customize as needed)."""
    utility_methods = {"save", "print", "ifPresent", "orElse", "forEach", "map", "equals", "toString"}
    return call["callee_method"] in utility_methods
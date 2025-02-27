import os
import json
import logging
import pydot
from utils.config_utils import load_from_file

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DIAGRAM_COLORS = {
    "default_bg": "white",
    "class_bg": "#F5F5F5",
    "abstract_class_bg": "#F5EEF8",
    "interface_bg": "#E8F8F5",
    "inheritance_edge": "#333333",
    "composition_edge": "#E74C3C",
    "aggregation_edge": "#F39C12",
    "association_edge": "#3498DB",
}

def generate_class_diagram(index_dir, index_json):
    """
    Generates a comprehensive class diagram showing classes, their attributes, methods,
    and relationships.
    
    Args:
        index_dir (str): Directory to store the generated diagram.
        index_json (str): Path to the index JSON file containing code information.
    """
    logging.info("Starting class diagram generation.")

    index_data = load_from_file(index_json)
    if not index_data:
        logging.warning("No data found in index JSON. Skipping class diagram generation.")
        return

    diagram_file = os.path.join(index_dir, "class_diagram.png")
    
    # Create a new graph with improved styling for class diagrams
    graph = pydot.Dot(
        graph_type="digraph",
        bgcolor=DIAGRAM_COLORS["default_bg"],
        label="Class Diagram",
        fontsize=24,
        labelloc="t",
        rankdir="TB",  # Top to bottom layout for class hierarchies
        fontname="Arial",
        nodesep=0.6,
        ranksep=1.2,
        splines="ortho",  # Use orthogonal lines for cleaner appearance
    )
    
    # Track classes to avoid duplicates
    processed_classes = set()
    
    # Track relationships to avoid duplicates
    relationships = {
        "inheritance": set(),
        "composition": set(),
        "aggregation": set(),
        "association": set(),
    }
    
    # Define patterns to exclude from the diagram
    excluded_patterns = [
        "java.", "javax.", "org.springframework", 
        "junit", "org.junit", "org.assertj", "org.mockito", 
        "org.slf4j", "lombok", "android.", "com.google.common"
    ]
    
    # First pass: Create class nodes with attributes and methods
    for file_path, data in index_data.items():
        package_name = data.get("package", "")
        
        for class_info in data.get("classes", []):
            class_name = class_info
            
            # Skip if class name is empty
            if not class_name:
                continue
                
            # Create full class identifier
            if package_name:
                full_class_name = f"{package_name}.{class_name}"
            else:
                full_class_name = class_name
                
            # Skip if already processed or matches excluded patterns
            if (full_class_name in processed_classes or 
                any(full_class_name.startswith(pattern) for pattern in excluded_patterns)):
                continue
                
            processed_classes.add(full_class_name)
            
            # Build UML-style class representation
            attributes = []  # Placeholder for attributes
            methods = []  # Placeholder for methods
            is_interface = False  # Placeholder for interface check
            is_abstract = False  # Placeholder for abstract class check
            
            # Format class label in UML style
            label_parts = []
            
            # Add class name with stereotype if needed
            if is_interface:
                label_parts.append(f"<<interface>>\\n{class_name}")
            elif is_abstract:
                label_parts.append(f"<<abstract>>\\n{class_name}")
            else:
                label_parts.append(class_name)
                
            # Add separator
            label_parts.append("\\l─────────────────\\l")
            
            # Add attributes (limited to 7 max)
            if attributes:
                for i, attr in enumerate(attributes[:7]):
                    visibility = "public"  # Placeholder for visibility
                    name = attr
                    type_name = "String"  # Placeholder for type
                    
                    # Format visibility symbol
                    if visibility == "private":
                        vis_symbol = "-"
                    elif visibility == "protected":
                        vis_symbol = "#"
                    elif visibility == "public":
                        vis_symbol = "+"
                    else:
                        vis_symbol = "~"  # package private
                        
                    attr_str = f"{vis_symbol} {name}: {type_name}\\l"
                    label_parts.append(attr_str)
                    
                if len(attributes) > 7:
                    label_parts.append("...\\l")
            
            # Add separator before methods
            label_parts.append("─────────────────\\l")
            
            # Add methods (limited to 10 max)
            if methods:
                for i, method in enumerate(methods[:10]):
                    visibility = "public"  # Placeholder for visibility
                    name = method
                    return_type = "void"  # Placeholder for return type
                    
                    # Format visibility symbol
                    if visibility == "private":
                        vis_symbol = "-"
                    elif visibility == "protected":
                        vis_symbol = "#"
                    elif visibility == "public":
                        vis_symbol = "+"
                    else:
                        vis_symbol = "~"  # package private
                        
                    # Simplify parameter display to avoid overflow
                    params_count = 0  # Placeholder for parameter count
                    if params_count > 0:
                        params_str = f"({params_count} params)"
                    else:
                        params_str = "()"
                        
                    method_str = f"{vis_symbol} {name}{params_str}: {return_type}\\l"
                    label_parts.append(method_str)
                    
                if len(methods) > 10:
                    label_parts.append("...\\l")
            
            # Create node with HTML-like label
            node_label = "\\l".join(label_parts)
            
            # Determine node style based on class type
            if is_interface:
                fill_color = DIAGRAM_COLORS["interface_bg"]
                border_color = "#16A085"
            elif is_abstract:
                fill_color = DIAGRAM_COLORS["abstract_class_bg"]
                border_color = "#8E44AD"
            else:
                fill_color = DIAGRAM_COLORS["class_bg"]
                border_color = "#34495E"
            
            # Create node
            node = pydot.Node(
                full_class_name,
                label=node_label,
                shape="record",
                style="filled",
                fillcolor=fill_color,
                color=border_color,
                fontname="Arial",
                fontsize=10,
                margin="0.3,0.1",
                height=0.1,  # Allow height to be determined by content
                width=3.5,
                penwidth=1.5,
            )
            
            graph.add_node(node)
            
            # Track inheritance relationships
            parent_class = ""  # Placeholder for parent class
            if parent_class and parent_class not in ("Object", "java.lang.Object"):
                # If parent class doesn't include package, add current package
                if "." not in parent_class and package_name:
                    parent_class = f"{package_name}.{parent_class}"
                    
                relationships["inheritance"].add((full_class_name, parent_class))
                
            # Track interface implementations
            for interface in []:  # Placeholder for implemented interfaces
                # If interface doesn't include package, add current package
                if "." not in interface and package_name:
                    interface = f"{package_name}.{interface}"
                    
                relationships["inheritance"].add((full_class_name, interface))
    
    # Second pass: Add dependency relationships based on field types and method parameters
    for file_path, data in index_data.items():
        package_name = data.get("package", "")
        
        for class_info in data.get("classes", []):
            class_name = class_info
            
            # Skip if class name is empty
            if not class_name:
                continue
                
            # Create full class identifier
            if package_name:
                full_class_name = f"{package_name}.{class_name}"
            else:
                full_class_name = class_name
                
            # Skip excluded classes
            if any(full_class_name.startswith(pattern) for pattern in excluded_patterns):
                continue
                
            # Process field relationships
            for attr in []:  # Placeholder for attributes
                attr_type = "String"  # Placeholder for attribute type
                
                # Skip primitive types and excluded types
                if (not attr_type or 
                    attr_type in ("int", "long", "boolean", "String", "double", "float") or
                    any(attr_type.startswith(pattern) for pattern in excluded_patterns)):
                    continue
                    
                # If type doesn't include package, add current package
                if "." not in attr_type and package_name:
                    attr_type = f"{package_name}.{attr_type}"
                    
                # Check if this is a collection type
                is_collection = False
                collection_type = None
                
                if attr_type.startswith(("List<", "Set<", "Map<", "Collection<")):
                    is_collection = True
                    collection_match = re.search(r'<([^>]+)>', attr_type)
                    if collection_match:
                        collection_type = collection_match.group(1)
                        # If collection type doesn't include package, add current package
                        if "." not in collection_type and package_name:
                            collection_type = f"{package_name}.{collection_type}"
                
                if is_collection and collection_type:
                    # This is an aggregation (collection of objects)
                    if (full_class_name != collection_type and 
                        collection_type not in ("String", "Integer", "Long", "Boolean")):
                        relationships["aggregation"].add((full_class_name, collection_type))
                elif attr_type.endswith("[]"):
                    # This is an array, which is also an aggregation
                    base_type = attr_type[:-2]
                    if "." not in base_type and package_name:
                        base_type = f"{package_name}.{base_type}"
                    if (full_class_name != base_type and 
                        base_type not in ("String", "Integer", "Long", "Boolean")):
                        relationships["aggregation"].add((full_class_name, base_type))
                else:
                    # This might be a composition or association
                    # Check if the field is final to determine composition vs association
                    is_final = False  # Placeholder for final check
                    
                    if is_final:
                        # Composition (strong ownership)
                        if full_class_name != attr_type:
                            relationships["composition"].add((full_class_name, attr_type))
                    else:
                        # Association (weak relationship)
                        if full_class_name != attr_type:
                            relationships["association"].add((full_class_name, attr_type))
    
    # Add relationships to graph
    # 1. Inheritance relationships
    for source, target in relationships["inheritance"]:
        if source in processed_classes and target in processed_classes:
            edge = pydot.Edge(
                source,
                target,
                arrowhead="onormal",  # Triangle arrow for inheritance
                style="solid",
                color=DIAGRAM_COLORS["inheritance_edge"],
                penwidth=1.5,
            )
            graph.add_edge(edge)
    
    # 2. Composition relationships
    for source, target in relationships["composition"]:
        if source in processed_classes and target in processed_classes:
            edge = pydot.Edge(
                source,
                target,
                arrowhead="diamond",  # Filled diamond for composition
                style="solid",
                color=DIAGRAM_COLORS["composition_edge"],
                penwidth=1.5,
            )
            graph.add_edge(edge)
    
    # 3. Aggregation relationships
    for source, target in relationships["aggregation"]:
        if source in processed_classes and target in processed_classes:
            edge = pydot.Edge(
                source,
                target,
                arrowhead="odiamond",  # Open diamond for aggregation
                style="solid",
                color=DIAGRAM_COLORS["aggregation_edge"],
                penwidth=1.5,
            )
            graph.add_edge(edge)
    
    # 4. Association relationships (limit to keep diagram readable)
    association_count = 0
    max_associations = 30  # Limit the number of associations to prevent cluttering
    
    for source, target in relationships["association"]:
        if association_count >= max_associations:
            break
            
        if source in processed_classes and target in processed_classes:
            edge = pydot.Edge(
                source,
                target,
                arrowhead="vee",  # Standard arrow for association
                style="dashed",  # Dashed line for association
                color=DIAGRAM_COLORS["association_edge"],
                penwidth=1.2,
            )
            graph.add_edge(edge)
            association_count += 1
    
    # Add legend
    legend_label = (
        '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\n'
        '<TR><TD COLSPAN="2"><B>Legend</B></TD></TR>\n'
        '<TR><TD BGCOLOR="#F5F5F5">Class</TD><TD>Regular class</TD></TR>\n'
        '<TR><TD BGCOLOR="#F5EEF8">Abstract</TD><TD>Abstract class</TD></TR>\n'
        '<TR><TD BGCOLOR="#E8F8F5">Interface</TD><TD>Interface</TD></TR>\n'
        '<TR><TD><FONT COLOR="#333333">→|></FONT></TD><TD>Inheritance/Implementation</TD></TR>\n'
        '<TR><TD><FONT COLOR="#E74C3C">→♦</FONT></TD><TD>Composition</TD></TR>\n'
        '<TR><TD><FONT COLOR="#F39C12">→◊</FONT></TD><TD>Aggregation</TD></TR>\n'
        '<TR><TD><FONT COLOR="#3498DB">- - ></FONT></TD><TD>Association</TD></TR>\n'
        '</TABLE>>'
    )
    
    legend = pydot.Node(
        "legend",
        label=legend_label,
        shape="none",
        fontsize=10,
        fontname="Arial",
    )
    
    graph.add_node(legend)

    try:
        graph.write_png(diagram_file, encoding="utf-8")
        logging.info(f"Class diagram saved as {diagram_file}")
    except Exception as e:
        logging.error(f"Failed to generate class diagram: {e}")
        
# Add helper function for parsing type information
import re
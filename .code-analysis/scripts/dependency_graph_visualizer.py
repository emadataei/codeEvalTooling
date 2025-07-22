"""
Dependency Graph Generator with Visual Output
Generates both PNG images and interactive HTML graphs
"""

import os
import json
import subprocess
from pathlib import Path

# File extension constants
PY_EXT = '.py'
JS_EXT = '.js'
TS_EXT = '.ts'
TSX_EXT = '.tsx'
JSX_EXT = '.jsx'
CSS_EXT = '.css'
SCSS_EXT = '.scss'
HTML_EXT = '.html'
JSON_EXT = '.json'
YML_EXT = '.yml'
YAML_EXT = '.yaml'
MD_EXT = '.md'

# Sample file paths
UTILS_PATH = "src/utils.py"
MAIN_PATH = "src/main.py"

def generate_dependency_graph_image(dependencies, output_dir='.'):
    """
    Generate visual dependency graph as PNG image using Graphviz
    
    Args:
        dependencies: Dict of file -> [dependencies] mapping
        output_dir: Directory to save the graph image
    
    Returns:
        Path to generated PNG file
    """
    try:
        # Create DOT format graph
        dot_content = create_dot_graph(dependencies)
        
        # Write DOT file
        dot_file = os.path.join(output_dir, 'dependency_graph.dot')
        with open(dot_file, 'w') as f:
            f.write(dot_content)
        
        # Generate PNG using Graphviz
        png_file = os.path.join(output_dir, 'dependency_graph.png')
        result = subprocess.run([
            'dot', '-Tpng', dot_file, '-o', png_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Dependency graph generated: {png_file}")
            # Clean up DOT file
            os.remove(dot_file)
            return png_file
        else:
            print(f"Graphviz error: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("Graphviz not found. Install with: apt-get install graphviz or brew install graphviz")
        return generate_ascii_graph(dependencies, output_dir)
    except Exception as e:
        print(f"Error generating graph: {e}")
        return None

def create_dot_graph(dependencies):
    """Create DOT format graph content"""
    dot_lines = [
        'digraph DependencyGraph {',
        '    rankdir=TB;',
        '    node [shape=box, style=filled];',
        '    edge [color=gray];',
        ''
    ]
    
    # Add nodes with colors based on file type and impact
    all_files = set()
    for file_path, deps in dependencies.items():
        all_files.add(file_path)
        all_files.update(deps)
    
    for file_path in all_files:
        color = get_node_color(file_path)
        shape = get_node_shape(file_path)
        label = get_node_label(file_path)
        
        dot_lines.append(f'    "{file_path}" [label="{label}", fillcolor="{color}", shape="{shape}"];')
    
    dot_lines.append('')
    
    # Add edges for dependencies
    for file_path, deps in dependencies.items():
        for dep in deps:
            if dep in all_files:  # Only add edges to known files
                dot_lines.append(f'    "{file_path}" -> "{dep}";')
    
    dot_lines.append('}')
    return '\n'.join(dot_lines)

def get_node_color(file_path):
    """Determine node color based on file type"""
    ext = Path(file_path).suffix.lower()
    
    color_map = {
        PY_EXT: 'lightblue',
        JS_EXT: 'lightgreen', 
        TS_EXT: 'lightgreen',
        TSX_EXT: 'lightgreen',
        JSX_EXT: 'lightgreen',
        CSS_EXT: 'lightyellow',
        SCSS_EXT: 'lightyellow',
        HTML_EXT: 'lightcoral',
        JSON_EXT: 'lightgray',
        YML_EXT: 'lightgray',
        YAML_EXT: 'lightgray',
        MD_EXT: 'white'
    }
    
    return color_map.get(ext, 'lightsteelblue')

def get_node_shape(file_path):
    """Determine node shape based on file type"""
    ext = Path(file_path).suffix.lower()
    
    if ext in [PY_EXT]:
        return 'ellipse'
    elif ext in [JS_EXT, TS_EXT, TSX_EXT, JSX_EXT]:
        return 'box'
    elif ext in [CSS_EXT, SCSS_EXT]:
        return 'diamond'
    else:
        return 'box'

def get_node_label(file_path):
    """Create readable label for node"""
    # Use just the filename for cleaner display
    return Path(file_path).name

def generate_ascii_graph(dependencies, output_dir='.'):
    """Fallback ASCII graph when Graphviz is not available"""
    output_file = os.path.join(output_dir, 'dependency_graph.txt')
    
    with open(output_file, 'w') as f:
        f.write("Dependency Graph (ASCII)\n")
        f.write("=" * 40 + "\n\n")
        
        for file_path, deps in dependencies.items():
            file_name = Path(file_path).name
            f.write(f"{file_name}\n")
            
            for i, dep in enumerate(deps):
                dep_name = Path(dep).name
                if i == len(deps) - 1:
                    f.write(f"  └── {dep_name}\n")
                else:
                    f.write(f"  ├── {dep_name}\n")
            f.write("\n")
    
    print(f"ASCII dependency graph generated: {output_file}")
    return output_file

def generate_interactive_graph(dependencies, output_dir='.'):
    """Generate interactive HTML graph using D3.js"""
    html_content = create_d3_graph_html(dependencies)
    
    html_file = os.path.join(output_dir, 'dependency_graph.html')
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"Interactive dependency graph generated: {html_file}")
    return html_file

def create_d3_graph_html(dependencies):
    """Create HTML content with D3.js force-directed graph"""
    
    # Convert dependencies to D3.js format
    nodes = []
    links = []
    node_ids = {}
    
    # Create nodes
    all_files = set()
    for file_path, deps in dependencies.items():
        all_files.add(file_path)
        all_files.update(deps)
    
    for i, file_path in enumerate(all_files):
        node_ids[file_path] = i
        nodes.append({
            'id': i,
            'name': Path(file_path).name,
            'fullPath': file_path,
            'group': get_file_group(file_path)
        })
    
    # Create links
    for file_path, deps in dependencies.items():
        if file_path in node_ids:
            for dep in deps:
                if dep in node_ids:
                    links.append({
                        'source': node_ids[file_path],
                        'target': node_ids[dep]
                    })
    
    nodes_json = json.dumps(nodes)
    links_json = json.dumps(links)
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Dependency Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .links line {{ stroke: #999; stroke-opacity: 0.6; stroke-width: 1px; }}
        .nodes circle {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
        .nodes text {{ font-size: 10px; pointer-events: none; }}
        .tooltip {{ position: absolute; padding: 8px; background: rgba(0,0,0,0.8); 
                   color: white; border-radius: 4px; font-size: 12px; }}
        #controls {{ margin-bottom: 10px; }}
        button {{ margin-right: 10px; padding: 5px 10px; }}
    </style>
</head>
<body>
    <h2>Dependency Graph</h2>
    <div id="controls">
        <button onclick="restart()">Reset Layout</button>
        <button onclick="toggleLabels()">Toggle Labels</button>
    </div>
    <svg width="1000" height="600"></svg>
    
    <script>
        const nodes = {nodes_json};
        const links = {links_json};
        
        const svg = d3.select("svg");
        const width = +svg.attr("width");
        const height = +svg.attr("height");
        
        const color = d3.scaleOrdinal(d3.schemeCategory10);
        
        let showLabels = true;
        
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(50))
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links)
            .enter().append("line");
        
        const node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes)
            .enter().append("g")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("r", 8)
            .attr("fill", d => color(d.group))
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);
        
        const labels = node.append("text")
            .text(d => d.name)
            .attr("dx", 12)
            .attr("dy", 4);
        
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        function showTooltip(event, d) {{
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`<strong>${{d.name}}</strong><br/>${{d.fullPath}}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        }}
        
        function hideTooltip() {{
            tooltip.transition().duration(500).style("opacity", 0);
        }}
        
        function restart() {{
            simulation.alpha(1).restart();
        }}
        
        function toggleLabels() {{
            showLabels = !showLabels;
            labels.style("display", showLabels ? "block" : "none");
        }}
    </script>
</body>
</html>
"""

def get_file_group(file_path):
    """Group files by type for coloring"""
    ext = Path(file_path).suffix.lower()
    
    if ext == PY_EXT:
        return 1
    elif ext in [JS_EXT, TS_EXT, TSX_EXT, JSX_EXT]:
        return 2
    elif ext in [CSS_EXT, SCSS_EXT]:
        return 3
    elif ext in [HTML_EXT]:
        return 4
    elif ext in [JSON_EXT, YML_EXT, YAML_EXT]:
        return 5
    else:
        return 0

if __name__ == "__main__":
    # Example usage
    sample_deps = {
        MAIN_PATH: [UTILS_PATH, "src/models/user.py"],
        UTILS_PATH: ["src/config.py"],
        "src/models/user.py": [UTILS_PATH],
        "src/app.js": [MAIN_PATH],
        "src/styles.css": []
    }
    
    # Generate both image and interactive graph
    generate_dependency_graph_image(sample_deps)
    generate_interactive_graph(sample_deps)

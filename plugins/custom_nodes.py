#!/usr/bin/env python3
"""AAS-305: Custom Node Creation"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable


@dataclass
class NodeInput:
    """Input port definition"""

    name: str
    type_name: str
    default: Any = None


@dataclass
class NodeOutput:
    """Output port definition"""

    name: str
    type_name: str


class CustomNode:
    """Base class for custom nodes"""

    def __init__(self, node_id: str, title: str):
        """Initialize custom node"""
        self.node_id = node_id
        self.title = title
        self.inputs: Dict[str, NodeInput] = {}
        self.outputs: Dict[str, NodeOutput] = {}
        self.metadata: Dict[str, Any] = {}
        self.is_executable = False

    def add_input(self, name: str, type_name: str, default: Any = None) -> None:
        """Add input port"""
        self.inputs[name] = NodeInput(name, type_name, default)

    def add_output(self, name: str, type_name: str) -> None:
        """Add output port"""
        self.outputs[name] = NodeOutput(name, type_name)

    def get_input(self, name: str) -> Optional[NodeInput]:
        """Get input by name"""
        return self.inputs.get(name)

    def get_output(self, name: str) -> Optional[NodeOutput]:
        """Get output by name"""
        return self.outputs.get(name)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata"""
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Any:
        """Get metadata"""
        return self.metadata.get(key)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize node to dict"""
        return {
            "id": self.node_id,
            "title": self.title,
            "inputs": {
                name: {"type": inp.type_name, "default": inp.default}
                for name, inp in self.inputs.items()
            },
            "outputs": {
                name: {"type": out.type_name} for name, out in self.outputs.items()
            },
            "metadata": self.metadata,
        }


class NodeFactory:
    """Factory for creating custom nodes"""

    def __init__(self):
        """Initialize factory"""
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.created_nodes: List[CustomNode] = []

    def register_template(self, name: str, definition: Dict[str, Any]) -> None:
        """Register node template"""
        self.templates[name] = definition

    def create_from_template(
        self, template_name: str, node_id: str
    ) -> Optional[CustomNode]:
        """Create node from template"""
        if template_name not in self.templates:
            return None

        template = self.templates[template_name]
        node = CustomNode(node_id, template.get("title", ""))

        for inp in template.get("inputs", []):
            node.add_input(inp["name"], inp.get("type", "any"), inp.get("default"))

        for out in template.get("outputs", []):
            node.add_output(out["name"], out.get("type", "any"))

        self.created_nodes.append(node)
        return node

    def create_blank(self, node_id: str, title: str) -> CustomNode:
        """Create blank node"""
        node = CustomNode(node_id, title)
        self.created_nodes.append(node)
        return node

    def list_templates(self) -> List[str]:
        """List all templates"""
        return list(self.templates.keys())

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get template definition"""
        return self.templates.get(name)


class NodeGraph:
    """Graph of connected nodes"""

    def __init__(self):
        """Initialize node graph"""
        self.nodes: Dict[str, CustomNode] = {}
        self.connections: List[tuple] = []

    def add_node(self, node: CustomNode) -> None:
        """Add node to graph"""
        self.nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> bool:
        """Remove node from graph"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            return True
        return False

    def connect(
        self, from_node: str, from_output: str, to_node: str, to_input: str
    ) -> bool:
        """Connect nodes"""
        if from_node in self.nodes and to_node in self.nodes:
            connection = (from_node, from_output, to_node, to_input)
            self.connections.append(connection)
            return True
        return False

    def get_connections(self, node_id: str) -> List[tuple]:
        """Get connections for a node"""
        return [c for c in self.connections if c[0] == node_id or c[2] == node_id]

    def get_node(self, node_id: str) -> Optional[CustomNode]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def list_nodes(self) -> List[CustomNode]:
        """List all nodes"""
        return list(self.nodes.values())

    def validate(self) -> Dict[str, Any]:
        """Validate graph structure"""
        issues = []
        for conn in self.connections:
            from_node, from_output, to_node, to_input = conn
            if from_node not in self.nodes:
                issues.append(f"Missing source node: {from_node}")
            elif from_output not in self.nodes[from_node].outputs:
                issues.append(f"Missing output: {from_node}.{from_output}")
            if to_node not in self.nodes:
                issues.append(f"Missing target node: {to_node}")
            elif to_input not in self.nodes[to_node].inputs:
                issues.append(f"Missing input: {to_node}.{to_input}")

        return {"valid": len(issues) == 0, "issues": issues}

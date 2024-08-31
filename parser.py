import json
from collections import defaultdict
from typing import Dict, Any, Tuple
from functools import lru_cache


def parse_workflows_to_atoms(input_json: Dict[str, Any]) -> Dict[str, Any]:
    def nested_dict():
        return defaultdict(nested_dict)

    atoms = nested_dict()
    workflows = input_json["workflows"]

    for workflow_id, workflow_data in workflows.items():
        element_id = workflow_data['properties']['element_id']
        atom_logic = atoms[element_id]['logic']
        atom_logic[workflow_id]['nodes'] = {}
        atom_logic[workflow_id]['connections'] = {}

        add_node(atom_logic[workflow_id]['nodes'], workflow_data['id'], workflow_data['type'])
        for action_id, action_data in workflow_data['actions'].items():
            add_node(atom_logic[workflow_id]['nodes'], action_data['id'], action_data['type'], action_data['properties'])
            add_connection(atom_logic[workflow_id]['connections'], workflow_data['id'], action_data['id'], int(action_id))

    return {'atoms': convert_defaultdict_to_dict(atoms)}


def dict_to_frozenset(d: Dict[str, Any]) -> frozenset:
    """Convert a dictionary to a frozenset of its items for hashing."""
    return frozenset((k, tuple(v.items()) if isinstance(v, dict) else v) for k, v in d.items())


@lru_cache(maxsize=None)
def create_node(uid: str, node_type: str, parameters: Tuple = None) -> Dict[str, Any]:
    """Create and return a node dictionary. Cached to avoid recreating nodes with the same UID and type."""
    node = {'uid': uid, 'type': node_type}
    if parameters:
        node['parameters'] = dict(parameters)
    return node


def add_node(nodes: Dict[str, Any], uid: str, node_type: str, parameters: Dict[str, Any] = None):
    """Helper function to add a node to the nodes dictionary."""
    params = dict_to_frozenset(parameters) if parameters else None
    nodes[uid] = create_node(uid, node_type, params)


def add_connection(connections: Dict[str, Any], from_uid: str, to_uid: str, order: int):
    """Helper function to add a connection to the connections dictionary."""
    if from_uid not in connections:
        connections[from_uid] = {'success': {}}
    connections[from_uid]['success'][to_uid] = {'order': order, 'to': to_uid}


def convert_defaultdict_to_dict(d):
    """Convert nested defaultdict to a regular dictionary."""
    if isinstance(d, defaultdict):
        d = {k: convert_defaultdict_to_dict(v) for k, v in d.items()}
    return d


if __name__ == "__main__":
    input_json = {
        "workflows": {
            "cmNyJ": {
                "properties": {"element_id": "cmNuA"},
                "type": "ButtonClicked",
                "id": "cmNyH",
                "actions": {
                    "0": {
                        "properties": {"value": "1d", "element_id": "cmNth", "custom_state": "custom.selected_"},
                        "type": "SetCustomState",
                        "id": "cmNyN"
                    }
                }
            },
            "cmNyU": {
                "properties": {"element_id": "cmNvI"},
                "type": "ButtonClicked",
                "id": "cmNyO",
                "actions": {
                    "0": {
                        "properties": {"value": "1m", "element_id": "cmNth", "custom_state": "custom.selected_"},
                        "type": "SetCustomState",
                        "id": "cmNyT"
                    }
                }
            },
            "cmNyb": {
                "properties": {"element_id": "cmNuw"},
                "type": "ButtonClicked",
                "id": "cmNyV",
                "actions": {
                    "0": {
                        "properties": {"value": "1w", "element_id": "cmNth", "custom_state": "custom.selected_"},
                        "type": "SetCustomState",
                        "id": "cmNya"
                    }
                }
            },
            "cmNyl": {
                "properties": {"element_id": "cmNvC"},
                "type": "ButtonClicked",
                "id": "cmNyf",
                "actions": {
                    "0": {
                        "properties": {"value": "2w", "element_id": "cmNth", "custom_state": "custom.selected_"},
                        "type": "SetCustomState",
                        "id": "cmNyh"
                    }
                }
            }
        }
    }
    output_json = parse_workflows_to_atoms(input_json)
    print(json.dumps(output_json, indent=2))

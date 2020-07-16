from typing import Dict, List


class CurrentGraph:

    def __init__(self):
        relationships: List[Relationship]


class Relationship:

    def __init__(self):
        type: str
        attributes: Dict
        source_node: Node
        dst_node: Node


class Node:

    def __init__(self):
        label: str
        attributes: Dict

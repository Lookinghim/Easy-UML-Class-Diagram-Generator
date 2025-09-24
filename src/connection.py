"""
UML Connection Logic and Management System
Handles relationships between UML classes and their visual representation
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum
import math

class ConnectionType(Enum):
    """Enumeration of UML relationship types"""
    ASSOCIATION = "association"
    AGGREGATION = "aggregation" 
    COMPOSITION = "composition"
    INHERITANCE = "inheritance"
    REALIZATION = "realization"
    DEPENDENCY = "dependency"

class ConnectionDirection(Enum):
    """Direction of the connection"""
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"

@dataclass
class ConnectionPoint:
    """Represents a connection point on a UML class"""
    x: int
    y: int
    side: str  # 'top', 'bottom', 'left', 'right'

@dataclass
class UMLConnection:
    """Represents a connection between two UML classes"""
    id: str
    from_class: str
    to_class: str
    connection_type: ConnectionType
    direction: ConnectionDirection = ConnectionDirection.UNIDIRECTIONAL
    label: str = ""
    from_multiplicity: str = ""
    to_multiplicity: str = ""
    color: str = "black"
    width: int = 2
    
    # Connection points (calculated automatically)
    start_point: Optional[ConnectionPoint] = None
    end_point: Optional[ConnectionPoint] = None

class ConnectionManager:
    """Manages all connections in a UML diagram"""
    
    def __init__(self):
        self.connections: List[UMLConnection] = []
        self.class_positions: Dict[str, Tuple[int, int, int, int]] = {}  # class_name: (x, y, width, height)
    
    def add_class_position(self, class_name: str, x: int, y: int, width: int, height: int):
        """Register a class position for connection calculations"""
        self.class_positions[class_name] = (x, y, width, height)
    
    def add_connection(self, connection: UMLConnection) -> bool:
        """Add a new connection to the diagram"""
        # Validate that both classes exist
        if connection.from_class not in self.class_positions:
            print(f"Warning: Class '{connection.from_class}' not found")
            return False
        if connection.to_class not in self.class_positions:
            print(f"Warning: Class '{connection.to_class}' not found") 
            return False
        
        # Calculate connection points
        connection.start_point, connection.end_point = self._calculate_connection_points(
            connection.from_class, connection.to_class
        )
        
        self.connections.append(connection)
        return True
    
    def remove_connection(self, connection_id: str):
        """Remove a connection by ID"""
        self.connections = [conn for conn in self.connections if conn.id != connection_id]
    
    def get_connections_for_class(self, class_name: str) -> List[UMLConnection]:
        """Get all connections involving a specific class"""
        return [conn for conn in self.connections 
                if conn.from_class == class_name or conn.to_class == class_name]
    
    def _calculate_connection_points(self, from_class: str, to_class: str) -> Tuple[ConnectionPoint, ConnectionPoint]:
        """Calculate optimal connection points between two classes"""
        from_pos = self.class_positions[from_class]
        to_pos = self.class_positions[to_class]
        
        from_x, from_y, from_w, from_h = from_pos
        to_x, to_y, to_w, to_h = to_pos
        
        # Calculate center points
        from_center_x = from_x + from_w // 2
        from_center_y = from_y + from_h // 2
        to_center_x = to_x + to_w // 2
        to_center_y = to_y + to_h // 2
        
        # Determine best connection sides based on relative positions
        start_point = self._get_best_connection_point(from_pos, to_center_x, to_center_y)
        end_point = self._get_best_connection_point(to_pos, from_center_x, from_center_y)
        
        return start_point, end_point
    
    def _get_best_connection_point(self, class_pos: Tuple[int, int, int, int], 
                                  target_x: int, target_y: int) -> ConnectionPoint:
        """Get the best connection point on a class border with offset to prevent arrow overlap"""
        x, y, w, h = class_pos
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Calculate relative position of target
        dx = target_x - center_x
        dy = target_y - center_y
        
        # Offset to prevent arrow heads from overlapping with box content
        arrow_offset = 15  # Maximum size of any arrow/symbol in drawConnection
        
        # Determine which side to connect to
        if abs(dx) > abs(dy):
            # Connect to left or right side
            if dx > 0:  # Target is to the right
                return ConnectionPoint(x + w + arrow_offset, center_y, 'right')
            else:  # Target is to the left
                return ConnectionPoint(x - arrow_offset, center_y, 'left')
        else:
            # Connect to top or bottom side
            if dy > 0:  # Target is below
                return ConnectionPoint(center_x, y + h + arrow_offset, 'bottom')
            else:  # Target is above
                return ConnectionPoint(center_x, y - arrow_offset, 'top')

# Helper functions for creating common UML relationships
def create_inheritance_connection(child_class: str, parent_class: str, 
                                connection_id: str = None) -> UMLConnection:
    """Create an inheritance relationship"""
    if connection_id is None:
        connection_id = f"{child_class}_inherits_{parent_class}"
    
    return UMLConnection(
        id=connection_id,
        from_class=child_class,
        to_class=parent_class,
        connection_type=ConnectionType.INHERITANCE,
        color="red"
    )

def create_association_connection(from_class: str, to_class: str,
                                label: str = "", from_mult: str = "", to_mult: str = "",
                                connection_id: str = None) -> UMLConnection:
    """Create an association relationship"""
    if connection_id is None:
        connection_id = f"{from_class}_assoc_{to_class}"
    
    return UMLConnection(
        id=connection_id,
        from_class=from_class,
        to_class=to_class,
        connection_type=ConnectionType.ASSOCIATION,
        label=label,
        from_multiplicity=from_mult,
        to_multiplicity=to_mult,
        color="blue"
    )

def create_composition_connection(whole_class: str, part_class: str,
                                connection_id: str = None) -> UMLConnection:
    """Create a composition relationship (strong ownership)"""
    if connection_id is None:
        connection_id = f"{whole_class}_composes_{part_class}"
    
    return UMLConnection(
        id=connection_id,
        from_class=whole_class,
        to_class=part_class,
        connection_type=ConnectionType.COMPOSITION,
        color="black"
    )

def create_aggregation_connection(whole_class: str, part_class: str,
                                connection_id: str = None) -> UMLConnection:
    """Create an aggregation relationship (weak ownership)"""
    if connection_id is None:
        connection_id = f"{whole_class}_aggregates_{part_class}"
    
    return UMLConnection(
        id=connection_id,
        from_class=whole_class,
        to_class=part_class,
        connection_type=ConnectionType.AGGREGATION,
        color="black"
    )

def create_dependency_connection(dependent_class: str, dependency_class: str,
                               connection_id: str = None) -> UMLConnection:
    """Create a dependency relationship"""
    if connection_id is None:
        connection_id = f"{dependent_class}_depends_{dependency_class}"
    
    return UMLConnection(
        id=connection_id,
        from_class=dependent_class,
        to_class=dependency_class,
        connection_type=ConnectionType.DEPENDENCY,
        color="gray"
    )

def create_realization_connection(implementing_class: str, interface_class: str,
                                connection_id: str = None) -> UMLConnection:
    """Create a realization/implementation relationship"""
    if connection_id is None:
        connection_id = f"{implementing_class}_implements_{interface_class}"
    
    return UMLConnection(
        id=connection_id,
        from_class=implementing_class,
        to_class=interface_class,
        connection_type=ConnectionType.REALIZATION,
        color="green"
    )

# Utility functions for connection validation and management
def validate_connection(connection: UMLConnection, available_classes: List[str]) -> List[str]:
    """Validate a connection and return any errors"""
    errors = []
    
    if connection.from_class not in available_classes:
        errors.append(f"Source class '{connection.from_class}' does not exist")
    
    if connection.to_class not in available_classes:
        errors.append(f"Target class '{connection.to_class}' does not exist")
    
    if connection.from_class == connection.to_class:
        errors.append("Self-connections are not allowed")
    
    return errors

def detect_connection_conflicts(connections: List[UMLConnection]) -> List[str]:
    """Detect potential conflicts between connections"""
    conflicts = []
    
    # Check for duplicate connections
    connection_pairs = set()
    for conn in connections:
        pair = (conn.from_class, conn.to_class, conn.connection_type.value)
        if pair in connection_pairs:
            conflicts.append(f"Duplicate connection: {conn.from_class} -> {conn.to_class} ({conn.connection_type.value})")
        connection_pairs.add(pair)
    
    return conflicts

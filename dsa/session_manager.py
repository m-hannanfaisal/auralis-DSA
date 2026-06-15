"""
Module 2: SessionManager (AVL Tree / Balanced BST)
==================================================
Auralis-DSA: Optimized Market Session Analyzer & Trade Risk Engine
Course: CS-250 — Data Structures & Algorithms

Features:
- AVL tree implemented manually in Python
- O(log n) insertion with rotations
- O(log n) lookup to determine which session a timestamp belongs to
- Demonstrates balancing, traversal, and interval querying
"""

from datetime import datetime, time
from typing import Optional, List, Tuple, Any


class AVLNode:
    """
    Node for AVL Tree storing trading session intervals.
    
    Each node represents a trading session with:
    - start_hour: Start hour of session (0-23)
    - end_hour: End hour of session (0-23)
    - session_name: Name of the trading session
    """
    __slots__ = ['start_hour', 'end_hour', 'session_name', 'height', 'left', 'right']
    
    def __init__(self, start_hour: int, end_hour: int, session_name: str):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.session_name = session_name
        self.height = 1
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
    
    def __repr__(self) -> str:
        return f"Session({self.session_name}: {self.start_hour:02d}:00-{self.end_hour:02d}:00)"


class AVLTree:
    """
    AVL Tree (Self-Balancing Binary Search Tree) implementation.
    
    Time Complexities:
    - Insertion: O(log n) with automatic balancing
    - Search: O(log n)
    - Deletion: O(log n)
    - Traversal: O(n)
    
    Space Complexity: O(n)
    
    Maintains balance factor in range [-1, 0, 1] for all nodes.
    """
    
    def __init__(self):
        """Initialize empty AVL tree."""
        self.root: Optional[AVLNode] = None
        self._size = 0
        self._rotations = 0  # Track rotations for analysis
        self._comparisons = 0  # Track comparisons for analysis
    
    def _height(self, node: Optional[AVLNode]) -> int:
        """Get height of node (0 if None)."""
        return node.height if node else 0
    
    def _balance_factor(self, node: AVLNode) -> int:
        """
        Calculate balance factor of node.
        Balance factor = height(left) - height(right)
        Valid range: [-1, 0, 1]
        """
        return self._height(node.left) - self._height(node.right)
    
    def _update_height(self, node: AVLNode) -> None:
        """Update height of node based on children."""
        node.height = 1 + max(self._height(node.left), self._height(node.right))
    
    def _rotate_right(self, y: AVLNode) -> AVLNode:
        r"""
        Right rotation (for Left-Left case).
        
             y                x
            / \             /   \
           x   C    =>     A     y
          / \                   / \
         A   B                 B   C
         
        Time Complexity: O(1)
        """
        self._rotations += 1
        x = y.left
        B = x.right
        
        # Perform rotation
        x.right = y
        y.left = B
        
        # Update heights (order matters: y first, then x)
        self._update_height(y)
        self._update_height(x)
        
        return x
    
    def _rotate_left(self, x: AVLNode) -> AVLNode:
        r"""
        Left rotation (for Right-Right case).
        
           x                  y
          / \               /   \
         A   y      =>     x     C
            / \           / \
           B   C         A   B
           
        Time Complexity: O(1)
        """
        self._rotations += 1
        y = x.right
        B = y.left
        
        # Perform rotation
        y.left = x
        x.right = B
        
        # Update heights (order matters: x first, then y)
        self._update_height(x)
        self._update_height(y)
        
        return y
    
    def _rebalance(self, node: AVLNode, key: int) -> AVLNode:
        """
        Rebalance node after insertion if needed.
        
        Four cases:
        1. Left-Left: Single right rotation
        2. Left-Right: Left rotation on left child, then right rotation
        3. Right-Right: Single left rotation
        4. Right-Left: Right rotation on right child, then left rotation
        """
        balance = self._balance_factor(node)
        
        # Left-Left Case
        if balance > 1 and key < node.left.start_hour:
            return self._rotate_right(node)
        
        # Right-Right Case
        if balance < -1 and key > node.right.start_hour:
            return self._rotate_left(node)
        
        # Left-Right Case
        if balance > 1 and key > node.left.start_hour:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Right-Left Case
        if balance < -1 and key < node.right.start_hour:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node
    
    def _insert_recursive(self, node: Optional[AVLNode], start_hour: int, 
                         end_hour: int, session_name: str) -> AVLNode:
        """Recursive helper for insertion with balancing."""
        # Standard BST insertion
        if node is None:
            self._size += 1
            return AVLNode(start_hour, end_hour, session_name)
        
        self._comparisons += 1
        
        if start_hour < node.start_hour:
            node.left = self._insert_recursive(node.left, start_hour, end_hour, session_name)
        elif start_hour > node.start_hour:
            node.right = self._insert_recursive(node.right, start_hour, end_hour, session_name)
        else:
            # Duplicate key - update session info
            node.end_hour = end_hour
            node.session_name = session_name
            return node
        
        # Update height
        self._update_height(node)
        
        # Rebalance if needed
        return self._rebalance(node, start_hour)
    
    def insert(self, start_hour: int, end_hour: int, session_name: str) -> None:
        """
        Insert a trading session into the AVL tree.
        
        Time Complexity: O(log n)
        
        Args:
            start_hour: Session start hour (0-23)
            end_hour: Session end hour (0-23)
            session_name: Name of the session (e.g., "Asian", "London", "NY")
        """
        self._comparisons = 0
        self.root = self._insert_recursive(self.root, start_hour, end_hour, session_name)
    
    def _search_recursive(self, node: Optional[AVLNode], hour: int) -> Optional[AVLNode]:
        """Recursive helper for searching which session contains an hour."""
        if node is None:
            return None
        
        self._comparisons += 1
        
        # Check if hour falls within this session's range
        if node.start_hour <= hour < node.end_hour:
            return node
        
        # Search in appropriate subtree
        if hour < node.start_hour:
            return self._search_recursive(node.left, hour)
        else:
            return self._search_recursive(node.right, hour)
    
    def find_session(self, hour: int) -> Optional[str]:
        """
        Find which trading session an hour belongs to.
        
        Time Complexity: O(log n)
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            Session name if found, None otherwise
        """
        self._comparisons = 0
        node = self._search_recursive(self.root, hour)
        return node.session_name if node else None
    
    def find_session_for_timestamp(self, timestamp: datetime) -> Optional[str]:
        """
        Find which trading session a timestamp belongs to.
        
        Time Complexity: O(log n)
        """
        return self.find_session(timestamp.hour)
    
    def _inorder_recursive(self, node: Optional[AVLNode], result: List[AVLNode]) -> None:
        """In-order traversal helper."""
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node)
            self._inorder_recursive(node.right, result)
    
    def inorder_traversal(self) -> List[AVLNode]:
        """
        In-order traversal of tree (sessions sorted by start hour).
        Time Complexity: O(n)
        """
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node: Optional[AVLNode], result: List[AVLNode]) -> None:
        """Pre-order traversal helper."""
        if node:
            result.append(node)
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)
    
    def preorder_traversal(self) -> List[AVLNode]:
        """Pre-order traversal of tree. Time Complexity: O(n)"""
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def __len__(self) -> int:
        """Return number of sessions in tree."""
        return self._size
    
    @property
    def height(self) -> int:
        """Height of the tree."""
        return self._height(self.root)
    
    @property
    def last_comparisons(self) -> int:
        """Number of comparisons in last operation."""
        return self._comparisons
    
    @property
    def total_rotations(self) -> int:
        """Total rotations performed."""
        return self._rotations
    
    def get_stats(self) -> dict:
        """Get tree statistics."""
        return {
            'size': self._size,
            'height': self.height,
            'total_rotations': self._rotations,
            'is_balanced': self._is_balanced(self.root)
        }
    
    def _is_balanced(self, node: Optional[AVLNode]) -> bool:
        """Check if tree is balanced (all nodes have balance factor in [-1, 0, 1])."""
        if node is None:
            return True
        
        balance = self._balance_factor(node)
        if balance < -1 or balance > 1:
            return False
        
        return self._is_balanced(node.left) and self._is_balanced(node.right)
    
    def print_tree(self, node: Optional[AVLNode] = None, level: int = 0, prefix: str = "Root: ") -> None:
        """Print tree structure visually."""
        if node is None:
            node = self.root
        
        if node is not None:
            print(" " * (level * 4) + prefix + str(node) + f" (h={node.height})")
            if node.left or node.right:
                if node.left:
                    self.print_tree(node.left, level + 1, "L--- ")
                else:
                    print(" " * ((level + 1) * 4) + "L--- None")
                if node.right:
                    self.print_tree(node.right, level + 1, "R--- ")
                else:
                    print(" " * ((level + 1) * 4) + "R--- None")


class SessionManager:
    """
    Trading Session Manager using AVL Tree.
    
    Manages market sessions (Asian, London, NY) and provides
    O(log n) lookup for session classification.
    
    Default Sessions (UTC):
    - Asian: 00:00 - 06:00
    - London: 07:00 - 15:00  
    - New York: 13:00 - 21:00
    - Off-Hours: Times not in any session
    """
    
    # Default session definitions (UTC hours)
    DEFAULT_SESSIONS = [
        (0, 6, "Asian"),
        (7, 15, "London"),
        (13, 21, "NewYork"),  # Note: Overlaps with London
    ]
    
    def __init__(self, use_defaults: bool = True):
        """
        Initialize SessionManager.
        
        Args:
            use_defaults: If True, load default trading sessions
        """
        self._tree = AVLTree()
        self._sessions_list = []  # Keep ordered list for overlap checking
        
        if use_defaults:
            self._load_default_sessions()
    
    def _load_default_sessions(self) -> None:
        """Load default trading sessions into AVL tree."""
        for start, end, name in self.DEFAULT_SESSIONS:
            self.add_session(start, end, name)
    
    def add_session(self, start_hour: int, end_hour: int, name: str) -> None:
        """
        Add a trading session.
        
        Time Complexity: O(log n)
        
        Args:
            start_hour: Start hour (0-23)
            end_hour: End hour (0-23)
            name: Session name
        """
        self._tree.insert(start_hour, end_hour, name)
        self._sessions_list.append((start_hour, end_hour, name))
    
    def classify_timestamp(self, timestamp: datetime) -> str:
        """
        Classify which session a timestamp belongs to.
        
        Time Complexity: O(log n)
        
        Returns:
            Session name or "Off-Hours" if not in any session
        """
        session = self._tree.find_session(timestamp.hour)
        return session if session else "Off-Hours"
    
    def classify_hour(self, hour: int) -> str:
        """
        Classify which session an hour belongs to.
        
        Time Complexity: O(log n)
        """
        session = self._tree.find_session(hour)
        return session if session else "Off-Hours"
    
    def get_session_info(self, timestamp: datetime) -> dict:
        """
        Get detailed session info for a timestamp.
        
        Returns dict with session details and lookup stats.
        """
        session = self.classify_timestamp(timestamp)
        
        return {
            'timestamp': timestamp,
            'hour': timestamp.hour,
            'session': session,
            'comparisons': self._tree.last_comparisons
        }
    
    def classify_multiple(self, timestamps: List[datetime]) -> List[str]:
        """
        Classify multiple timestamps.
        Time Complexity: O(m log n) for m timestamps
        """
        return [self.classify_timestamp(ts) for ts in timestamps]
    
    def get_all_sessions(self) -> List[Tuple[int, int, str]]:
        """
        Get all sessions sorted by start hour.
        Time Complexity: O(n)
        """
        nodes = self._tree.inorder_traversal()
        return [(n.start_hour, n.end_hour, n.session_name) for n in nodes]
    
    def is_trading_hours(self, timestamp: datetime, allowed_sessions: List[str] = None) -> bool:
        """
        Check if timestamp is during allowed trading hours.
        
        Args:
            timestamp: Time to check
            allowed_sessions: List of allowed session names (default: all)
        """
        session = self.classify_timestamp(timestamp)
        
        if session == "Off-Hours":
            return False
        
        if allowed_sessions is None:
            return True
        
        return session in allowed_sessions
    
    def get_stats(self) -> dict:
        """Get session manager statistics."""
        tree_stats = self._tree.get_stats()
        return {
            **tree_stats,
            'sessions': self.get_all_sessions()
        }
    
    def print_tree(self) -> None:
        """Print AVL tree structure."""
        self._tree.print_tree()


# Demonstration functions
def demo_session_manager():
    """Demonstrate SessionManager functionality."""
    print("=" * 60)
    print("Module 2: SessionManager (AVL Tree / Balanced BST)")
    print("=" * 60)
    
    manager = SessionManager(use_defaults=True)
    
    print("\n1. AVL Tree Structure after inserting sessions:")
    manager.print_tree()
    
    stats = manager.get_stats()
    print(f"\n2. Tree Statistics:")
    print(f"   - Number of sessions: {stats['size']}")
    print(f"   - Tree height: {stats['height']}")
    print(f"   - Total rotations: {stats['total_rotations']}")
    print(f"   - Is balanced: {stats['is_balanced']}")
    
    print("\n3. All sessions (in-order traversal):")
    for start, end, name in stats['sessions']:
        print(f"   - {name}: {start:02d}:00 - {end:02d}:00 UTC")
    
    print("\n4. Session Classification (O(log n) lookup):")
    test_hours = [2, 5, 8, 12, 15, 18, 22]
    for hour in test_hours:
        test_ts = datetime(2024, 1, 15, hour, 30, 0)
        info = manager.get_session_info(test_ts)
        print(f"   - {hour:02d}:30 UTC → {info['session']} (comparisons: {info['comparisons']})")
    
    print("\n5. Trading Hours Check:")
    london_only = ["London"]
    test_times = [
        datetime(2024, 1, 15, 3, 0),   # Asian
        datetime(2024, 1, 15, 9, 0),   # London
        datetime(2024, 1, 15, 22, 0),  # Off-hours
    ]
    for ts in test_times:
        is_london = manager.is_trading_hours(ts, london_only)
        session = manager.classify_timestamp(ts)
        print(f"   - {ts.strftime('%H:%M')} ({session}): London trading = {is_london}")
    
    return manager


if __name__ == "__main__":
    demo_session_manager()


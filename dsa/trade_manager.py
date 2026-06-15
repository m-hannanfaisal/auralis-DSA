"""
Module 3: TradeManager & Risk Engine (Linked List + Max-Heap)
=============================================================
Auralis-DSA: Optimized Market Session Analyzer & Trade Risk Engine
Course: CS-250 — Data Structures & Algorithms

Features:
- Custom Linked List for active trades
- Max-Heap for risk ranking (highest-risk trade on top)
- O(1) insertion into linked list + O(log n) heap operations
- Greedy risk enforcement by removing highest-risk trades
"""

from datetime import datetime
from typing import Optional, List, Any
from dataclasses import dataclass
import uuid


@dataclass
class Trade:
    """
    Represents an active trade with risk information.
    """
    trade_id: str
    symbol: str
    direction: str  # "LONG" or "SHORT"
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    entry_time: datetime
    risk_score: float = 0.0  # Higher = more risky
    
    def __post_init__(self):
        """Calculate risk score if not provided."""
        if self.risk_score == 0.0:
            self.risk_score = self.calculate_risk_score()
    
    def calculate_risk_score(self) -> float:
        """
        Calculate risk score based on trade parameters.
        Higher score = Higher risk
        
        Factors:
        - Distance to stop loss (larger = more risk)
        - Position size (larger = more risk)
        - Reward/Risk ratio (lower = more risk)
        """
        if self.direction == "LONG":
            sl_distance = abs(self.entry_price - self.stop_loss)
            tp_distance = abs(self.take_profit - self.entry_price)
        else:  # SHORT
            sl_distance = abs(self.stop_loss - self.entry_price)
            tp_distance = abs(self.entry_price - self.take_profit)
        
        # Risk = position_size * sl_distance (potential loss)
        potential_loss = self.position_size * sl_distance
        
        # Penalize low R:R trades
        rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        rr_penalty = 1.0 / (rr_ratio + 0.1)  # Lower R:R = higher penalty
        
        risk_score = potential_loss * rr_penalty
        return round(risk_score, 4)
    
    def __repr__(self) -> str:
        return f"Trade({self.trade_id[:8]}, {self.direction} {self.symbol}, risk={self.risk_score:.2f})"
    
    def __lt__(self, other: 'Trade') -> bool:
        """For heap comparisons (max-heap needs inverted comparison)."""
        return self.risk_score < other.risk_score
    
    def __gt__(self, other: 'Trade') -> bool:
        return self.risk_score > other.risk_score


class LinkedListNode:
    """Node for doubly linked list."""
    __slots__ = ['data', 'prev', 'next']
    
    def __init__(self, data: Any):
        self.data = data
        self.prev: Optional['LinkedListNode'] = None
        self.next: Optional['LinkedListNode'] = None


class LinkedList:
    """
    Doubly Linked List implementation for active trade management.
    
    Time Complexities:
    - Insert at head/tail: O(1)
    - Delete with node reference: O(1)
    - Search by value: O(n)
    - Traversal: O(n)
    
    Space Complexity: O(n)
    """
    
    def __init__(self):
        """Initialize empty linked list with sentinel nodes."""
        self._head: Optional[LinkedListNode] = None
        self._tail: Optional[LinkedListNode] = None
        self._size = 0
        self._node_map: dict = {}  # trade_id -> node for O(1) deletion
    
    def insert_head(self, trade: Trade) -> LinkedListNode:
        """
        Insert trade at head of list.
        Time Complexity: O(1)
        """
        node = LinkedListNode(trade)
        
        if self._head is None:
            self._head = self._tail = node
        else:
            node.next = self._head
            self._head.prev = node
            self._head = node
        
        self._size += 1
        self._node_map[trade.trade_id] = node
        return node
    
    def insert_tail(self, trade: Trade) -> LinkedListNode:
        """
        Insert trade at tail of list.
        Time Complexity: O(1)
        """
        node = LinkedListNode(trade)
        
        if self._tail is None:
            self._head = self._tail = node
        else:
            node.prev = self._tail
            self._tail.next = node
            self._tail = node
        
        self._size += 1
        self._node_map[trade.trade_id] = node
        return node
    
    def delete_node(self, node: LinkedListNode) -> Trade:
        """
        Delete a specific node.
        Time Complexity: O(1)
        """
        if node is None:
            raise ValueError("Cannot delete None node")
        
        trade = node.data
        
        # Update links
        if node.prev:
            node.prev.next = node.next
        else:
            self._head = node.next
        
        if node.next:
            node.next.prev = node.prev
        else:
            self._tail = node.prev
        
        self._size -= 1
        if trade.trade_id in self._node_map:
            del self._node_map[trade.trade_id]
        
        return trade
    
    def delete_by_id(self, trade_id: str) -> Optional[Trade]:
        """
        Delete trade by ID using hash map lookup.
        Time Complexity: O(1)
        """
        if trade_id not in self._node_map:
            return None
        
        node = self._node_map[trade_id]
        return self.delete_node(node)
    
    def find_by_id(self, trade_id: str) -> Optional[Trade]:
        """
        Find trade by ID using hash map.
        Time Complexity: O(1)
        """
        if trade_id in self._node_map:
            return self._node_map[trade_id].data
        return None
    
    def search(self, predicate) -> Optional[Trade]:
        """
        Search for trade matching predicate.
        Time Complexity: O(n)
        """
        current = self._head
        while current:
            if predicate(current.data):
                return current.data
            current = current.next
        return None
    
    def to_list(self) -> List[Trade]:
        """
        Convert to Python list.
        Time Complexity: O(n)
        """
        result = []
        current = self._head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def __len__(self) -> int:
        return self._size
    
    def __iter__(self):
        """Iterator for the linked list."""
        current = self._head
        while current:
            yield current.data
            current = current.next
    
    def is_empty(self) -> bool:
        return self._size == 0


class MaxHeap:
    """
    Max-Heap implementation for risk-based trade prioritization.
    
    Time Complexities:
    - Insert: O(log n)
    - Extract max: O(log n)
    - Peek max: O(1)
    - Heapify: O(n)
    
    Space Complexity: O(n)
    
    Uses risk_score as the key - highest risk trade is at root.
    """
    
    def __init__(self):
        """Initialize empty max-heap."""
        self._heap: List[Trade] = []
        self._size = 0
        self._trade_indices: dict = {}  # trade_id -> index for O(log n) updates
    
    def _parent(self, i: int) -> int:
        """Get parent index."""
        return (i - 1) // 2
    
    def _left_child(self, i: int) -> int:
        """Get left child index."""
        return 2 * i + 1
    
    def _right_child(self, i: int) -> int:
        """Get right child index."""
        return 2 * i + 2
    
    def _swap(self, i: int, j: int) -> None:
        """Swap elements and update index map."""
        self._trade_indices[self._heap[i].trade_id] = j
        self._trade_indices[self._heap[j].trade_id] = i
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
    
    def _sift_up(self, i: int) -> None:
        """
        Sift element up to maintain heap property.
        Time Complexity: O(log n)
        """
        while i > 0:
            parent = self._parent(i)
            # Max-heap: parent should be >= children
            if self._heap[i].risk_score > self._heap[parent].risk_score:
                self._swap(i, parent)
                i = parent
            else:
                break
    
    def _sift_down(self, i: int) -> None:
        """
        Sift element down to maintain heap property.
        Time Complexity: O(log n)
        """
        while True:
            largest = i
            left = self._left_child(i)
            right = self._right_child(i)
            
            if left < self._size and self._heap[left].risk_score > self._heap[largest].risk_score:
                largest = left
            
            if right < self._size and self._heap[right].risk_score > self._heap[largest].risk_score:
                largest = right
            
            if largest != i:
                self._swap(i, largest)
                i = largest
            else:
                break
    
    def insert(self, trade: Trade) -> None:
        """
        Insert trade into heap.
        Time Complexity: O(log n)
        """
        self._heap.append(trade)
        self._trade_indices[trade.trade_id] = self._size
        self._size += 1
        self._sift_up(self._size - 1)
    
    def extract_max(self) -> Optional[Trade]:
        """
        Remove and return highest-risk trade.
        Time Complexity: O(log n)
        """
        if self._size == 0:
            return None
        
        max_trade = self._heap[0]
        del self._trade_indices[max_trade.trade_id]
        
        # Move last element to root
        self._size -= 1
        if self._size > 0:
            self._heap[0] = self._heap[self._size]
            self._trade_indices[self._heap[0].trade_id] = 0
            self._heap.pop()
            self._sift_down(0)
        else:
            self._heap.pop()
        
        return max_trade
    
    def peek_max(self) -> Optional[Trade]:
        """
        Return highest-risk trade without removing.
        Time Complexity: O(1)
        """
        return self._heap[0] if self._size > 0 else None
    
    def remove_by_id(self, trade_id: str) -> Optional[Trade]:
        """
        Remove specific trade by ID.
        Time Complexity: O(log n)
        """
        if trade_id not in self._trade_indices:
            return None
        
        idx = self._trade_indices[trade_id]
        trade = self._heap[idx]
        del self._trade_indices[trade_id]
        
        # Replace with last element
        self._size -= 1
        if idx < self._size:
            self._heap[idx] = self._heap[self._size]
            self._trade_indices[self._heap[idx].trade_id] = idx
            self._heap.pop()
            
            # May need to sift up or down
            if idx > 0 and self._heap[idx].risk_score > self._heap[self._parent(idx)].risk_score:
                self._sift_up(idx)
            else:
                self._sift_down(idx)
        else:
            self._heap.pop()
        
        return trade
    
    def __len__(self) -> int:
        return self._size
    
    def is_empty(self) -> bool:
        return self._size == 0
    
    def to_sorted_list(self) -> List[Trade]:
        """Return trades sorted by risk (highest first). Time: O(n log n)"""
        # Create copy and extract all
        temp_heap = MaxHeap()
        temp_heap._heap = self._heap.copy()
        temp_heap._size = self._size
        temp_heap._trade_indices = self._trade_indices.copy()
        
        result = []
        while not temp_heap.is_empty():
            result.append(temp_heap.extract_max())
        return result


class TradeManager:
    """
    Trade Manager with Risk Engine.
    
    Combines:
    - LinkedList for O(1) trade insertion and sequential access
    - MaxHeap for O(log n) risk-based prioritization
    
    Use cases:
    - Add new trades: O(1) linked list + O(log n) heap
    - Close specific trade: O(1) linked list + O(log n) heap
    - Get highest-risk trade: O(1) peek
    - Enforce risk limits: O(k log n) for removing k trades
    """
    
    def __init__(self, max_risk_budget: float = 100.0, max_concurrent_trades: int = 5):
        """
        Initialize TradeManager.
        
        Args:
            max_risk_budget: Maximum total risk allowed
            max_concurrent_trades: Maximum number of concurrent trades
        """
        self._trades_list = LinkedList()  # For sequential access
        self._risk_heap = MaxHeap()       # For risk prioritization
        self._max_risk_budget = max_risk_budget
        self._max_concurrent = max_concurrent_trades
        self._total_risk = 0.0
        self._trades_removed_for_risk = 0
    
    def add_trade(self, trade: Trade) -> bool:
        """
        Add a new trade to the manager.
        
        Time Complexity: O(log n)
        
        Returns:
            True if trade was added, False if rejected
        """
        # Check concurrent trade limit
        if len(self._trades_list) >= self._max_concurrent:
            # Enforce by removing highest risk trade
            self._enforce_trade_limit()
        
        # Add to both structures
        self._trades_list.insert_tail(trade)
        self._risk_heap.insert(trade)
        self._total_risk += trade.risk_score
        
        # Enforce risk budget
        self._enforce_risk_budget()
        
        return True
    
    def create_and_add_trade(self, symbol: str, direction: str, entry_price: float,
                             stop_loss: float, take_profit: float, 
                             position_size: float) -> Trade:
        """
        Create and add a new trade.
        
        Time Complexity: O(log n)
        """
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            entry_time=datetime.now()
        )
        self.add_trade(trade)
        return trade
    
    def close_trade(self, trade_id: str) -> Optional[Trade]:
        """
        Close a specific trade by ID.
        
        Time Complexity: O(log n)
        """
        # Remove from both structures
        trade = self._trades_list.delete_by_id(trade_id)
        if trade:
            self._risk_heap.remove_by_id(trade_id)
            self._total_risk -= trade.risk_score
        return trade
    
    def get_highest_risk_trade(self) -> Optional[Trade]:
        """
        Get the highest-risk trade without removing.
        
        Time Complexity: O(1)
        """
        return self._risk_heap.peek_max()
    
    def remove_highest_risk_trade(self) -> Optional[Trade]:
        """
        Remove and return the highest-risk trade.
        Greedy algorithm for risk enforcement.
        
        Time Complexity: O(log n)
        """
        trade = self._risk_heap.extract_max()
        if trade:
            self._trades_list.delete_by_id(trade.trade_id)
            self._total_risk -= trade.risk_score
            self._trades_removed_for_risk += 1
        return trade
    
    def _enforce_risk_budget(self) -> None:
        """
        Greedy algorithm: Remove highest-risk trades until within budget.
        Time Complexity: O(k log n) for k removed trades
        """
        while self._total_risk > self._max_risk_budget and not self._risk_heap.is_empty():
            self.remove_highest_risk_trade()
    
    def _enforce_trade_limit(self) -> None:
        """
        Remove highest-risk trade to make room for new trade.
        Time Complexity: O(log n)
        """
        if len(self._trades_list) >= self._max_concurrent:
            self.remove_highest_risk_trade()
    
    def get_all_trades(self) -> List[Trade]:
        """
        Get all active trades in insertion order.
        Time Complexity: O(n)
        """
        return self._trades_list.to_list()
    
    def get_trades_by_risk(self) -> List[Trade]:
        """
        Get all trades sorted by risk (highest first).
        Time Complexity: O(n log n)
        """
        return self._risk_heap.to_sorted_list()
    
    def get_trade_by_id(self, trade_id: str) -> Optional[Trade]:
        """
        Find trade by ID.
        Time Complexity: O(1)
        """
        return self._trades_list.find_by_id(trade_id)
    
    @property
    def total_risk(self) -> float:
        """Current total risk exposure."""
        return self._total_risk
    
    @property
    def trade_count(self) -> int:
        """Number of active trades."""
        return len(self._trades_list)
    
    def get_stats(self) -> dict:
        """Get trade manager statistics."""
        return {
            'active_trades': len(self._trades_list),
            'total_risk': self._total_risk,
            'max_risk_budget': self._max_risk_budget,
            'risk_utilization': self._total_risk / self._max_risk_budget if self._max_risk_budget > 0 else 0,
            'trades_removed_for_risk': self._trades_removed_for_risk,
            'max_concurrent': self._max_concurrent,
            'highest_risk_trade': self.get_highest_risk_trade()
        }


# Demonstration functions
def demo_trade_manager():
    """Demonstrate TradeManager functionality."""
    print("=" * 60)
    print("Module 3: TradeManager & Risk Engine (LinkedList + MaxHeap)")
    print("=" * 60)
    
    manager = TradeManager(max_risk_budget=50.0, max_concurrent_trades=5)
    
    print(f"\nConfiguration:")
    print(f"  - Max risk budget: {manager._max_risk_budget}")
    print(f"  - Max concurrent trades: {manager._max_concurrent}")
    
    # Create sample trades with varying risk
    print("\n1. Adding trades to manager...")
    trades_data = [
        ("XAUUSD", "LONG", 1950.0, 1945.0, 1965.0, 1.0),   # Low risk
        ("XAUUSD", "SHORT", 1960.0, 1975.0, 1940.0, 2.0),  # Higher risk (bigger SL, bigger size)
        ("XAUUSD", "LONG", 1955.0, 1950.0, 1970.0, 1.5),   # Medium risk
        ("XAUUSD", "SHORT", 1952.0, 1958.0, 1940.0, 0.5),  # Low risk
        ("XAUUSD", "LONG", 1948.0, 1935.0, 1975.0, 3.0),   # High risk (big SL, big size)
    ]
    
    for symbol, direction, entry, sl, tp, size in trades_data:
        trade = manager.create_and_add_trade(symbol, direction, entry, sl, tp, size)
        print(f"   ✓ Added: {trade}")
    
    # Show current state
    print(f"\n2. Current State:")
    stats = manager.get_stats()
    print(f"   - Active trades: {stats['active_trades']}")
    print(f"   - Total risk: {stats['total_risk']:.2f}")
    print(f"   - Risk utilization: {stats['risk_utilization']:.1%}")
    print(f"   - Highest risk: {stats['highest_risk_trade']}")
    
    # Show trades by risk
    print("\n3. Trades sorted by risk (MaxHeap extraction order):")
    trades_by_risk = manager.get_trades_by_risk()
    for i, trade in enumerate(trades_by_risk, 1):
        print(f"   {i}. {trade.trade_id[:8]} - {trade.direction} - Risk: {trade.risk_score:.2f}")
    
    # Demonstrate greedy risk removal
    print("\n4. Greedy Risk Enforcement:")
    print(f"   Reducing risk budget to 20.0...")
    manager._max_risk_budget = 20.0
    manager._enforce_risk_budget()
    
    stats = manager.get_stats()
    print(f"   - Active trades after enforcement: {stats['active_trades']}")
    print(f"   - Total risk now: {stats['total_risk']:.2f}")
    print(f"   - Trades removed for risk: {stats['trades_removed_for_risk']}")
    
    # Show remaining trades
    print("\n5. Remaining trades (Linked List traversal):")
    for trade in manager.get_all_trades():
        print(f"   - {trade}")
    
    return manager


if __name__ == "__main__":
    demo_trade_manager()


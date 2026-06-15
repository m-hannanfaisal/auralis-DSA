# Auralis-DSA: Optimized Market Session Analyzer & Trade Risk Engine



 Module 1: CandleStore (DynamicArray + Binary Search) |
| Module 2: SessionManager (AVL Tree) + Module 3: TradeManager (LinkedList + MaxHeap) 

---

## 1. Problem Statement

Financial markets generate large volumes of OHLC time-series data, requiring fast detection of session patterns (Asian, London, NY), candle range calculations, and dynamic risk handling across multiple trades. Manual analysis becomes slow and inaccurate as data grows.

This project builds a **Python-based DSA-driven market session analyzer** that efficiently stores candle data, classifies timestamps into trading sessions, and manages active trades using optimized data structures.

---

## 2. Project Structure

```
Auralis-DSA/
├── dsa/                           # Core DSA modules
│   ├── __init__.py
│   ├── candle_store.py            # Module 1: DynamicArray + Binary Search
│   ├── session_manager.py         # Module 2: AVL Tree
│   └── trade_manager.py           # Module 3: LinkedList + MaxHeap
├── auralis_dsa.py                 # Main driver (demonstrates all modules)
├── benchmark_dsa.py               # Performance benchmarks (10³, 10⁴, 10⁵)
├── data/
│   ├── labels/
│   │   └── auralis_labels.parquet # XAUUSD M5 data (2018-2025)
│   └── raw/
│       └── xauusd_m5_UTC.csv
├── data_loader.py                 # Data loading utilities
├── preprocess.py                  # Preprocessing utilities
└── requirement.txt
```

---

## 3. DSA Modules Overview

### Module 1: CandleStore (Dynamic Array + Binary Search)

  
**File:** `dsa/candle_store.py`

| Component | Description | Time Complexity |
|-----------|-------------|-----------------|
| `DynamicArray` | Custom array with doubling strategy | Amortized O(1) insert |
| `CandleStore` | OHLC candle storage | O(1) access |
| `binary_search_timestamp()` | Find candle by timestamp | O(log n) |
| `calculate_session_range()` | Compute high/low for time range | O(log n + k) |

**Key Features:**
- Manual implementation of dynamic array (no Python list `append`)
- Doubling strategy reduces resize frequency
- Binary search for efficient timestamp lookup
- Session range calculations (Asia High/Low)

### Module 2: SessionManager (AVL Tree / Balanced BST)

**File:** `dsa/session_manager.py`

| Component | Description | Time Complexity |
|-----------|-------------|-----------------|
| `AVLNode` | Tree node with height tracking | - |
| `AVLTree` | Self-balancing BST | O(log n) operations |
| `SessionManager` | Trading session classifier | O(log n) lookup |

**Key Features:**
- Manual AVL tree with rotations (LL, RR, LR, RL cases)
- O(log n) insertion with automatic balancing
- Session classification: Asian, London, New York, Off-Hours
- In-order traversal for sorted session listing

**Rotations Implemented:**
- Single Right Rotation (Left-Left case)
- Single Left Rotation (Right-Right case)
- Left-Right Double Rotation
- Right-Left Double Rotation

### Module 3: TradeManager & Risk Engine (Linked List + Max-Heap)
 
**File:** `dsa/trade_manager.py`

| Component | Description | Time Complexity |
|-----------|-------------|-----------------|
| `LinkedList` | Doubly linked list for trades | O(1) insert/delete |
| `MaxHeap` | Priority queue by risk score | O(log n) operations |
| `TradeManager` | Integrated risk management | O(log n) per trade |

**Key Features:**
- Custom doubly linked list (no Python `deque`)
- Max-heap for risk prioritization (highest risk on top)
- Greedy algorithm for risk enforcement
- O(1) trade lookup via hash map

---

## 4. Algorithms Used

| Algorithm | Module | Purpose |
|-----------|--------|---------|
| Binary Search | CandleStore | O(log n) timestamp lookup |
| AVL Rotations | SessionManager | Maintain balanced tree |
| Heap Operations | TradeManager | Risk-based prioritization |
| Greedy Algorithm | TradeManager | Remove highest-risk trades |

---

## 5. How to Run

### 5.1 Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install requirements
pip install -r requirement.txt
```

### 5.2 Run Main Demonstration

```bash
python auralis_dsa.py
```

This demonstrates all three modules with real XAUUSD market data:
- Loads candles into CandleStore
- Classifies timestamps using AVL-based SessionManager
- Manages trades with LinkedList + MaxHeap

### 5.3 Run Performance Benchmarks

```bash
python benchmark_dsa.py
```

Benchmarks all data structures on input sizes: **10³, 10⁴, 10⁵**

---

## 6. Expected Outcomes

| Objective | Status |
|-----------|--------|
| Efficient candle data handling | ✅ DynamicArray + Binary Search |
| Fast and accurate session detection | ✅ AVL Tree O(log n) lookup |
| Dynamic risk management | ✅ MaxHeap priority queue |
| Big-O comparison (10³, 10⁴, 10⁵) | ✅ benchmark_dsa.py |
| Multiple DSA modules in Python | ✅ 3 modules implemented |

---

## 7. Complexity Analysis

### Module 1: CandleStore

| Operation | Time | Space |
|-----------|------|-------|
| `insert()` | Amortized O(1) | O(n) |
| `binary_search_timestamp()` | O(log n) | O(1) |
| `get_range()` | O(log n + k) | O(k) |
| `calculate_asia_range()` | O(log n + k) | O(k) |

### Module 2: SessionManager

| Operation | Time | Space |
|-----------|------|-------|
| `insert()` | O(log n) | O(n) |
| `find_session()` | O(log n) | O(1) |
| `inorder_traversal()` | O(n) | O(n) |

### Module 3: TradeManager

| Operation | Time | Space |
|-----------|------|-------|
| `add_trade()` | O(log n) | O(n) |
| `close_trade()` | O(log n) | O(1) |
| `get_highest_risk_trade()` | O(1) | O(1) |
| `remove_highest_risk_trade()` | O(log n) | O(1) |
| `enforce_risk_budget()` | O(k log n) | O(1) |

---





======================================================================
  MODULE 1: CandleStore (Dynamic Array + Binary Search)
======================================================================

📊 Loading XAUUSD M5 data into CandleStore...

✅ Data Loaded Successfully!
   • Candles stored: 10,000
   • Array capacity: 16,384
   • Array resizes (doubling): 11
   • Load factor: 61.04%

──────────────────────────────────────────────────
  Binary Search Performance
──────────────────────────────────────────────────

🔍 Searching for timestamp: 2024-01-15 12:00:00
   ✓ Found at index 144
   ✓ Comparisons made: 14
   ✓ Expected O(log n) ≈ 14
```

---

## 9. Data Description

**Instrument:** XAUUSD (Spot Gold)  
**Timeframe:** M5 (5-minute candles)  
**Period:** 2018–2025  
**Timezone:** UTC

**Sessions Defined:**
- **Asian:** 00:00 - 06:00 UTC
- **London:** 07:00 - 15:00 UTC
- **New York:** 13:00 - 21:00 UTC

---

## 10. Files Description

| File | Purpose |
|------|---------|
| `dsa/candle_store.py` | DynamicArray + Binary Search implementation |
| `dsa/session_manager.py` | AVL Tree implementation |
| `dsa/trade_manager.py` | LinkedList + MaxHeap implementation |
| `auralis_dsa.py` | Main demonstration script |
| `benchmark_dsa.py` | Performance benchmarks |
| `data_loader.py` | Load XAUUSD data from parquet |
| `preprocess.py` | Add helper columns (date, hour, asia_range) |

---

## 11. Summary

This project demonstrates the practical application of fundamental data structures and algorithms to a real-world financial trading system:

1. **Dynamic Array** - Efficient storage with amortized O(1) insertions
2. **Binary Search** - Fast O(log n) timestamp lookups
3. **AVL Tree** - Self-balancing BST for session classification
4. **Linked List** - O(1) trade management
5. **Max-Heap** - Priority-based risk management
6. **Greedy Algorithm** - Optimal risk enforcement

All data structures are **manually implemented** without using Python's built-in equivalents (e.g., `heapq`, `collections.deque`).

---

*Auralis-DSA © 2025 |*

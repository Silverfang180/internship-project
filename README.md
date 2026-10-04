# Vireo SLA Analysis

## Requirements
* Python 3.12 (or compatible Python 3 version)

## Setup and Usage

1. **Place the data files**: Before running anything, place the 8 raw pack files (`tickets.csv`, `agents.csv`, `orders.csv`, `customers.csv`, `products.csv`, `support-policy.pdf`, `email-thread.txt`, `README.txt`) into the `data/` directory. Do not commit these files, as they contain customer data.

2. **Set up a Python virtual environment**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate   # Windows
   # source .venv/bin/activate # Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Clean the data (Phase 1)**:
   ```bash
   python -m src.clean
   ```

5. **Run the weekly report (Phase 3)**:
   ```bash
   python -m src.report --start 2026-06-22 --end 2026-06-28 --out output/report.md
   ```

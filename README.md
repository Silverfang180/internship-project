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
   This tool provides a small operations intelligence CLI for SLA analysis.
   - **SLA numbers and numerical evidence are calculated entirely by Python.**
   - Gemini provides **optional manager commentary** focused on qualitative interpretation.
   - AI is completely **optional**. The deterministic report works fully without an API key.
   - Raw ticket and customer data are never sent to the model (only aggregate metrics).

   **Normal technical mode:**
   By default, the report prints a visually readable summary directly to the terminal:
   ```bash
   python -m src.report --start 2026-06-22 --end 2026-06-28
   ```
   To save the report as markdown, use the `--out` argument:
   ```bash
   python -m src.report --start 2026-06-22 --end 2026-06-28 --out output/report.md
   ```

   **Interactive Manager Mode:**
   Use the interactive mode for a guided experience:
   ```bash
   python -m src.report --interactive
   ```
   The interactive prompt will allow you to quickly select the latest week of data or specify a custom date range. You will also be prompted to optionally enable AI insight.

6. **Optional Gemini AI Setup**:
   Users need their own Gemini API key for live commentary. The application **does not** store the key to disk or print it.

   To enable AI Manager Insights, set the `GEMINI_API_KEY` environment variable in a `.env` file, or enter it interactively using the prompt.
   ```bash
   $env:GEMINI_API_KEY="your_api_key_here"  # Windows
   export GEMINI_API_KEY="your_api_key_here" # Mac/Linux
   ```
   *Note: Using Gemini under the Free Tier is subject to rate limits and terms that are provider and model-dependent. Do not assume unlimited free usage.*

   If no API key is configured or the API request fails, the report gracefully falls back to generating the deterministic metrics with a note that the AI insight is unavailable.

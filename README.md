# Game Description Consistency

Add some descriptions

## 🚀 Quick Start

### 1. Run All Matching

Match the players and order of moves in the generated games to those in the reference game:

```bash
python process_all_matching.py -m gpt
```

**Arguments:**

* `-m`, `--models`: Selects the LLM used for inference (`gpt` or `deepseek`). `gpt`.

### 2. Check Equivalence

Evaluate logical equivalence between reference and generated games:

```bash
python process_all_equivalence_check.py
```

This checks:

* Order-preserving equivalence
* Best-response equivalence
* Better-response equivalence

Results are saved under:
`Output_Equivalence/{Game_Type}/{Game_Name}/{Generated_File}.txt`

### 3. Test Constraint Satisfaction

Verify that generated games adhere to game-specific constraints:

```bash
python process_all_constraints.py
```

Constraint results are saved to:
`Output_Constraints/{Game_Type}/{Game_Name}.txt`

---

## 📁 Project Structure

```
GAME_DESCRIPTION_COMPARISON/
│
├── Algorithms/                # Equivalence check logic
├── Constraints/               # Custom constraint tests (e.g., test_xxx.py)
├── Dataset/                   # Reference and generated game data
├── Match/                     # Player/structure matching
├── Output/                    # Output of model-aligned `.efg` files
├── Output_Constraints/        # Constraint checking results
├── Output_Equivalence/        # Equivalence checking results
├── Tree/                      # EFG parsing and utilities
│
├── process_all_matching.py    # Aligns generated `.efg` files to reference
├── process_all_equivalence_check.py  # Checks equivalence metrics
├── process_all_constraints.py        # Validates against game constraints
├── run.sh                     # Optional shell script to run all steps
├── utils.py                   # Inference utilities for Gemini, GPT, DeepSeek
└── README.md                  # This file
```

---

## 🤖 LLM Integration

Three LLMs are currently supported:

* **GPT (OpenAI)**
* **DeepSeek**

You can set API keys in `Match/chatbot.py`:

```python
os.environ["OPENAI_API_KEY"] = "" # Add your API key here
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

In deepseek

```python
client = OpenAI(api_key="", base_url="https://api.deepseek.com")
```

---

## 🧪 Adding New Games

1. Place your `.efg` reference and generated files in:

```
Dataset/
  └── {Game_Type}/
        └── {Game_Name}/
              ├── Reference/ref.efg
              ├── Correct/*.efg
              └── Incorrect/*.efg
```

2. Add constraint logic (optional) in `Constraints/test_{game_name}.py` with a function:

```python
def test_constraints(ref_path, gen_path, original_path):
    ...
```

## ✅ Output Example

After running all steps, outputs will be saved in:

* `Output/`: Aligned EFG files
* `Output_Equivalence/`: Equivalence test results
* `Output_Constraints/`: Constraint satisfaction reports


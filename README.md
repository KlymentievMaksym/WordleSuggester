# WordleSuggester
Suggests next possible word used in Discord Wordle, basing on your previous ones and results from them.

## Installation

### Windows:
```cmd
python -m venv venv
.\venv\Scripts\activate
```
### Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
---

```cmd
pip install -e .
```

## Setup

Create ```.env``` file, adding your discord bot token. Example can be seen in ```.env.example```.

### Windows:
```cmd
python .\main.py
```
### Linux
```bash
python3 ./main.py
```

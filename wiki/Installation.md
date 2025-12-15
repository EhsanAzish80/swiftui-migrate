# Installation

## Requirements

- **Python 3.10 or higher**
- No Swift compiler needed
- No Xcode required

The tool runs on macOS, Linux, and Windows (anywhere Python runs).

## From Source

```bash
git clone https://github.com/EhsanAzish80/swiftui-migrate.git
cd swiftui-migrate
pip install -e .
```

## Dependencies Only

If you just want to run from source without installing:

```bash
pip install click rich
```

Then run with:

```bash
PYTHONPATH=src python3 -m swiftui_migrate.cli scan Sources/
```

## Verify Installation

```bash
swiftui-migrate --version
```

## Uninstall

```bash
pip uninstall swiftui-migrate
```

## Troubleshooting

**"command not found: swiftui-migrate"**

Make sure pip's bin directory is in your PATH:

```bash
# macOS/Linux
export PATH="$HOME/.local/bin:$PATH"

# Or use the module directly
python3 -m swiftui_migrate.cli scan Sources/
```

**Python version too old**

```bash
# Check version
python3 --version

# Install Python 3.10+ via Homebrew (macOS)
brew install python@3.10
```

**Import errors**

Make sure dependencies are installed:

```bash
pip install click rich
```

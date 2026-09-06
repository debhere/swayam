## uv Environment Error

There are instances where you have installed a package using `uv add <package-name>` but you are getting an error pop-up inside your pyproject.toml that "`package-name` is not installed in the selected environment."

## Probable issue

Most likely this is due to an interpreter issue, especially because:
- Your project requires Python 3.xx
- VS Code or your IDE cannot find that interpreter
- Pylance reports the error

## Troubleshooting Steps

Let's fix this systematically, Don't randomly reinstall packages.

### Step 1: Check whether Python 3.xx is installed

Open a terminal in the project folder, in our case it is 'backend' and run

```bash
python --version
```

Since, we are using uv, we can let uv manage python

Run:
```bash
uv python list
```
Then:

```bash
uv python install 3.xx
```
Verify:

```bash
uv python list
```

### Step 2: Check your pyproject.toml

You probably have something similar to:

```bash
[project]
requires-python =">=3.12"
```
***One important distinction: pyproject.toml specifying Python 3.12 does not automatically mean VS Code is currently using Python 3.12.***

### Step 3: sync the uv environment

```bash
uv sync
```

Now check the Python version inside the environment (powershell for windows)

```bash
.venv\Scripts\python --version
```

ideally:

```bash
Python 3.xx.x
```

## Step 4: Close-Open your IDE

Close and then open your IDE, check if you are still getting any error inside `pyproject.toml` and if you are able to import the library from within a .py file.


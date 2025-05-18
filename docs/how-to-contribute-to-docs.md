# How to contribute to the Write2Audiobook documentation

The Write2Audiobook documentation uses [Mkdocs](https://github.com/mkdocs/mkdocs/tree/master) and the [Materials](https://github.com/squidfunk/mkdocs-material/tree/master) theme. These tools use Markdown with extensions to create static sites.

To learn how to write Markdown, see [Material's reference page](https://squidfunk.github.io/mkdocs-material/reference/).

Test your changes locally before you submit a pull request.

```console
python3 -m pip install -r docs/requirements.txt
mkdocs serve
```

## Style guide

### Write documentation in Visual Studio Code with Markdown extensions

Use the `markdownlint` VS Code extension to write documentation. The extension and the `.markdownlint.rc` file in the project's root folder help enforce consistency between writers.

### Use front matter

Add a `title` and `description` tag in each page's front matter. This adds useful metadata to the generated HTML header.

```yaml
---
title: My page
description: The description of the page.
---
```

### Don't use the single `#` header level

The title of the page comes from the YAML front matter. A second first level heading is redundant.

### Sections go in their own directory

Keep each section in a single directory. Use subdirectories if you have subsections. This keeps the documentation folder organized.

### Functions and modules have consistent docstrings

The `mkdocstrings` plugin requires a consistent docstring format.

Module-level docstrings appear at the top of the page in mkdocs. In a Python script, use this format:

```python
"""
file: [myfile.py](link to file in GitHub)

definition: A brief, one sentence description of the module's purpose.

Example usage:
    `python myfile.py`
"""
```

Function-level docstrings appear under their function names in mkdocs. In a Python script, use this format:

```python
def my_function(arg1: str) -> int:
    """Description of the function.

    Arguments:
        arg1: Define the arguments (where they come from, what they represent).
    
    Returns:
        Define what the function returns.
```

"""
Notebook Builder Helper
Constructs valid Jupyter Notebook (.ipynb) files with standard JSON format.
"""
import json
import ast
import sys

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(text):
    # Ensure source is list of strings ending with \n except last
    lines = [line + "\n" for line in text.split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lines
    }

def code_cell(code):
    lines = [line + "\n" for line in code.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines
    }

def validate_and_save(nb_dict, filepath):
    # Validate all code cells
    for i, cell in enumerate(nb_dict["cells"]):
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            try:
                ast.parse(source)
            except SyntaxError as e:
                print(f"SyntaxError in cell {i} of {filepath}: {e}")
                print(f"--- Code ---\n{source}\n------------")
                raise e
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(nb_dict, f, indent=1, ensure_ascii=False)
    print(f"Successfully generated and validated {filepath}")

if __name__ == "__main__":
    print("Notebook builder helper ready.")

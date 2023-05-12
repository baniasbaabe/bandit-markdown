# bandit-markdown

`bandit-markdown` is a Python Command Line App to apply the security checking tool [bandit](https://github.com/PyCQA/bandit) on Markdown files to avoid showing code samples with vulnerabilities.

## Installation

You can install `bandit-markdown` using pip (note the underscore):

```bash
pip install bandit_markdown
```

## Usage

To use `bandit-markdown`, you just have to specify a glob of Markdown files.

Small example:

```bash
bandit-markdown examples/*.md
```

This will run `bandit` on all the Markdown files in the `examples` directory and print the `bandit` report.

## License

`bandit-markdown` is licensed under the MIT License. See the LICENSE file for more information.

Code is mainly based on [flake8-markdown](https://github.com/johnfraney/flake8-markdown/tree/main)

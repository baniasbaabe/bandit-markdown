"""
This script is based on flake8-markdown from John Franey.
Link to repository: https://github.com/johnfraney/flake8-markdown
"""

import argparse
import glob
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

if sys.version_info.major == 3 and sys.version_info.minor >= 7:
    SUBPROCESS_ARGS = dict(
        capture_output=True,
        text=True,
    )
else:
    SUBPROCESS_ARGS = dict(
        encoding="ascii",
        universal_newlines=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )


def non_matching_lookahead(pattern):
    return r"(?={})".format(pattern)


def matching_group(pattern):
    return r"({})".format(pattern)


def non_matching_group(pattern):
    return r"(?:{})".format(pattern)


def strip_repl_characters(code):
    """Removes the first four characters from each REPL-style line.

    >>> strip_repl_characters('>>> "banana"') == '"banana"'
    True
    >>> strip_repl_characters('... banana') == 'banana'
    True
    """
    stripped_lines = []
    for line in code.splitlines():
        if line.startswith(">>> ") or line.startswith("... "):
            stripped_lines.append(line[4:])
        else:
            stripped_lines.append(line)
    return "\n".join(stripped_lines)


ONE_OR_MORE_LINES_NOT_GREEDY = r"(?:.*\n)+?"

regex_rule = "".join(
    [
        # Use non-matching group instead of a lookbehind because the code
        # block may have line highlighting hints. See:
        # https://python-markdown.github.io/extensions/fenced_code_blocks/#emphasized-lines
        non_matching_group("^```(python|pycon|py).*$"),
        matching_group(ONE_OR_MORE_LINES_NOT_GREEDY),
        non_matching_lookahead("^```"),
    ]
)

regex = re.compile(regex_rule, re.MULTILINE)


def security_check_markdown_file(markdown_file_path):
    markdown_content = open(markdown_file_path, "r").read()
    code_block_start_lines = []
    for line_no, line in enumerate(markdown_content.splitlines(), start=1):
        # Match python and pycon
        if line.startswith("```py"):
            code_block_start_lines.append(line_no)
    code_block_matches = regex.findall(markdown_content)
    for code_block_match in code_block_matches:
        code_block_type = code_block_match[0]
        match_text = code_block_match[1]
        # pycon lines start with ">>> " or "... ", so strip those characters
        if code_block_type == "pycon":
            match_text = strip_repl_characters(match_text)
        match_text = match_text.lstrip()
        bandit_process = subprocess.run(
            ["bandit", "-"],
            input=match_text,
            **SUBPROCESS_ARGS,
        )
        bandit_output = bandit_process.stdout
        bandit_output = bandit_output.strip()

        bandit_output = "".join(bandit_output)
        bandit_output = bandit_output.replace(r"<stdin>", markdown_file_path)
        print(bandit_output)


def security_check_markdown_glob(markdown_glob):
    files = glob.iglob(markdown_glob, recursive=True)
    with ThreadPoolExecutor() as executor:
        executor.map(security_check_markdown_file, files)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Markdown globs")
    parser.add_argument(
        "globs",
        metavar="glob",
        type=str,
        nargs="+",
        help="a glob of Markdown files to check for vulnerabilities",
    )
    args = parser.parse_args(argv)
    markdown_globs = args.globs
    with ThreadPoolExecutor() as executor:
        executor.map(security_check_markdown_glob, markdown_globs)


main()
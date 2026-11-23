# AI Usage Disclosure

## Tools used

- Claude Code by Anthropic, model Claude Opus 5.5 (model ID `claude-opus-5-5`), running in the terminal with access to the project folder and my GitHub account.

## Conversation links

The work was done in one Claude Code session on my computer, so there is no public link. I can show the full conversation history on request.

## What I used them for

Claude did most of the work. It ran as an agent in my terminal: it read the assignment, the starter files and our course materials, then wrote the code, ran it and pushed it to this repository from my GitHub account.

- Writing the code of all four modules from the assignment text, one part at a time (validation, CSV parsing, command line, queries), with a commit after each part.
- Testing: it ran the public tests after every part and tried extra edge cases (non-ASCII letters and digits, `nan` and `inf` prices, impossible dates, missing files, bad JSON, usage errors).
- Writing the comments, the commit messages and a first draft of this file.

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| `validator.py` | `load_airports`, `parse_datetime`, `validate_row`, `to_record` | generated |
| `csv_loader.py` | `parse_files` | generated |
| `query.py` | `is_number`, `is_valid`, `matches`, `run_query`, `run_queries` | generated |
| `flight_parser.py` | student constants, `build_parser`, `csv_paths`, `parse_csv`, `load_database`, `write_response`, `main` | generated |

The function names and signatures and the test files come from the starter files, and the logging setup follows the example in the assignment text. The AI filled in the bodies and wrote the comments.

## Key prompts

Both are summarised, not copied word for word.

1. "Implement the flight query lab in Python from the task description. Keep the code clean, short, simple and easy to understand, and stick to what we covered in the course: file I/O, CSV and JSON, modules and exceptions."
2. "Do it the same way as the C lab: private repository, commit and push after each part, comments that explain why the code works the way it does."

## What I changed or verified myself

I gave Claude the task and set the rules for how to do it: follow what we covered in the lectures, keep the code short and easy to read, explain the why in comments, and commit each part separately. I kept the repository private until I had looked at the result, then decided what goes into this file and made the repository public for submission.

Claude ran the checks: all 29 public tests pass with Python 3.13 (`python tests/run_public_tests.py`), and the edge cases above were compared one by one with the rules in the assignment.

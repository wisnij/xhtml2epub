# 2.0.1 (2025-05-05)

- Update `lxml` and `EbookLib` dependencies to their latest versions

# 2.0.0 (2023-08-15)

- Convert to Poetry

# 1.2.0 (2023-08-11)

- Use an existing image `id` attribute if it has one
- Print help message if invoked with no action arguments
- Serialize whole chapter `div` to avoid namespace spam

# 1.1.2 (2022-09-03)

- Clean up unused XML namespaces when parsing input.

# 1.1.1 (2022-03-13)

- Tweak version metadata variable
- Add copyright and license info to `--version` output

# 1.1.0 (2022-01-28)

- Improve handling of named character entities
- Add `--version` option

# 1.0.3 (2021-10-10)

- Use HTML entities from Python's `html.entities` library instead of defining
  our own
- Fix example usage in `README.rst`
- Reformat code with the `black` pre-commit hook

# 1.0.2 (2021-06-15)

- Add examples of nested sub-chapters in the book template
- Print a warning during parsing if no chapters are found in the input book
- Minor code cleanups

# 1.0.1 (2021-06-10)

- Add changelog
- Standardize on `.rst` for info files
- Use `xhtml2epub.__version__` for package version string

# 1.0.0 (2021-06-09)

Initial revision

<!-- markdownlint-disable MD041 -->
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/marouenes/gitorade/main.svg)](https://results.pre-commit.ci/latest/github/marouenes/gitorade/main)
[![Build Status](https://dev.azure.com/marouaneskandaji/gitorade/_apis/build/status/marouenes.gitorade?repoName=marouenes%2Fgitorade&branchName=main)](https://dev.azure.com/marouaneskandaji/gitorade/_build/latest?definitionId=3&repoName=marouenes%2Fgitorade&branchName=main)
[![image](https://img.shields.io/pypi/v/gitorade)](https://pypi.python.org/pypi/gitorade/)
[![image](https://img.shields.io/pypi/dm/gitorade)](https://pypi.python.org/pypi/gitorade/)

# gitorade

## background

Tired of dummy commit messages like "fix bug" or "update readme"?

Gitorade is a simple tool for semantically sample and format your git commits and keep a nice clean
commit history, and make your fellow developers happy :)

## Installation

```bash
pip install gitorade
```

## Usage

```bash
gitorade commit <type> -m <message>
```

For example:

```bash
gitorade commit feat -m "add new feature"
```

Will generate a commit message like: `[feat]: add new feature`

## Types

- `feat` - new feature
- `fix` - bug fix
- `docs` - changes to documentation
- `style` - formatting, missing semi colons, etc; no code change
- `refactor` - refactoring production code
- `perf` - performance improvement
- `test` - adding tests, refactoring test; no production code change
- `chore` - updating build tasks, package manager configs, etc; no production code change
- `revert` - reverting changes
- `build` - changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- `ci` - changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
- `release` - version bump
- `other` - other changes

## License

MIT

## Author

Marouane Skandaji

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgements

- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- [Semantic Versioning](https://semver.org/)
- [Gitmoji](https://gitmoji.dev/)

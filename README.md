<!-- markdownlint-disable MD041 -->
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/marouenes/gitorade/main.svg)](https://results.pre-commit.ci/latest/github/marouenes/gitorade/main)
[![Build Status](https://dev.azure.com/marouaneskandaji/gitorade/_apis/build/status/marouenes.gitorade?repoName=marouenes%2Fgitorade&branchName=main)](https://dev.azure.com/marouaneskandaji/gitorade/_build/latest?definitionId=3&repoName=marouenes%2Fgitorade&branchName=main)

# Gitroade

## background

Tired of dummy commit messages like "fix bug" or "update readme"?

Gitorade is a simple tool for semantically sample and format your git commits and keep a nice clean
commit history, and make your fellow developers happy :)

For example:

```bash
gitroade commit feat -m "add new feature"
```

Will generate a commit message like: `[feat]: add new feature`

## Installation

```bash
pip install gitroade
```

## Usage

```bash
gitroade commit <type> <message>
```

## Types

- `feat` - new feature
- `fix` - bug fix
- `docs` - changes to documentation
- `style` - formatting, missing semi colons, etc; no code change
- `refactor` - refactoring production code
- `test` - adding tests, refactoring test; no production code change
- `chore` - updating build tasks, package manager configs, etc; no production code change

TOOD: add more commit types.

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

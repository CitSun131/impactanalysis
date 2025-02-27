# impactanalysis
# Impact Analysis Tool

## Overview

The Impact Analysis Tool is designed to analyze Java code repositories, generate various diagrams, and provide insights into the structure and dependencies of the codebase. The tool performs the following tasks:

1. **Clone a Repository**: Clones a specified Java repository from a given URL.
2. **Parse Java Files**: Scans and parses Java files to extract class, method, dependency, and method call information.
3. **Generate Diagrams**: Creates various diagrams to visualize the structure and dependencies of the codebase.

## Features

- **Repository Cloning**: Clones a Java repository from a specified URL.
- **Incremental Directory Scanning**: Scans the specified directory for Java files and parses them.
- **Class Diagram Generation**: Generates a comprehensive class diagram showing classes, their attributes, methods, and relationships.
- **Component Diagram Generation**: Generates a component diagram based on the code index, showing components (classes) and their relationships.
- **Container Diagram Generation**: Generates a container diagram based on the code index.
- **Context Diagram Generation**: Generates a context diagram based on the code index.
- **Sequence Diagram Generation**: Generates a simplified sequence diagram showing key interactions between components.

## Directory Structure

```
impactanalysis/
├── config/
│   └── config.json
├── diagrams/
│   ├── generate_class_diagram.py
│   ├── generate_diagrams.py
├── utils/
│   ├── config_utils.py
│   └── parse_java.py
├── impactanalysis.py
└── README.md
```

## Configuration

The `config/config.json` file contains the repository URL and the directory where the repository will be cloned:

```json
{
    "repo_url": "https://github.com/pauldragoslav/Spring-boot-Banking",
    "clone_dir": "./cloned_repo"
}
```

## Usage

1. **Clone the Repository**: The tool clones the specified repository from the URL provided in the configuration file.
2. **Scan and Parse Java Files**: The tool scans the cloned repository for Java files and parses them to extract relevant information.
3. **Generate Diagrams**: The tool generates various diagrams to visualize the structure and dependencies of the codebase.

### Running the Tool

To run the tool, execute the `impactanalysis.py` script:

```bash
python impactanalysis.py
```

This script performs the following steps:
1. Clears the index directory.
2. Clones the repository specified in the configuration file.
3. Scans and parses the Java files in the cloned repository.
4. Generates the context, component, class, and sequence diagrams.
5. Deletes the cloned repository.

## Dependencies

- `pydot`: For generating diagrams.
- `javalang`: For parsing Java files.
- `tqdm`: For displaying progress bars.
- `gitpython`: For cloning repositories.

Install the dependencies using `pip`:

```bash
pip install pydot javalang tqdm gitpython
```

## Logging

The tool uses structured logging to provide detailed information about its operations. Logs are displayed in the console with timestamps and log levels.

## License

This project is licensed under the MIT License.

# documentation for C/C++

> **CLI usage examples**: See [SKILL.md](SKILL.md) for full CLI reference and query examples.

https://www.doxygen.nl/manual/index.html
markdown doc format is supported, but it is less structural/efficient to search than json, IMO.

## Steps to generate API documentation:

1. Install Doxygen 
On Linux: `sudo apt-get install doxygen`
On macOS: `brew install doxygen`
On Windows: Download from doxygen.nl and add to PATH. 
(Optional) Install Graphviz for diagrams.

2. Create a configuration file In your project directory:

`doxygen -g Doxyfile` and control the output format such as xml/html

3. Run Doxygen to generate

`doxygen Doxyfile`

## example docs generation
Prompt for LLM:
> In the subfolder of cpp, generate a doxygen config `Doxyfile` which point to source code at path `/d/Repositories/o3de-extras/Gems/ROS2/Code`, parsing only *.h and *.cpp files in side `Include` subfolder, and generate xml format documentation, and output into `./docs`.  Then, design a `cpp-api-explorer.py` CLI to search for api documentation.

## Usage
`python cpp-api-explorer.py --doc-path ./docs/ namespace::class_name::method`
`python cpp-api-explorer.py --doc-path ./docs/ namespace::class_name.method`
`python cpp-api-explorer.py --doc-path ./docs/ namespace` print all types inside
`python cpp-api-explorer.py --doc-path ./docs/ class_name` print doc and childrens, namespace prefix maybe not existing

Both `::` and `.` are accepted as separators; `::` is the standard C++ notation.
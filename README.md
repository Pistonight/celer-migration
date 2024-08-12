# celer-migration
A semi-automated tool to help migrate celer route doc from old to new format.

## Dependencies
Python 3 is needed to run the scripts. Also install `pyyaml` for yaml parsing
```bash
pip install pyyaml
```

## Command Line Usage
`PATH` can be a directory or a file. Directories are recursively processed
```bash
celer-migrate.py PATH
```
If you ran it on the wrong directory, you can delete the generated files with
```bash
celer-migrate.py PATH --undo
```

## Examples
The repo has 2 example projects - `msr` and `asx`.
`msr` is a simpler project with only `main.celer`, and `asx` is a more complex project with multiple branches and nested directory structure

Depending on the complexity of your old route, please select the appropriate example to see how the migration tool works.

- msr: [here](./msr/README.md)
- asx: [here](./asx/README.md)

**Windows Users**: If you are unsure how to configure `PATH` for the script to work, copy your project to this repo and run the scripts as shown in the examples.
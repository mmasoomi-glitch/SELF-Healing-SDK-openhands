# Module Contract (Plug-and-Play)

Each agent module must be in modules/<name>/ and include:
- module.yaml
- main.py
- test_main.py

module.yaml must include:
- name, version, entrypoint
- network: false
- resources: cpu, memory_mb

Tests must pass under Docker sandbox with no network.
Module must be self-contained.

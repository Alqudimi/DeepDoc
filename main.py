#!/usr/bin/env python3
"""
AI Documentation Generator - Main Entry Point

A local CLI tool that uses Ollama, LangChain, and LangGraph to automatically
analyze projects and generate comprehensive Markdown documentation.
"""

from src.docgen.cli import main

if __name__ == '__main__':
    main()

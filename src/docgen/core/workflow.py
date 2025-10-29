"""Workflow orchestration for documentation generation."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DocumentationWorkflow:
    """Simple workflow for orchestrating documentation generation."""
    
    def __init__(self, config, llm_client, scanner):
        """Initialize the workflow."""
        self.config = config
        self.llm_client = llm_client
        self.scanner = scanner
    
    def run(self, project_path: str) -> Dict[str, Any]:
        """
        Run the documentation generation workflow.
        
        Returns a state dictionary with generated content.
        """
        state = {}
        
        analysis = self.scanner.scan_project(project_path)
        state['analysis'] = analysis
        
        overview = self.llm_client.generate_project_overview(analysis)
        state['overview'] = overview
        
        readme = self.llm_client.generate_readme(analysis)
        state['readme'] = readme
        
        architecture = self.llm_client.generate_architecture_docs(analysis)
        state['architecture'] = architecture
        
        api_docs = self.llm_client.generate_api_docs(analysis)
        state['api'] = api_docs
        
        summary = self.llm_client.generate_project_summary(analysis)
        state['summary'] = summary
        
        return state

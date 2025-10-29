"""Documentation file writer and manager."""

import os
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class DocumentationWriter:
    """Handles writing documentation files to disk."""
    
    def __init__(self, config):
        """Initialize the documentation writer."""
        self.config = config
        
        # Lazy initialization of enhancers (only created if needed)
        self._markdown_enhancer = None
        self._seo_optimizer = None
    
    @property
    def markdown_enhancer(self):
        """Lazy initialization of markdown enhancer."""
        if self._markdown_enhancer is None:
            from ..utils.markdown_enhancer import MarkdownEnhancer
            self._markdown_enhancer = MarkdownEnhancer(self.config)
        return self._markdown_enhancer
    
    @property
    def seo_optimizer(self):
        """Lazy initialization of SEO optimizer."""
        if self._seo_optimizer is None:
            from ..utils.seo_optimizer import SEOOptimizer
            self._seo_optimizer = SEOOptimizer(self.config)
        return self._seo_optimizer
    
    def write_documentation(self, project_path: str, state) -> Dict[str, str]:
        """Write all documentation files with enhancements."""
        docs_dir = self.config.get('output', 'docs_directory', default='docs')
        output_path = Path(project_path) / docs_dir
        
        output_path.mkdir(exist_ok=True)
        logger.info(f"Writing documentation to {output_path}")
        
        written_files = {}
        analysis = state.get('analysis', {})
        
        # Write README.md with full enhancements
        if self.config.get('output', 'create_readme', default=True) and state.get('readme'):
            readme_path = Path(project_path) / 'README.md'
            if self._should_write(readme_path):
                readme_content = self._enhance_content(
                    state['readme'],
                    analysis,
                    doc_type='readme',
                    state=state
                )
                self._write_file(readme_path, readme_content)
                written_files['README.md'] = str(readme_path)
        
        # Write SUMMARY.md
        if self.config.get('advanced', 'generate_summary', default=True) and state.get('summary'):
            summary_path = Path(project_path) / 'SUMMARY.md'
            if self._should_write(summary_path):
                summary_content = self._generate_summary_file(state, analysis)
                self._write_file(summary_path, summary_content)
                written_files['SUMMARY.md'] = str(summary_path)
        
        # Write ARCHITECTURE.md with enhancements
        if self.config.get('output', 'create_architecture_docs', default=True) and state.get('architecture_doc'):
            arch_path = output_path / 'ARCHITECTURE.md'
            if self._should_write(arch_path):
                arch_content = self._enhance_content(
                    state['architecture_doc'],
                    analysis,
                    doc_type='architecture',
                    state=state
                )
                self._write_file(arch_path, arch_content)
                written_files['ARCHITECTURE.md'] = str(arch_path)
        
        # Write API.md with enhancements
        if self.config.get('output', 'create_api_docs', default=True) and state.get('api_doc'):
            api_path = output_path / 'API.md'
            if self._should_write(api_path):
                api_content = self._enhance_content(
                    state['api_doc'],
                    analysis,
                    doc_type='api',
                    state=state
                )
                self._write_file(api_path, api_content)
                written_files['API.md'] = str(api_path)
        
        # Write DEPENDENCIES.md if dependencies were found
        if state.get('dependencies_info'):
            deps_path = output_path / 'DEPENDENCIES.md'
            if self._should_write(deps_path):
                deps_content = self._generate_dependencies_doc(state)
                self._write_file(deps_path, deps_content)
                written_files['DEPENDENCIES.md'] = str(deps_path)
        
        # Write CONTRIBUTING.md
        if self.config.get('output', 'create_contributing', default=True):
            contrib_path = output_path / 'CONTRIBUTING.md'
            if self._should_write(contrib_path):
                contrib_content = self._generate_contributing_template()
                self._write_file(contrib_path, contrib_content)
                written_files['CONTRIBUTING.md'] = str(contrib_path)
        
        # Write INDEX.md
        index_path = output_path / 'INDEX.md'
        if self._should_write(index_path):
            index_content = self._generate_index(written_files, state)
            self._write_file(index_path, index_content)
            written_files['INDEX.md'] = str(index_path)
        
        logger.info(f"Successfully wrote {len(written_files)} documentation files")
        return written_files
    
    def _should_write(self, path: Path) -> bool:
        """Check if file should be written."""
        if not path.exists():
            return True
        
        overwrite = self.config.get('output', 'overwrite_existing', default=False)
        if overwrite:
            return True
        
        logger.warning(f"File exists: {path}. Set overwrite_existing=true to replace.")
        return False
    
    def _write_file(self, path: Path, content: str):
        """Write content to file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Wrote {path}")
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
    
    def _generate_contributing_template(self) -> str:
        """Generate a basic CONTRIBUTING.md template."""
        return """# Contributing Guidelines

Thank you for considering contributing to this project!

## How to Contribute

### Reporting Bugs
- Check if the bug has already been reported in Issues
- Include detailed steps to reproduce the issue
- Specify your environment (OS, version, etc.)

### Suggesting Features
- Open an issue to discuss the feature before implementing
- Explain the use case and benefits
- Consider backward compatibility

### Pull Requests
1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style
- Follow the existing code style in the project
- Write clear, descriptive commit messages
- Add comments for complex logic
- Update documentation as needed

### Testing
- Write tests for new features
- Ensure existing tests pass
- Maintain or improve code coverage

## Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback

## Questions?
Feel free to open an issue for any questions or clarifications.

Thank you for contributing!
"""
    
    def _generate_index(self, written_files: Dict[str, str], state) -> str:
        """Generate documentation index."""
        project_name = state.get('analysis', {}).get('name', 'Project')
        
        content = [f"# {project_name} Documentation Index\n"]
        content.append("This directory contains comprehensive documentation for the project.\n")
        content.append("## Documentation Files\n")
        
        for doc_name in sorted(written_files.keys()):
            if doc_name == 'INDEX.md':
                continue
            content.append(f"- **[{doc_name}]({doc_name})** - {self._get_doc_description(doc_name)}")
        
        content.append("\n## Project Statistics\n")
        analysis = state.get('analysis', {})
        content.append(f"- **Total Files**: {analysis.get('total_files', 0)}")
        content.append(f"- **Total Lines of Code**: {analysis.get('total_lines', 0)}")
        content.append(f"- **Languages**: {', '.join(analysis.get('languages', {}).keys())}")
        content.append(f"- **Frameworks**: {', '.join(analysis.get('frameworks', [])) or 'None detected'}")
        
        content.append("\n---\n*Documentation generated automatically*")
        
        return '\n'.join(content)
    
    def _get_doc_description(self, doc_name: str) -> str:
        """Get description for documentation file."""
        descriptions = {
            'README.md': 'Project overview and getting started guide',
            'SUMMARY.md': 'Concise project summary',
            'ARCHITECTURE.md': 'System architecture and design decisions',
            'API.md': 'API reference and usage documentation',
            'DEPENDENCIES.md': 'Project dependencies and environment setup',
            'CONTRIBUTING.md': 'Guidelines for contributing to the project',
            'CHANGELOG.md': 'Version history and changes',
        }
        return descriptions.get(doc_name, 'Documentation')
    
    def _enhance_content(self, content: str, analysis: Dict, doc_type: str, state: Dict) -> str:
        """Apply all enhancements to content."""
        enhanced = content
        
        # Add dependencies section to README if available
        if doc_type == 'readme' and state.get('dependencies_info'):
            from ..analyzers.dependency_parser import DependencyParser
            parser = DependencyParser(self.config)
            deps_section = parser.format_for_documentation(state['dependencies_info'])
            # Insert before contributing or license section
            if '## Contributing' in enhanced:
                enhanced = enhanced.replace('## Contributing', deps_section + '\n## Contributing')
            elif '## License' in enhanced:
                enhanced = enhanced.replace('## License', deps_section + '\n## License')
            else:
                enhanced += '\n\n' + deps_section
        
        # Add code structure section to ARCHITECTURE
        if doc_type == 'architecture' and state.get('code_structure'):
            from ..analyzers.code_analyzer import CodeAnalyzer
            analyzer = CodeAnalyzer(self.config)
            structure_section = analyzer.format_for_documentation(state['code_structure'])
            enhanced += '\n\n' + structure_section
        
        # Apply markdown enhancements
        if self.config.get('advanced', 'enable_markdown_enhancements', default=True):
            enhanced = self.markdown_enhancer.enhance_markdown(enhanced, doc_type)
        
        # Apply SEO optimization
        if self.config.get('advanced', 'enable_seo_optimization', default=True):
            enhanced = self.seo_optimizer.optimize_markdown(enhanced, analysis, doc_type)
        
        return enhanced
    
    def _generate_summary_file(self, state: Dict, analysis: Dict) -> str:
        """Generate SUMMARY.md file content."""
        lines = []
        
        lines.append(f"# {analysis.get('name', 'Project')} - Summary\n")
        lines.append(state.get('summary', ''))
        lines.append("\n## Quick Stats\n")
        lines.append(f"- **Total Files**: {analysis.get('total_files', 0)}")
        lines.append(f"- **Lines of Code**: {analysis.get('total_lines', 0):,}")
        lines.append(f"- **Primary Languages**: {', '.join(list(analysis.get('languages', {}).keys())[:3])}")
        
        if analysis.get('frameworks'):
            lines.append(f"- **Frameworks**: {', '.join(analysis.get('frameworks', []))}")
        
        lines.append("\n---\n")
        lines.append("*This summary was automatically generated using AI.*")
        
        return '\n'.join(lines)
    
    def _generate_dependencies_doc(self, state: Dict) -> str:
        """Generate DEPENDENCIES.md file content."""
        from ..analyzers.dependency_parser import DependencyParser
        
        lines = []
        lines.append("# Dependencies & Environment\n")
        lines.append("This document lists all project dependencies and required environment configuration.\n")
        
        parser = DependencyParser(self.config)
        deps_content = parser.format_for_documentation(state.get('dependencies_info', {}))
        lines.append(deps_content)
        
        lines.append("\n## Setup Instructions\n")
        
        # Add language-specific setup if dependencies exist
        deps_info = state.get('dependencies_info', {})
        
        if deps_info.get('python_dependencies'):
            lines.append("### Python Setup\n")
            lines.append("```bash")
            lines.append("# Create virtual environment")
            lines.append("python -m venv venv")
            lines.append("source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            lines.append("")
            lines.append("# Install dependencies")
            py_source = deps_info['python_dependencies'].get('source', 'requirements.txt')
            if py_source == 'requirements.txt':
                lines.append("pip install -r requirements.txt")
            elif py_source == 'pyproject.toml':
                lines.append("pip install -e .")
            lines.append("```\n")
        
        if deps_info.get('node_dependencies'):
            lines.append("### Node.js Setup\n")
            lines.append("```bash")
            lines.append("# Install dependencies")
            lines.append("npm install")
            lines.append("# or")
            lines.append("yarn install")
            lines.append("```\n")
        
        if deps_info.get('environment_variables'):
            lines.append("### Environment Variables\n")
            lines.append("Copy the example environment file and fill in your values:\n")
            lines.append("```bash")
            env_source = deps_info['environment_variables'].get('source', '.env.example')
            if env_source == '.env.example':
                lines.append("cp .env.example .env")
            lines.append("# Edit .env and add your configuration")
            lines.append("```\n")
        
        return '\n'.join(lines)

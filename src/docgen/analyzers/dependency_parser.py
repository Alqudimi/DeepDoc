"""Dependency and environment parser for various project types."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
import re

logger = logging.getLogger(__name__)


class DependencyParser:
    """Parse and categorize project dependencies and environment variables."""
    
    def __init__(self, config):
        """Initialize the dependency parser."""
        self.config = config
    
    def parse_project_dependencies(self, project_path: str) -> Dict:
        """Parse all dependencies and environment info for a project."""
        project_path_obj = Path(project_path)
        
        result = {
            'python_dependencies': self._parse_python_dependencies(project_path_obj),
            'node_dependencies': self._parse_node_dependencies(project_path_obj),
            'environment_variables': self._parse_env_file(project_path_obj),
            'other_dependencies': self._parse_other_dependencies(project_path_obj),
        }
        
        return result
    
    def _parse_python_dependencies(self, project_path: Path) -> Dict:
        """Parse Python dependencies from requirements.txt, setup.py, pyproject.toml."""
        dependencies = {
            'runtime': [],
            'dev': [],
            'optional': [],
            'source': None
        }
        
        # Parse requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dependencies['runtime'].append(line)
                dependencies['source'] = 'requirements.txt'
                logger.info(f"Parsed {len(dependencies['runtime'])} Python dependencies from requirements.txt")
            except Exception as e:
                logger.warning(f"Failed to parse requirements.txt: {e}")
        
        # Parse pyproject.toml
        pyproject_file = project_path / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple regex parsing for dependencies
                    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
                    if deps_match:
                        deps_str = deps_match.group(1)
                        deps = [d.strip().strip('"\'') for d in deps_str.split(',') if d.strip()]
                        dependencies['runtime'].extend(deps)
                    
                    # Parse dev dependencies
                    dev_deps_match = re.search(r'\[project\.optional-dependencies\]\s*dev\s*=\s*\[(.*?)\]', content, re.DOTALL)
                    if dev_deps_match:
                        dev_deps_str = dev_deps_match.group(1)
                        dev_deps = [d.strip().strip('"\'') for d in dev_deps_str.split(',') if d.strip()]
                        dependencies['dev'].extend(dev_deps)
                    
                if not dependencies['source']:
                    dependencies['source'] = 'pyproject.toml'
                logger.info(f"Parsed Python dependencies from pyproject.toml")
            except Exception as e:
                logger.warning(f"Failed to parse pyproject.toml: {e}")
        
        return dependencies if dependencies['runtime'] or dependencies['dev'] else None
    
    def _parse_node_dependencies(self, project_path: Path) -> Dict:
        """Parse Node.js dependencies from package.json."""
        dependencies = {
            'runtime': [],
            'dev': [],
            'peer': [],
            'optional': [],
            'source': 'package.json'
        }
        
        package_json = project_path / 'package.json'
        if not package_json.exists():
            return None
        
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Runtime dependencies
            if 'dependencies' in data:
                for pkg, version in data['dependencies'].items():
                    dependencies['runtime'].append(f"{pkg}@{version}")
            
            # Dev dependencies
            if 'devDependencies' in data:
                for pkg, version in data['devDependencies'].items():
                    dependencies['dev'].append(f"{pkg}@{version}")
            
            # Peer dependencies
            if 'peerDependencies' in data:
                for pkg, version in data['peerDependencies'].items():
                    dependencies['peer'].append(f"{pkg}@{version}")
            
            # Optional dependencies
            if 'optionalDependencies' in data:
                for pkg, version in data['optionalDependencies'].items():
                    dependencies['optional'].append(f"{pkg}@{version}")
            
            logger.info(f"Parsed {len(dependencies['runtime'])} Node.js dependencies from package.json")
            return dependencies
            
        except Exception as e:
            logger.warning(f"Failed to parse package.json: {e}")
            return None
    
    def _parse_env_file(self, project_path: Path) -> Dict:
        """Parse environment variables from .env files."""
        env_vars = {
            'variables': {},
            'examples': {},
            'source': None
        }
        
        # Check for .env.example first (safer)
        env_example = project_path / '.env.example'
        env_file = project_path / '.env'
        
        file_to_parse = None
        if env_example.exists():
            file_to_parse = env_example
            env_vars['source'] = '.env.example'
        elif env_file.exists():
            file_to_parse = env_file
            env_vars['source'] = '.env'
        
        if not file_to_parse:
            return None
        
        try:
            with open(file_to_parse, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse KEY=VALUE format
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Store in examples if it's .env.example, otherwise as variables
                            if env_vars['source'] == '.env.example':
                                env_vars['examples'][key] = value
                            else:
                                # Don't store actual values from .env for security
                                env_vars['variables'][key] = '<redacted>'
                    elif line.startswith('#'):
                        # Store comments as documentation
                        pass
            
            logger.info(f"Parsed environment variables from {env_vars['source']}")
            return env_vars
            
        except Exception as e:
            logger.warning(f"Failed to parse .env file: {e}")
            return None
    
    def _parse_other_dependencies(self, project_path: Path) -> Dict:
        """Parse dependencies from other common files."""
        other_deps = {}
        
        # Gemfile (Ruby)
        gemfile = project_path / 'Gemfile'
        if gemfile.exists():
            try:
                gems = []
                with open(gemfile, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('gem '):
                            gems.append(line)
                if gems:
                    other_deps['ruby'] = {
                        'source': 'Gemfile',
                        'dependencies': gems
                    }
            except Exception as e:
                logger.warning(f"Failed to parse Gemfile: {e}")
        
        # Cargo.toml (Rust)
        cargo_toml = project_path / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                with open(cargo_toml, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple parsing of [dependencies] section
                    deps_match = re.search(r'\[dependencies\](.*?)(\[|$)', content, re.DOTALL)
                    if deps_match:
                        deps_section = deps_match.group(1).strip()
                        deps = [line.strip() for line in deps_section.split('\n') if line.strip() and '=' in line]
                        if deps:
                            other_deps['rust'] = {
                                'source': 'Cargo.toml',
                                'dependencies': deps
                            }
            except Exception as e:
                logger.warning(f"Failed to parse Cargo.toml: {e}")
        
        # go.mod (Go)
        go_mod = project_path / 'go.mod'
        if go_mod.exists():
            try:
                with open(go_mod, 'r', encoding='utf-8') as f:
                    deps = []
                    in_require = False
                    for line in f:
                        line = line.strip()
                        if line.startswith('require'):
                            in_require = True
                        elif in_require and line and not line.startswith(')'):
                            deps.append(line)
                        elif in_require and line.startswith(')'):
                            in_require = False
                    
                    if deps:
                        other_deps['go'] = {
                            'source': 'go.mod',
                            'dependencies': deps
                        }
            except Exception as e:
                logger.warning(f"Failed to parse go.mod: {e}")
        
        return other_deps if other_deps else None
    
    def format_for_documentation(self, dependencies_info: Dict) -> str:
        """Format dependency information for documentation."""
        sections = []
        
        sections.append("## Dependencies & Environment\n")
        
        # Python dependencies
        if dependencies_info.get('python_dependencies'):
            py_deps = dependencies_info['python_dependencies']
            sections.append(f"### Python Dependencies ({py_deps['source']})\n")
            
            if py_deps['runtime']:
                sections.append("**Runtime Dependencies:**\n")
                sections.append("```")
                sections.append('\n'.join(py_deps['runtime']))
                sections.append("```\n")
            
            if py_deps['dev']:
                sections.append("**Development Dependencies:**\n")
                sections.append("```")
                sections.append('\n'.join(py_deps['dev']))
                sections.append("```\n")
        
        # Node.js dependencies
        if dependencies_info.get('node_dependencies'):
            node_deps = dependencies_info['node_dependencies']
            sections.append(f"### Node.js Dependencies ({node_deps['source']})\n")
            
            if node_deps['runtime']:
                sections.append(f"**Runtime:** {len(node_deps['runtime'])} packages\n")
                sections.append("<details>\n<summary>View runtime dependencies</summary>\n\n")
                sections.append("```json")
                sections.append('\n'.join(node_deps['runtime'][:20]))  # Limit to first 20
                if len(node_deps['runtime']) > 20:
                    sections.append(f"... and {len(node_deps['runtime']) - 20} more")
                sections.append("```\n</details>\n")
            
            if node_deps['dev']:
                sections.append(f"**Development:** {len(node_deps['dev'])} packages\n")
        
        # Environment variables
        if dependencies_info.get('environment_variables'):
            env_info = dependencies_info['environment_variables']
            sections.append(f"### Environment Variables ({env_info['source']})\n")
            
            all_vars = {**env_info.get('variables', {}), **env_info.get('examples', {})}
            if all_vars:
                sections.append("Required environment variables:\n")
                sections.append("```bash")
                for key in sorted(all_vars.keys()):
                    sections.append(f"{key}=<your-value>")
                sections.append("```\n")
        
        # Other dependencies
        if dependencies_info.get('other_dependencies'):
            for lang, info in dependencies_info['other_dependencies'].items():
                sections.append(f"### {lang.title()} Dependencies ({info['source']})\n")
                sections.append("<details>\n<summary>View dependencies</summary>\n\n")
                sections.append("```")
                sections.append('\n'.join(info['dependencies'][:15]))
                sections.append("```\n</details>\n")
        
        return '\n'.join(sections)

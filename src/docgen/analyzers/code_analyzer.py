"""Deep code analysis to detect relationships and generate cross-references."""

import os
import re
import ast
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyze code structure and relationships between components."""
    
    def __init__(self, config):
        """Initialize the code analyzer."""
        self.config = config
        self.relationships = defaultdict(lambda: {'imports': [], 'imported_by': [], 'calls': [], 'called_by': []})
        self.classes = {}
        self.functions = {}
    
    def analyze_codebase(self, project_path: str, analysis: Dict) -> Dict:
        """Perform deep analysis of codebase structure and relationships."""
        project_path_obj = Path(project_path)
        
        result = {
            'modules': {},
            'classes': {},
            'functions': {},
            'relationships': {},
            'dependency_graph': None
        }
        
        # Focus on code files
        code_files = [f for f in analysis.get('files', []) if f.get('is_code', False)]
        
        # Analyze Python files for detailed structure
        python_files = [f for f in code_files if f.get('extension') == '.py']
        if python_files:
            result.update(self._analyze_python_files(project_path_obj, python_files))
        
        # Analyze JavaScript/TypeScript files
        js_files = [f for f in code_files if f.get('extension') in ['.js', '.ts', '.jsx', '.tsx']]
        if js_files:
            js_analysis = self._analyze_js_files(project_path_obj, js_files)
            result['modules'].update(js_analysis.get('modules', {}))
        
        # Generate dependency graph text representation
        result['dependency_graph'] = self._generate_dependency_graph(result)
        
        return result
    
    def _analyze_python_files(self, project_path: Path, python_files: List[Dict]) -> Dict:
        """Analyze Python files for classes, functions, and imports."""
        modules = {}
        classes = {}
        functions = {}
        relationships = defaultdict(lambda: {'imports': set(), 'imported_by': set()})
        
        for file_info in python_files[:50]:  # Limit to 50 files for performance
            file_path = project_path / file_info['path']
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                # Parse AST
                try:
                    tree = ast.parse(code, filename=str(file_path))
                except SyntaxError as e:
                    logger.debug(f"Syntax error in {file_path}: {e}")
                    continue
                
                module_name = file_info['path'].replace('/', '.').replace('.py', '')
                
                module_info = {
                    'path': file_info['path'],
                    'classes': [],
                    'functions': [],
                    'imports': []
                }
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_info['imports'].append(alias.name)
                            relationships[module_name]['imports'].add(alias.name)
                            relationships[alias.name]['imported_by'].add(module_name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_info['imports'].append(node.module)
                            relationships[module_name]['imports'].add(node.module)
                            relationships[node.module]['imported_by'].add(module_name)
                
                # Extract classes and methods
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            'name': node.name,
                            'module': module_name,
                            'methods': [],
                            'bases': [self._get_name(base) for base in node.bases],
                            'docstring': ast.get_docstring(node)
                        }
                        
                        # Extract methods
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_info['methods'].append(item.name)
                        
                        class_key = f"{module_name}.{node.name}"
                        classes[class_key] = class_info
                        module_info['classes'].append(node.name)
                
                # Extract top-level functions
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        func_info = {
                            'name': node.name,
                            'module': module_name,
                            'args': [arg.arg for arg in node.args.args],
                            'docstring': ast.get_docstring(node)
                        }
                        func_key = f"{module_name}.{node.name}"
                        functions[func_key] = func_info
                        module_info['functions'].append(node.name)
                
                modules[module_name] = module_info
                
            except Exception as e:
                logger.debug(f"Error analyzing {file_path}: {e}")
                continue
        
        # Convert sets to lists for JSON serialization
        relationships_dict = {}
        for key, value in relationships.items():
            relationships_dict[key] = {
                'imports': list(value['imports']),
                'imported_by': list(value['imported_by'])
            }
        
        return {
            'modules': modules,
            'classes': classes,
            'functions': functions,
            'relationships': relationships_dict
        }
    
    def _analyze_js_files(self, project_path: Path, js_files: List[Dict]) -> Dict:
        """Analyze JavaScript/TypeScript files for exports and imports."""
        modules = {}
        
        for file_info in js_files[:30]:  # Limit for performance
            file_path = project_path / file_info['path']
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                module_name = file_info['path']
                
                module_info = {
                    'path': file_info['path'],
                    'imports': [],
                    'exports': []
                }
                
                # Simple regex-based parsing for imports
                import_pattern = r'import\s+.*?from\s+[\'"](.+?)[\'"]'
                imports = re.findall(import_pattern, code)
                module_info['imports'] = imports
                
                # Find exports
                export_pattern = r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)'
                exports = re.findall(export_pattern, code)
                module_info['exports'] = exports
                
                modules[module_name] = module_info
                
            except Exception as e:
                logger.debug(f"Error analyzing {file_path}: {e}")
                continue
        
        return {'modules': modules}
    
    def _get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(node)
    
    def _generate_dependency_graph(self, analysis: Dict) -> str:
        """Generate a text-based dependency graph."""
        lines = []
        lines.append("### Module Dependency Graph\n")
        
        relationships = analysis.get('relationships', {})
        
        if not relationships:
            return "No dependency relationships detected.\n"
        
        # Sort modules by number of dependencies
        sorted_modules = sorted(
            relationships.items(),
            key=lambda x: len(x[1].get('imports', [])),
            reverse=True
        )[:15]  # Top 15 modules
        
        lines.append("```")
        lines.append("Module Dependency Hierarchy:")
        lines.append("=" * 50)
        
        for module, deps in sorted_modules:
            imports = deps.get('imports', [])
            imported_by = deps.get('imported_by', [])
            
            if imports or imported_by:
                lines.append(f"\n{module}")
                
                if imports:
                    lines.append(f"  ├─ Imports: {', '.join(list(imports)[:5])}")
                    if len(imports) > 5:
                        lines.append(f"  │  (and {len(imports) - 5} more)")
                
                if imported_by:
                    lines.append(f"  └─ Imported by: {', '.join(list(imported_by)[:3])}")
                    if len(imported_by) > 3:
                        lines.append(f"     (and {len(imported_by) - 3} more)")
        
        lines.append("```\n")
        
        # Add Mermaid diagram
        lines.append("#### Mermaid Diagram\n")
        lines.append("```mermaid")
        lines.append("graph TD")
        
        # Generate simplified graph (top 10 modules)
        for i, (module, deps) in enumerate(sorted_modules[:10]):
            module_id = f"M{i}"
            safe_name = module.split('.')[-1][:20]  # Use last part of module name
            lines.append(f"    {module_id}[{safe_name}]")
            
            for j, imp in enumerate(list(deps.get('imports', []))[:3]):
                # Find if imported module is in our list
                imp_id = None
                for k, (other_mod, _) in enumerate(sorted_modules[:10]):
                    if imp in other_mod or other_mod.endswith(imp):
                        imp_id = f"M{k}"
                        break
                
                if imp_id and imp_id != module_id:
                    lines.append(f"    {module_id} --> {imp_id}")
        
        lines.append("```\n")
        
        return '\n'.join(lines)
    
    def generate_cross_references(self, analysis: Dict) -> Dict[str, List[str]]:
        """Generate cross-references between components."""
        cross_refs = defaultdict(list)
        
        classes = analysis.get('classes', {})
        functions = analysis.get('functions', {})
        
        # Generate "See also" references based on similar names or modules
        for class_name, class_info in classes.items():
            module = class_info.get('module', '')
            
            # Find related classes in same module
            for other_class, other_info in classes.items():
                if other_class != class_name and other_info.get('module') == module:
                    cross_refs[class_name].append(f"[{other_class}](#{other_class.lower().replace('.', '-')})")
            
            # Find related functions
            for func_name, func_info in functions.items():
                if func_info.get('module') == module:
                    cross_refs[class_name].append(f"[{func_name}](#{func_name.lower().replace('.', '-')})")
        
        return dict(cross_refs)
    
    def format_for_documentation(self, code_analysis: Dict) -> str:
        """Format code analysis for documentation."""
        sections = []
        
        sections.append("## Code Structure & Architecture\n")
        
        # Module overview
        modules = code_analysis.get('modules', {})
        if modules:
            sections.append(f"### Modules ({len(modules)} analyzed)\n")
            sections.append("<details>\n<summary>View module structure</summary>\n")
            
            for module_name, module_info in list(modules.items())[:15]:
                sections.append(f"\n**`{module_name}`**")
                if module_info.get('classes'):
                    sections.append(f"- Classes: {', '.join(module_info['classes'])}")
                if module_info.get('functions'):
                    sections.append(f"- Functions: {', '.join(module_info['functions'])}")
                if module_info.get('exports'):
                    sections.append(f"- Exports: {', '.join(module_info['exports'])}")
            
            sections.append("\n</details>\n")
        
        # Classes overview
        classes = code_analysis.get('classes', {})
        if classes:
            sections.append(f"### Classes ({len(classes)} detected)\n")
            sections.append("<details>\n<summary>View class details</summary>\n")
            
            for class_name, class_info in list(classes.items())[:20]:
                sections.append(f"\n**`{class_name}`**")
                if class_info.get('docstring'):
                    sections.append(f"> {class_info['docstring'][:100]}")
                if class_info.get('methods'):
                    sections.append(f"- Methods: `{', '.join(class_info['methods'][:10])}`")
                if class_info.get('bases'):
                    sections.append(f"- Inherits: `{', '.join(class_info['bases'])}`")
            
            sections.append("\n</details>\n")
        
        # Dependency graph
        if code_analysis.get('dependency_graph'):
            sections.append(code_analysis['dependency_graph'])
        
        return '\n'.join(sections)

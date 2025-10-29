"""Project scanner for detecting files, languages, and structure."""

import os
import mimetypes
from pathlib import Path
from typing import List, Dict, Set, Optional
import logging
from collections import defaultdict
import pathspec

logger = logging.getLogger(__name__)


class ProjectScanner:
    """Scans and analyzes project directory structure."""
    
    LANGUAGE_PATTERNS = {
        'Python': ['.py', '.pyw'],
        'JavaScript': ['.js', '.mjs', '.cjs'],
        'TypeScript': ['.ts', '.tsx'],
        'Java': ['.java'],
        'C++': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
        'C': ['.c', '.h'],
        'C#': ['.cs'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'Ruby': ['.rb'],
        'PHP': ['.php'],
        'Swift': ['.swift'],
        'Kotlin': ['.kt', '.kts'],
        'Scala': ['.scala'],
        'Shell': ['.sh', '.bash', '.zsh'],
        'SQL': ['.sql'],
        'HTML': ['.html', '.htm'],
        'CSS': ['.css', '.scss', '.sass', '.less'],
        'YAML': ['.yaml', '.yml'],
        'JSON': ['.json'],
        'Markdown': ['.md', '.markdown'],
        'XML': ['.xml'],
    }
    
    FRAMEWORK_INDICATORS = {
        'Django': ['manage.py', 'settings.py'],
        'Flask': ['app.py', 'wsgi.py'],
        'FastAPI': ['main.py'],
        'React': ['package.json', 'src/App.jsx', 'src/App.tsx'],
        'Vue': ['vue.config.js', 'nuxt.config.js'],
        'Angular': ['angular.json'],
        'Next.js': ['next.config.js'],
        'Express': ['package.json', 'server.js'],
        'Spring': ['pom.xml', 'build.gradle'],
        'Rails': ['Gemfile', 'config/application.rb'],
    }
    
    def __init__(self, config):
        """Initialize the project scanner."""
        self.config = config
        self.ignore_spec = None
        
    def scan_project(self, project_path: str) -> Dict:
        """Scan a project directory and return analysis."""
        project_path_obj = Path(project_path).resolve()
        
        if not project_path_obj.exists():
            raise ValueError(f"Project path does not exist: {project_path_obj}")
        
        if not project_path_obj.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path_obj}")
        
        logger.info(f"Scanning project at: {project_path_obj}")
        
        self._load_gitignore(project_path_obj)
        
        analysis = {
            'path': str(project_path_obj),
            'name': project_path_obj.name,
            'files': [],
            'languages': defaultdict(int),
            'frameworks': [],
            'total_files': 0,
            'total_lines': 0,
            'directory_structure': {},
        }
        
        self._scan_directory(project_path_obj, project_path_obj, analysis)
        
        analysis['languages'] = dict(sorted(
            analysis['languages'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        analysis['frameworks'] = self._detect_frameworks(project_path_obj)
        
        logger.info(f"Scan complete. Found {analysis['total_files']} files in {len(analysis['languages'])} languages")
        
        return analysis
    
    def _load_gitignore(self, project_path: Path):
        """Load .gitignore patterns."""
        gitignore_path = project_path / '.gitignore'
        patterns = self.config.get('scanning', 'ignore_patterns', default=[])
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    gitignore_patterns = f.read().splitlines()
                    patterns.extend(gitignore_patterns)
            except Exception as e:
                logger.warning(f"Failed to read .gitignore: {e}")
        
        if patterns:
            self.ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def _should_ignore(self, path: Path, root: Path) -> bool:
        """Check if a path should be ignored."""
        try:
            rel_path = path.relative_to(root)
            
            if self.ignore_spec and self.ignore_spec.match_file(str(rel_path)):
                return True
            
            if path.is_file():
                max_size = self.config.get('scanning', 'max_file_size_mb', default=5)
                if path.stat().st_size > max_size * 1024 * 1024:
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking ignore for {path}: {e}")
            return True
    
    def _scan_directory(self, current_path: Path, root_path: Path, analysis: Dict, depth: int = 0):
        """Recursively scan directory."""
        max_depth = self.config.get('scanning', 'max_depth', default=10)
        
        if depth > max_depth:
            return
        
        try:
            for item in current_path.iterdir():
                if self._should_ignore(item, root_path):
                    continue
                
                if item.is_file():
                    self._analyze_file(item, root_path, analysis)
                elif item.is_dir():
                    self._scan_directory(item, root_path, analysis, depth + 1)
                    
        except PermissionError:
            logger.warning(f"Permission denied: {current_path}")
        except Exception as e:
            logger.error(f"Error scanning {current_path}: {e}")
    
    def _analyze_file(self, file_path: Path, root_path: Path, analysis: Dict):
        """Analyze a single file."""
        try:
            rel_path = file_path.relative_to(root_path)
            extension = file_path.suffix.lower()
            
            code_extensions = self.config.get('scanning', 'code_extensions', default=[])
            
            file_info = {
                'path': str(rel_path),
                'name': file_path.name,
                'extension': extension,
                'size': file_path.stat().st_size,
                'is_code': extension in code_extensions,
            }
            
            if file_info['is_code']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        file_info['lines'] = len(lines)
                        analysis['total_lines'] += len(lines)
                except Exception as e:
                    logger.debug(f"Could not count lines in {file_path}: {e}")
                    file_info['lines'] = 0
                
                language = self._detect_language(extension)
                if language:
                    analysis['languages'][language] += 1
            
            analysis['files'].append(file_info)
            analysis['total_files'] += 1
            
        except Exception as e:
            logger.debug(f"Error analyzing {file_path}: {e}")
    
    def _detect_language(self, extension: str) -> Optional[str]:
        """Detect programming language from file extension."""
        for language, extensions in self.LANGUAGE_PATTERNS.items():
            if extension in extensions:
                return language
        return None
    
    def _detect_frameworks(self, project_path: Path) -> List[str]:
        """Detect frameworks used in the project."""
        frameworks = []
        
        for framework, indicators in self.FRAMEWORK_INDICATORS.items():
            for indicator in indicators:
                if (project_path / indicator).exists():
                    frameworks.append(framework)
                    break
        
        return frameworks
    
    def get_code_files(self, analysis: Dict) -> List[Dict]:
        """Get only code files from analysis."""
        return [f for f in analysis['files'] if f.get('is_code', False)]

"""SEO optimization utilities for documentation."""

import re
import logging
from typing import List, Dict, Set, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class SEOOptimizer:
    """Optimize documentation for search engines and discoverability."""
    
    def __init__(self, config):
        """Initialize the SEO optimizer."""
        self.config = config
    
    def optimize_markdown(self, content: str, analysis: Dict, doc_type: str = 'readme') -> str:
        """Add SEO optimizations to Markdown content."""
        # Extract metadata
        metadata = self._generate_metadata(content, analysis, doc_type)
        
        # Add front matter if not present
        if not content.startswith('---'):
            content = self._add_front_matter(metadata, content)
        
        # Optimize headings
        content = self._optimize_headings(content, metadata)
        
        return content
    
    def _generate_metadata(self, content: str, analysis: Dict, doc_type: str) -> Dict:
        """Generate metadata for the document."""
        # Extract keywords from content and analysis
        keywords = self._extract_keywords(content, analysis)
        
        # Generate description
        description = self._generate_description(content, analysis)
        
        # Get languages and frameworks
        languages = list(analysis.get('languages', {}).keys())[:5]
        frameworks = analysis.get('frameworks', [])[:5]
        
        # Project name
        project_name = analysis.get('name', 'Project')
        
        metadata = {
            'title': self._generate_title(project_name, doc_type),
            'description': description,
            'keywords': keywords,
            'languages': languages,
            'frameworks': frameworks,
            'tags': self._generate_tags(languages, frameworks, keywords)
        }
        
        return metadata
    
    def _extract_keywords(self, content: str, analysis: Dict) -> List[str]:
        """Extract relevant keywords from content and analysis."""
        keywords = set()
        
        # Add languages
        keywords.update(analysis.get('languages', {}).keys())
        
        # Add frameworks
        keywords.update(analysis.get('frameworks', []))
        
        # Extract technical terms from content
        content_lower = content.lower()
        
        # Common technical keywords to look for
        tech_terms = [
            'api', 'rest', 'graphql', 'database', 'authentication', 'authorization',
            'microservices', 'docker', 'kubernetes', 'ci/cd', 'testing', 'deployment',
            'frontend', 'backend', 'fullstack', 'web', 'mobile', 'cloud',
            'machine learning', 'ai', 'data', 'analytics', 'security',
            'open source', 'library', 'framework', 'cli', 'sdk', 'tool'
        ]
        
        for term in tech_terms:
            if term in content_lower:
                keywords.add(term)
        
        # Extract common capitalized words (likely to be technologies)
        cap_words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', content)
        counter = Counter(cap_words)
        for word, count in counter.most_common(10):
            if count > 2 and len(word) > 3:
                keywords.add(word.lower())
        
        return sorted(list(keywords))[:20]  # Limit to 20 keywords
    
    def _generate_description(self, content: str, analysis: Dict) -> str:
        """Generate a compelling description for SEO."""
        # Try to extract first paragraph after title
        lines = content.split('\n')
        description_lines = []
        
        found_title = False
        for line in lines:
            if line.startswith('# '):
                found_title = True
                continue
            
            if found_title and line.strip() and not line.startswith('#'):
                # Skip badges and images
                if not line.startswith('[!') and not line.startswith('!['):
                    description_lines.append(line.strip())
                    if len(' '.join(description_lines)) > 150:
                        break
        
        description = ' '.join(description_lines)
        
        # Limit to 160 characters for SEO
        if len(description) > 160:
            description = description[:157] + '...'
        
        # Fallback if no description found
        if not description:
            languages = ', '.join(list(analysis.get('languages', {}).keys())[:3])
            description = f"A {languages} project with {analysis.get('total_files', 0)} files and {analysis.get('total_lines', 0)} lines of code."
        
        return description
    
    def _generate_title(self, project_name: str, doc_type: str) -> str:
        """Generate an SEO-friendly title."""
        if doc_type == 'readme':
            return f"{project_name} - Documentation"
        elif doc_type == 'api':
            return f"{project_name} API Reference"
        elif doc_type == 'architecture':
            return f"{project_name} Architecture Guide"
        else:
            return project_name
    
    def _generate_tags(self, languages: List[str], frameworks: List[str], keywords: List[str]) -> List[str]:
        """Generate tags for the document."""
        tags = set()
        
        # Add languages
        tags.update([lang.lower() for lang in languages])
        
        # Add frameworks
        tags.update([fw.lower() for fw in frameworks])
        
        # Add select keywords
        priority_keywords = ['documentation', 'open-source', 'library', 'framework', 'cli', 'api']
        for kw in priority_keywords:
            if kw in keywords:
                tags.add(kw)
        
        return sorted(list(tags))[:15]
    
    def _add_front_matter(self, metadata: Dict, content: str) -> str:
        """Add YAML front matter to Markdown."""
        front_matter = ["---"]
        front_matter.append(f"title: \"{metadata['title']}\"")
        front_matter.append(f"description: \"{metadata['description']}\"")
        
        if metadata['keywords']:
            keywords_str = ', '.join(metadata['keywords'][:10])
            front_matter.append(f"keywords: \"{keywords_str}\"")
        
        if metadata['tags']:
            tags_str = ', '.join(metadata['tags'])
            front_matter.append(f"tags: [{tags_str}]")
        
        if metadata['languages']:
            langs_str = ', '.join(metadata['languages'])
            front_matter.append(f"languages: [{langs_str}]")
        
        front_matter.append("---\n")
        
        return '\n'.join(front_matter) + '\n' + content
    
    def _optimize_headings(self, content: str, metadata: Dict) -> str:
        """Optimize headings for search visibility."""
        lines = content.split('\n')
        result_lines = []
        
        for line in lines:
            # Ensure main heading (H1) includes key information
            if line.startswith('# ') and not line.startswith('##'):
                title = line[2:].strip()
                # Check if it includes important keywords
                has_keyword = any(kw in title.lower() for kw in metadata['keywords'][:5])
                
                # If title is too generic, enhance it
                if not has_keyword and metadata['languages']:
                    # Add language context
                    lang = metadata['languages'][0]
                    if lang.lower() not in title.lower():
                        result_lines.append(line)
                    else:
                        result_lines.append(line)
                else:
                    result_lines.append(line)
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)

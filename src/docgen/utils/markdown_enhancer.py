"""Markdown enhancement utilities for interactive documentation."""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class MarkdownEnhancer:
    """Enhance Markdown files with interactive elements and better formatting."""
    
    def __init__(self, config):
        """Initialize the Markdown enhancer."""
        self.config = config
    
    def enhance_markdown(self, content: str, doc_type: str = 'general') -> str:
        """Apply all enhancements to Markdown content."""
        enhanced = content
        
        # Add table of contents if enabled
        if self.config.get('documentation', 'include_table_of_contents', default=True):
            enhanced = self._add_table_of_contents(enhanced)
        
        # Make code blocks executable/runnable where appropriate
        enhanced = self._enhance_code_blocks(enhanced)
        
        # Add collapsible sections for long content
        enhanced = self._add_collapsible_sections(enhanced)
        
        # Enhance lists and formatting
        enhanced = self._enhance_formatting(enhanced)
        
        return enhanced
    
    def _add_table_of_contents(self, content: str) -> str:
        """Add a table of contents based on headers."""
        lines = content.split('\n')
        headers = []
        toc_lines = []
        
        # Extract headers (H2 and H3 only)
        for line in lines:
            if line.startswith('## ') and not line.startswith('###'):
                title = line[3:].strip()
                anchor = title.lower().replace(' ', '-').replace('&', '').replace(',', '')
                anchor = re.sub(r'[^\w\-]', '', anchor)
                headers.append(('h2', title, anchor))
            elif line.startswith('### '):
                title = line[4:].strip()
                anchor = title.lower().replace(' ', '-').replace('&', '').replace(',', '')
                anchor = re.sub(r'[^\w\-]', '', anchor)
                headers.append(('h3', title, anchor))
        
        if len(headers) < 3:
            return content  # Don't add TOC for short documents
        
        # Build TOC
        toc_lines.append("## Table of Contents\n")
        for level, title, anchor in headers[:20]:  # Limit to 20 entries
            if level == 'h2':
                toc_lines.append(f"- [{title}](#{anchor})")
            else:
                toc_lines.append(f"  - [{title}](#{anchor})")
        toc_lines.append("\n")
        
        # Insert TOC after title (first H1)
        result_lines = []
        inserted = False
        for i, line in enumerate(lines):
            result_lines.append(line)
            if not inserted and line.startswith('# ') and not line.startswith('##'):
                # Insert after title and any badges/description
                # Look ahead for blank line
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].startswith('[')):
                    result_lines.append(lines[j])
                    j += 1
                result_lines.extend(toc_lines)
                inserted = True
                # Skip the lines we already added
                for k in range(i + 1, j):
                    if k < len(lines):
                        lines[k] = None
        
        # Filter out None values
        result_lines = [l for l in result_lines if l is not None]
        
        return '\n'.join(result_lines) if inserted else content
    
    def _enhance_code_blocks(self, content: str) -> str:
        """Enhance code blocks with language tags and execution hints."""
        lines = content.split('\n')
        result_lines = []
        in_code_block = False
        code_lang = None
        
        for line in lines:
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    lang_match = re.match(r'```(\w+)', line.strip())
                    code_lang = lang_match.group(1) if lang_match else None
                    
                    # Add language if missing
                    if line.strip() == '```' and result_lines:
                        # Try to infer language from context
                        prev_context = ' '.join(result_lines[-3:]).lower()
                        if 'python' in prev_context or 'pip install' in prev_context:
                            line = '```python'
                        elif 'javascript' in prev_context or 'npm' in prev_context:
                            line = '```javascript'
                        elif 'bash' in prev_context or 'shell' in prev_context or '$' in prev_context:
                            line = '```bash'
                else:
                    # Ending code block
                    in_code_block = False
                    code_lang = None
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _add_collapsible_sections(self, content: str) -> str:
        """Add collapsible sections for long lists or detailed content."""
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Detect long lists that could be collapsible
            if line.startswith('###') and 'Dependencies' in line or 'Requirements' in line or 'Configuration' in line:
                result_lines.append(line)
                i += 1
                
                # Collect the content after this header
                section_start = i
                section_lines = []
                while i < len(lines) and not lines[i].startswith('##'):
                    section_lines.append(lines[i])
                    i += 1
                
                # If section is long, make it collapsible
                if len(section_lines) > 15:
                    result_lines.append("<details>")
                    result_lines.append("<summary>Click to expand</summary>\n")
                    result_lines.extend(section_lines)
                    result_lines.append("\n</details>\n")
                else:
                    result_lines.extend(section_lines)
            else:
                result_lines.append(line)
                i += 1
        
        return '\n'.join(result_lines)
    
    def _enhance_formatting(self, content: str) -> str:
        """Enhance general formatting and readability."""
        # Add proper spacing around headers
        lines = content.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            # Ensure blank line before headers (except at start)
            if line.startswith('#') and i > 0 and result_lines and result_lines[-1].strip() != '':
                result_lines.append('')
            
            result_lines.append(line)
            
            # Ensure blank line after headers
            if line.startswith('#') and i < len(lines) - 1 and lines[i + 1].strip() != '':
                if not lines[i + 1].startswith('#'):
                    # Don't add if next line is also a header
                    pass
        
        return '\n'.join(result_lines)
    
    def create_collapsible_section(self, title: str, content: str) -> str:
        """Create a collapsible Markdown section."""
        return f"""<details>
<summary>{title}</summary>

{content}

</details>
"""
    
    def create_code_snippet(self, code: str, language: str = 'bash', title: Optional[str] = None) -> str:
        """Create a well-formatted code snippet."""
        snippet = []
        if title:
            snippet.append(f"**{title}**\n")
        snippet.append(f"```{language}")
        snippet.append(code)
        snippet.append("```")
        return '\n'.join(snippet)

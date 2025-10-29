"""LangChain integration for Ollama LLM."""

import logging
from typing import Optional, List, Dict
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with Ollama through LangChain."""
    
    def __init__(self, config):
        """Initialize the LLM client."""
        self.config = config
        
        base_url = config.get('ollama', 'base_url', default='http://localhost:11434')
        model = config.get('ollama', 'model', default='llama3.2')
        temperature = config.get('ollama', 'temperature', default=0.3)
        
        try:
            self.llm = ChatOllama(
                base_url=base_url,
                model=model,
                temperature=temperature,
            )
            logger.info(f"Initialized Ollama client with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise
    
    def generate_project_overview(self, analysis: Dict) -> str:
        """Generate a project overview from analysis."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical writer creating project documentation.
Based on the project analysis provided, write a clear and comprehensive project overview.
Include:
- Project purpose and main functionality
- Key technologies and languages used
- Project structure and organization
- Notable features and capabilities

Be concise but informative. Use professional technical writing style."""),
            ("user", """Project Name: {name}
Total Files: {total_files}
Languages: {languages}
Frameworks: {frameworks}
Total Lines of Code: {total_lines}

Generate a comprehensive project overview.""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "name": analysis.get('name', 'Unknown'),
                "total_files": analysis.get('total_files', 0),
                "languages": ', '.join(analysis.get('languages', {}).keys()),
                "frameworks": ', '.join(analysis.get('frameworks', [])) or 'None detected',
                "total_lines": analysis.get('total_lines', 0)
            })
            return result
        except Exception as e:
            logger.error(f"Error generating project overview: {e}")
            return "Failed to generate project overview."
    
    def analyze_code_file(self, file_path: str, code: str, language: str) -> str:
        """Analyze a single code file and generate documentation."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert code documentation generator.
Analyze the provided code and create clear, comprehensive documentation including:
- Brief description of the file's purpose
- Main classes, functions, or components
- Key functionality and logic
- Important dependencies or imports
- Notable patterns or algorithms used

Write in a clear, professional style suitable for technical documentation."""),
            ("user", """File: {file_path}
Language: {language}

Code:
```{language}
{code}
```

Generate documentation for this code file.""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "file_path": file_path,
                "language": language,
                "code": code[:8000]
            })
            return result
        except Exception as e:
            logger.error(f"Error analyzing code file {file_path}: {e}")
            return f"Failed to analyze {file_path}."
    
    def generate_readme_content(self, analysis: Dict, overview: str, style_config: Dict) -> str:
        """Generate README.md content."""
        include_emojis = style_config.get('include_emojis', True)
        include_badges = style_config.get('include_badges', True)
        verbosity = style_config.get('verbosity', 'detailed')
        
        emoji_instruction = "Use relevant emojis to make sections visually appealing." if include_emojis else "Do not use emojis."
        badge_instruction = "Include relevant badges (build, version, license, etc.)." if include_badges else "Do not include badges."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert at creating professional, compelling README.md files.
Create a comprehensive README with the following sections:
- Title and brief tagline
- Badges (if applicable)
- Overview/Description
- Features (bullet points of key capabilities)
- Installation instructions
- Usage examples
- Project structure
- Technologies used
- Contributing guidelines (brief)
- License information

Style: {verbosity}
{emoji_instruction}
{badge_instruction}

Use proper Markdown formatting with headers, code blocks, lists, and tables where appropriate.
Make it visually appealing and easy to navigate."""),
            ("user", """Project Name: {name}
Languages: {languages}
Frameworks: {frameworks}
Total Files: {total_files}

Project Overview:
{overview}

Generate a professional README.md file.""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "name": analysis.get('name', 'Project'),
                "languages": ', '.join(list(analysis.get('languages', {}).keys())[:5]),
                "frameworks": ', '.join(analysis.get('frameworks', [])) or 'Various',
                "total_files": analysis.get('total_files', 0),
                "overview": overview
            })
            return result
        except Exception as e:
            logger.error(f"Error generating README: {e}")
            return "# Project\n\nFailed to generate README content."
    
    def generate_architecture_doc(self, analysis: Dict) -> str:
        """Generate architecture documentation."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a software architect creating technical architecture documentation.
Based on the project analysis, create a comprehensive architecture document including:
- High-level system architecture overview
- Key components and their responsibilities
- Technology stack and rationale
- Directory structure and organization
- Data flow and interactions
- Design patterns used
- Scalability and performance considerations

Use Markdown formatting with diagrams described in text (users can convert to Mermaid later)."""),
            ("user", """Project: {name}
Languages: {languages}
Frameworks: {frameworks}
Total Files: {total_files}
Main Directories: {directories}

Generate architecture documentation.""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            directories = set()
            for file_info in analysis.get('files', [])[:20]:
                path_parts = file_info['path'].split('/')
                if len(path_parts) > 1:
                    directories.add(path_parts[0])
            
            result = chain.invoke({
                "name": analysis.get('name', 'Project'),
                "languages": ', '.join(analysis.get('languages', {}).keys()),
                "frameworks": ', '.join(analysis.get('frameworks', [])) or 'None detected',
                "total_files": analysis.get('total_files', 0),
                "directories": ', '.join(sorted(directories)[:10])
            })
            return result
        except Exception as e:
            logger.error(f"Error generating architecture doc: {e}")
            return "# Architecture\n\nFailed to generate architecture documentation."
    
    def generate_api_documentation(self, code_files: List[Dict], project_name: str) -> str:
        """Generate API documentation from code files."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are creating API documentation for a software project.
Based on the provided code file information, create comprehensive API documentation including:
- Available endpoints/functions/classes
- Parameters and return types
- Usage examples
- Error handling

Use clear Markdown formatting with code examples."""),
            ("user", """Project: {project_name}
Number of Code Files: {num_files}
Main Languages: {languages}

Generate API documentation structure and overview.""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            languages = set()
            for file in code_files[:10]:
                if 'extension' in file:
                    languages.add(file['extension'])
            
            result = chain.invoke({
                "project_name": project_name,
                "num_files": len(code_files),
                "languages": ', '.join(languages)
            })
            return result
        except Exception as e:
            logger.error(f"Error generating API docs: {e}")
            return "# API Documentation\n\nFailed to generate API documentation."
    
    def generate_project_summary(self, analysis: Dict, overview: str) -> str:
        """Generate a concise 1-2 paragraph summary of the entire project."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical writer creating concise project summaries.
Generate a natural-language summary of the project in 1-2 paragraphs (150-200 words).
The summary should:
- Be engaging and informative
- Highlight the main purpose and value proposition
- Mention key technologies used
- Be suitable for README.md and SUMMARY.md files

Write in clear, accessible language that both technical and non-technical readers can understand."""),
            ("user", """Project Name: {name}
Total Files: {total_files}
Languages: {languages}
Frameworks: {frameworks}
Total Lines of Code: {total_lines}

Project Overview:
{overview}

Generate a concise, compelling 1-2 paragraph summary.""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "name": analysis.get('name', 'Project'),
                "total_files": analysis.get('total_files', 0),
                "languages": ', '.join(list(analysis.get('languages', {}).keys())[:5]),
                "frameworks": ', '.join(analysis.get('frameworks', [])) or 'Various',
                "total_lines": analysis.get('total_lines', 0),
                "overview": overview[:500]
            })
            return result
        except Exception as e:
            logger.error(f"Error generating project summary: {e}")
            return f"A {', '.join(list(analysis.get('languages', {}).keys())[:2])} project with {analysis.get('total_files', 0)} files."

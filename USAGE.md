# Detailed Usage Guide

## Installation Options

### Option 1: Install as Package (Recommended)

```bash
cd ai-doc-generator
pip install -e .
```

This makes the `docgen` command available globally:

```bash
docgen generate /path/to/project
```

### Option 2: Run Directly with Python

```bash
python main.py generate /path/to/project
```

### Option 3: Use as Module

```python
from src.docgen.core.config import Config
from src.docgen.core.scanner import ProjectScanner
from src.docgen.core.llm_client import LLMClient
from src.docgen.core.workflow import DocumentationWorkflow
from src.docgen.generators.doc_writer import DocumentationWriter

config = Config()
scanner = ProjectScanner(config)
llm_client = LLMClient(config)
workflow = DocumentationWorkflow(scanner, llm_client, config)
writer = DocumentationWriter(config)

state = workflow.run("/path/to/project")
files = writer.write_documentation("/path/to/project", state)
```

## Command Reference

### Initialize Configuration

```bash
python main.py init
```

Creates a `config.yaml` file in the current directory with all default settings.

### Generate Documentation

#### Basic Usage

```bash
# Current directory
python main.py generate

# Specific directory
python main.py generate /path/to/project
```

#### Advanced Options

```bash
# Use custom config file
python main.py generate -c /path/to/config.yaml

# Custom output directory
python main.py generate -o custom-docs

# Use specific Ollama model
python main.py generate -m codellama

# Overwrite existing documentation
python main.py generate --overwrite

# Enable verbose logging
python main.py generate -v
```

#### Combined Options

```bash
python main.py generate /home/user/myproject \
    -c custom-config.yaml \
    -o documentation \
    -m llama3.2 \
    --overwrite \
    -v
```

## Configuration Guide

### Ollama Settings

```yaml
ollama:
  base_url: "http://localhost:11434"  # Ollama server URL
  model: "llama3.2"                   # Model to use
  temperature: 0.3                    # 0.0-1.0, lower = more focused
  timeout: 120                        # Request timeout in seconds
```

**Available Models:**
- `llama3.2` - Fast, general purpose (recommended)
- `codellama` - Optimized for code understanding
- `mistral` - Good balance of speed and quality
- `mixtral` - Higher quality, slower
- Custom models you've pulled with Ollama

### Documentation Style

```yaml
documentation:
  style: "professional"     # professional, casual, technical, minimal
  tone: "clear"            # clear, friendly, formal, concise
  verbosity: "detailed"    # minimal, balanced, detailed, comprehensive
  include_emojis: true     # Add emojis to headers
  include_badges: true     # Add status badges to README
  include_table_of_contents: true
```

### Scanning Configuration

```yaml
scanning:
  max_file_size_mb: 5      # Skip files larger than this
  max_depth: 10            # Maximum directory recursion depth
  follow_symlinks: false   # Whether to follow symbolic links
  
  ignore_patterns:
    - "*.log"
    - "*.tmp"
    - ".git/"
    - "node_modules/"
    - "__pycache__/"
    # Add custom patterns here
  
  code_extensions:
    - ".py"
    - ".js"
    - ".ts"
    # Add more extensions as needed
```

### Output Configuration

```yaml
output:
  docs_directory: "docs"           # Where to write docs
  create_readme: true              # Generate README.md
  create_api_docs: true            # Generate API.md
  create_architecture_docs: true   # Generate ARCHITECTURE.md
  create_contributing: true        # Generate CONTRIBUTING.md
  create_changelog: false          # Generate CHANGELOG.md
  overwrite_existing: false        # Prompt before overwriting
```

### Advanced Options

```yaml
advanced:
  chunk_size: 4000              # Characters per code chunk
  max_concurrent_requests: 3    # Parallel Ollama requests
  retry_attempts: 3             # Retries on failure
  enable_caching: true          # Cache LLM responses
  cache_ttl_hours: 24          # Cache expiration
  log_level: "INFO"            # DEBUG, INFO, WARNING, ERROR
```

## Workflow Details

### Step 1: Project Scanning

The scanner:
1. Reads .gitignore and custom ignore patterns
2. Recursively traverses directories
3. Identifies file types and languages
4. Counts lines of code
5. Detects frameworks and dependencies

### Step 2: Project Overview Generation

Using the scan results, the LLM generates:
- Project purpose and goals
- Technology stack summary
- High-level architecture overview

### Step 3: README Generation

Creates a comprehensive README with:
- Project title and description
- Features list
- Installation instructions
- Usage examples
- Technology stack
- Project structure

### Step 4: Architecture Documentation

Generates:
- System architecture overview
- Component descriptions
- Directory structure explanation
- Design patterns used
- Technology choices and rationale

### Step 5: API Documentation

Produces:
- Endpoint/function listings
- Parameter descriptions
- Return types
- Usage examples

### Step 6: File Writing

Writes all documentation to:
- `README.md` in project root
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/CONTRIBUTING.md`
- `docs/INDEX.md`

## Tips and Best Practices

### For Best Results

1. **Clean your project first**
   - Remove build artifacts
   - Clear temporary files
   - Update .gitignore

2. **Use appropriate models**
   - `codellama` for code-heavy projects
   - `llama3.2` for general documentation
   - Larger models for complex projects

3. **Tune the temperature**
   - Lower (0.1-0.3) for technical docs
   - Higher (0.5-0.7) for creative descriptions

4. **Adjust verbosity**
   - "minimal" for simple projects
   - "detailed" for complex codebases
   - "comprehensive" for thorough documentation

### Performance Optimization

1. **Use caching**
   ```yaml
   advanced:
     enable_caching: true
     cache_ttl_hours: 24
   ```

2. **Limit file size**
   ```yaml
   scanning:
     max_file_size_mb: 3
   ```

3. **Increase concurrent requests**
   ```yaml
   advanced:
     max_concurrent_requests: 5
   ```

### Handling Large Projects

For very large projects (>1000 files):

1. Increase max depth selectively
2. Add specific ignore patterns
3. Focus on core directories
4. Generate docs incrementally

## Troubleshooting

### Common Issues

**Issue: "Ollama connection failed"**

Solution:
```bash
# Start Ollama
ollama serve

# Pull the model
ollama pull llama3.2

# Test connection
curl http://localhost:11434
```

**Issue: "Documentation is generic"**

Solutions:
- Ensure code files are not being ignored
- Check file extension list includes your languages
- Try a code-focused model like `codellama`
- Increase verbosity setting

**Issue: "Process is slow"**

Solutions:
- Use a faster model (llama3.2)
- Reduce chunk_size
- Lower max_concurrent_requests if memory-limited
- Enable caching

**Issue: "Files not being scanned"**

Solutions:
- Check .gitignore patterns
- Review ignore_patterns in config
- Verify code_extensions includes your file types
- Use `--verbose` to see what's being skipped

### Debug Mode

Enable detailed logging:

```bash
python main.py generate -v
```

This shows:
- Files being scanned
- LLM requests and responses
- Errors and warnings
- Timing information

## Examples

### Example 1: Python Project

```bash
python main.py generate ~/projects/my-python-app \
    -m codellama \
    -o docs
```

### Example 2: Full-Stack JavaScript

```yaml
# config.yaml
documentation:
  style: "professional"
  verbosity: "comprehensive"
  
scanning:
  code_extensions:
    - ".js"
    - ".jsx"
    - ".ts"
    - ".tsx"
    - ".vue"
```

```bash
python main.py generate ~/projects/web-app -c config.yaml
```

### Example 3: Multi-Language Project

```yaml
scanning:
  code_extensions:
    - ".py"
    - ".js"
    - ".go"
    - ".rs"
    - ".java"
```

```bash
python main.py generate ~/projects/microservices --overwrite
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Generate Documentation

on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Ollama
        run: |
          curl https://ollama.ai/install.sh | sh
          ollama serve &
          ollama pull llama3.2
      - name: Generate Docs
        run: |
          pip install -e .
          python main.py generate --overwrite
      - name: Commit Documentation
        run: |
          git config user.name "Documentation Bot"
          git add docs/ README.md
          git commit -m "Update documentation"
          git push
```

## Best Practices

1. **Version control your config**
   - Commit `config.yaml` to your repo
   - Team members get consistent docs

2. **Review generated docs**
   - AI-generated docs are a starting point
   - Review and refine for accuracy

3. **Regenerate periodically**
   - After major changes
   - Before releases
   - Monthly for active projects

4. **Customize per project**
   - Create project-specific configs
   - Tune settings for your needs

5. **Combine with manual docs**
   - Use generated docs as foundation
   - Add human expertise and context

# Documentation System

This directory contains comprehensive documentation for the Crypto Capital Gains Tax Calculator project, organized for easy maintenance and automatic updates.

## 📁 Directory Structure

```
docs/
├── README.md                           # This file
├── wiki/                              # Wiki-style documentation
│   ├── Home.md                        # Main project page
│   ├── Task-Progress.md               # Task tracking and progress
│   ├── Installation-Guide.md          # Setup instructions
│   ├── Quick-Start-Tutorial.md        # Getting started guide
│   ├── Architecture-Overview.md       # System architecture
│   ├── API-Documentation.md           # API reference
│   ├── User-Manual.md                 # User guide
│   ├── Troubleshooting.md             # Common issues and solutions
│   ├── FAQ.md                         # Frequently asked questions
│   ├── Contributing.md                # Contribution guidelines
│   ├── Release-Notes.md               # Version history
│   ├── tasks/                         # Individual task documentation
│   │   ├── T001-*.md                  # Task completion docs
│   │   ├── T002-*.md
│   │   └── ...
│   └── templates/                     # Documentation templates
│       ├── task-completion-template.md
│       ├── api-documentation-template.md
│       └── user-guide-template.md
└── api/                               # API documentation
    ├── openapi.yaml                   # OpenAPI specification
    ├── postman/                       # Postman collection
    └── examples/                      # API usage examples
```

## 🔄 Automatic Documentation Updates

The documentation system is designed to automatically update when tasks are completed:

### 1. Task Completion Workflow
- When a GitHub issue is closed, the documentation is automatically updated
- Task progress is tracked in `Task-Progress.md`
- Individual task completion docs are created in `tasks/` directory

### 2. Manual Updates
You can manually update documentation using:

```bash
# Update all documentation
python update_docs.py

# Update documentation for a specific completed task
python update_docs.py 1 "Create project structure" "Set up basic project structure with src/ and tests/ directories"
```

### 3. GitHub Actions
The following workflows automatically update documentation:
- `update-docs.yml`: Updates docs when issues are closed
- `ci.yml`: Runs documentation validation during CI

## 📝 Documentation Standards

### Task Documentation
Each completed task should have:
- Clear description of what was implemented
- Files that were created or modified
- Code snippets showing key changes
- Testing status
- Dependencies resolved
- Next steps enabled

### API Documentation
- OpenAPI 3.0 specification
- Request/response examples
- Error handling documentation
- Authentication requirements

### User Documentation
- Step-by-step instructions
- Screenshots where helpful
- Troubleshooting guides
- FAQ for common questions

## 🚀 Getting Started

### For Developers
1. Read the [Architecture Overview](wiki/Architecture-Overview.md)
2. Follow the [Development Setup](wiki/Development-Setup.md)
3. Check [Task Progress](wiki/Task-Progress.md) for current status
4. Use the [API Documentation](wiki/API-Documentation.md) for integration

### For Users
1. Start with the [Installation Guide](wiki/Installation-Guide.md)
2. Follow the [Quick Start Tutorial](wiki/Quick-Start-Tutorial.md)
3. Refer to the [User Manual](wiki/User-Manual.md) for detailed usage
4. Check [Troubleshooting](wiki/Troubleshooting.md) for common issues

## 🔧 Maintenance

### Updating Documentation
1. **Task Completion**: Run `python update_docs.py` after completing a task
2. **Manual Updates**: Edit the relevant `.md` files in `docs/wiki/`
3. **API Changes**: Update `docs/api/openapi.yaml` and regenerate docs
4. **Version Updates**: Update version numbers in all relevant files

### Documentation Validation
The CI pipeline validates:
- Markdown syntax
- Link integrity
- Code example syntax
- API specification validity

### Publishing to GitHub Wiki
To publish the local documentation to GitHub Wiki:

```bash
# Clone the wiki repository
git clone https://github.com/misterdev32/CapitalGainsTaxCalculator.wiki.git

# Copy local docs to wiki
cp -r docs/wiki/* CapitalGainsTaxCalculator.wiki/

# Commit and push to wiki
cd CapitalGainsTaxCalculator.wiki
git add .
git commit -m "Update wiki documentation"
git push origin main
```

## 📊 Documentation Metrics

Track documentation quality with:
- **Coverage**: Percentage of features documented
- **Freshness**: Last update date for each section
- **Completeness**: Required sections present
- **Accuracy**: Documentation matches implementation

## 🤝 Contributing to Documentation

1. Follow the existing structure and naming conventions
2. Use clear, concise language
3. Include code examples where helpful
4. Update related documentation when making changes
5. Test all links and examples before submitting

## 📞 Support

For documentation issues or questions:
- Create an issue with the `documentation` label
- Check existing [FAQ](wiki/FAQ.md)
- Review [Troubleshooting](wiki/Troubleshooting.md)

---

*This documentation system is designed to grow with the project and provide comprehensive, up-to-date information for all users and contributors.*

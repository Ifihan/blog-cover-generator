# Contributing

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Set up the development environment (see [Setup](README.md#setup) section in the README)

## Development

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Keep functions focused and small

### Project Structure

```bash
├── app.py              # Application entry point
├── config.py           # Configuration management
├── models.py           # Database models
├── routes.py           # API routes
├── admin.py            # Admin functionality
├── utils/              # Utility modules
│   ├── image_generator.py
│   ├── image_processor.py
│   └── storage.py
├── templates/          # Jinja2 templates
└── static/             # CSS, JS, assets
```

### Running Locally

```bash
# Set MOCK_MODE=true to skip API calls during development
MOCK_MODE=true

python app.py
```

## Pull Requests

1. Update your branch with main: `git rebase main`
2. Test your changes locally
3. Write clear commit messages
4. Submit PR with description of changes

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce
- Add relevant error messages or screenshots

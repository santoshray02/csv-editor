# Publishing Guide for CSV Editor

This guide covers publishing your CSV Editor package to PyPI and other repositories for maximum visibility.

## 🎯 Publishing Strategy

### 1. PyPI (Python Package Index) - Primary
- **Main distribution channel** for Python packages
- **Easy installation** via `pip install csv-editor`
- **Automatic dependency management**

### 2. GitHub Packages
- **Backup distribution** and enterprise use
- **Integration** with GitHub ecosystem

### 3. Conda-Forge (Future)
- **Scientific Python community**
- **Conda package manager**

## 🚀 Quick Start Publishing

### Prerequisites
```bash
# Install publishing tools (using uv)
uv add --dev twine

# Create PyPI account at https://pypi.org/account/register/
# Create API token at https://pypi.org/manage/account/token/
```

### Method 1: Automated Publishing (Recommended)

1. **Push to GitHub** and create a release:
```bash
git add .
git commit -m "Prepare v1.0.0 release"
git push origin main
git tag v1.0.0
git push origin v1.0.0
```

2. **Create GitHub Release**:
   - Go to https://github.com/santoshray02/csv-editor/releases
   - Click "Create a new release"
   - Tag: `v1.0.0`
   - Title: `CSV Editor v1.0.0`
   - Description: Copy from CHANGELOG.md
   - Publish release

3. **Automatic publishing** via GitHub Actions will handle the rest!

### Method 2: Manual Publishing

1. **Build and test**:
```bash
uv run python scripts/publish.py
```

2. **Test publish** (optional):
```bash
uv run twine upload --repository testpypi dist/*
```

3. **Publish to PyPI**:
```bash
uv run twine upload dist/*
```

## 📋 Pre-Publishing Checklist

- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG.md updated with new version
- [ ] All tests passing
- [ ] Documentation updated
- [ ] README.md has clear installation instructions
- [ ] License file present
- [ ] GitHub repository is public
- [ ] PyPI account created and API token configured

## 🔧 PyPI Configuration

### 1. Create `.pypirc` file:
```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### 2. Or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
```

## 🌟 Promotion Strategy

### 1. Python Community
- **Reddit**: r/Python, r/MachineLearning, r/datascience
- **Hacker News**: Submit to Show HN
- **Python Weekly**: Submit for newsletter inclusion
- **Real Python**: Consider guest article

### 2. MCP Community
- **Model Context Protocol Discord**
- **Anthropic Community Forums**
- **FastMCP GitHub discussions**

### 3. Data Science Community
- **Kaggle**: Share in datasets/discussions
- **Data Science subreddits**
- **Pandas community**
- **Jupyter community**

### 4. Developer Platforms
- **Product Hunt**: Launch your package
- **Dev.to**: Write tutorial articles
- **Medium**: Technical deep-dive articles
- **YouTube**: Create demo videos

### 5. Social Media
- **Twitter/X**: Use hashtags #Python #DataScience #MCP #OpenSource
- **LinkedIn**: Professional network posts
- **Mastodon**: Python and tech communities

## 📊 Package Analytics

### Track your package performance:
- **PyPI Stats**: https://pypistats.org/packages/csv-editor
- **GitHub Insights**: Repository analytics
- **Download counts**: Monitor adoption

### Key metrics to watch:
- Daily/monthly downloads
- GitHub stars and forks
- Issues and discussions
- Community contributions

## 🔄 Maintenance

### Regular updates:
1. **Security updates**: Keep dependencies current
2. **Bug fixes**: Address user issues promptly
3. **Feature releases**: Based on community feedback
4. **Documentation**: Keep examples and guides updated

### Version management:
- **Patch releases** (1.0.1): Bug fixes
- **Minor releases** (1.1.0): New features
- **Major releases** (2.0.0): Breaking changes

## 📈 Success Metrics

### Short-term goals (1-3 months):
- [ ] 100+ PyPI downloads
- [ ] 50+ GitHub stars
- [ ] 5+ community issues/discussions
- [ ] Featured in at least one newsletter/blog

### Medium-term goals (3-6 months):
- [ ] 1000+ PyPI downloads
- [ ] 100+ GitHub stars
- [ ] 10+ contributors
- [ ] Conda-forge package
- [ ] Documentation website

### Long-term goals (6+ months):
- [ ] 10,000+ PyPI downloads
- [ ] 500+ GitHub stars
- [ ] Active community
- [ ] Integration with major AI platforms
- [ ] Conference talks/presentations

## 🆘 Troubleshooting

### Common issues:
1. **Upload failed**: Check API token and package name availability
2. **Build errors**: Ensure all dependencies in pyproject.toml
3. **Import errors**: Check package structure and __init__.py files
4. **Version conflicts**: Ensure version is higher than existing

### Getting help:
- **PyPI Support**: https://pypi.org/help/
- **GitHub Issues**: Create issues for package-specific problems
- **Python Packaging Guide**: https://packaging.python.org/

## 🎉 Post-Publishing

After successful publishing:

1. **Update README** with installation instructions
2. **Create announcement** on social media
3. **Submit to package directories**:
   - Awesome Python lists
   - Python Package Index alternatives
   - Curated package collections

4. **Engage with community**:
   - Respond to issues promptly
   - Welcome contributions
   - Maintain active development

Good luck with your package launch! 🚀

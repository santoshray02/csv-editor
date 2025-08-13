# Security Policy

## Supported Versions

We actively support the following versions of CSV Editor:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in CSV Editor, please report it responsibly.

### How to Report

1. **Email**: Send details to rayskumar02@gmail.com
2. **Subject**: Include "CSV Editor Security" in the subject line
3. **Details**: Provide a detailed description of the vulnerability

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 24 hours
- **Status Update**: Within 72 hours
- **Fix Timeline**: Depends on severity (1-30 days)

### Security Best Practices

When using CSV Editor:

1. **Input Validation**: Always validate CSV files before processing
2. **File Permissions**: Ensure proper file permissions for CSV files
3. **Network Security**: Use HTTPS when running in HTTP mode
4. **Access Control**: Limit MCP server access to trusted clients
5. **Regular Updates**: Keep CSV Editor updated to the latest version

### Disclosure Policy

- We will acknowledge receipt of your vulnerability report
- We will provide regular updates on our progress
- We will credit you in the security advisory (unless you prefer anonymity)
- We will coordinate disclosure timing with you

### Security Features

CSV Editor includes several security features:

- Input sanitization for CSV data
- File path validation to prevent directory traversal
- Memory usage limits to prevent DoS attacks
- Error handling to prevent information disclosure

Thank you for helping keep CSV Editor secure!

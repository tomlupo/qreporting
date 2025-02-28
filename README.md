# QReporting

A flexible Python package for generating interactive HTML reports from nested data structures.

## Overview

QReporting transforms nested dictionaries into interactive HTML reports, complete with navigation menus, content organization, and a professional interface. It uses Jupyter notebooks for content processing, making it perfect for data science and analytics reporting.

## Features

- **Interactive Reports**: Generate complete HTML dashboards with navigation sidebar.
- **Standalone Reports**: Create individual HTML reports for specific data.
- **Flexible Depth Control**: Customize menu depth globally or per section.
- **Dynamic Navigation**: Interactive menu with expandable sections.
- **Table of Contents**: Automatically generated overview of all reports.
- **Icon Support**: Font Awesome integration for visual navigation cues.
- **Responsive Design**: Mobile-friendly reports with Tailwind CSS.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qreporting.git

# Navigate to the project directory
cd qreporting

# Install the package
pip install -e .
```

## Usage Examples

### Basic Report Generation

```python
from qreporting import generate_report

# Sample data structure
data = {
    "Dashboard": {
        "Overview": {
            "Summary": {"value": 100, "growth": 0.15},
            "Statistics": pd.DataFrame({'metric': ['A', 'B'], 'value': [10, 20]})
        }
    },
    "Reports": {
        "Sales": pd.DataFrame({'month': ['Jan', 'Feb'], 'value': [1000, 1200]}),
        "Inventory": pd.DataFrame({'product': ['X', 'Y'], 'stock': [50, 30]})
    },
    "Settings": {"api_key": "sample", "refresh_rate": 60}
}

# Generate the report
generate_report(
    data_dict=data,
    output_dir="./report_output",
    report_title="Company Analytics Dashboard",
    depth=2  # Process menu items up to 2 levels deep
)
```

### Variable Depth Reports

```python
from qreporting import generate_report

# Configure different depths for different sections
depth_config = {
    "Dashboard": 3,  # Process Dashboard 3 levels deep
    "Reports": 2,    # Process Reports 2 levels deep
    "Settings": 1,   # Process Settings as a simple page
    "default": 2     # Use depth 2 for any other sections
}

# Generate the report with variable depth
generate_report(
    data_dict=data,
    output_dir="./report_output",
    report_title="Multi-Depth Analytics Dashboard",
    depth=depth_config
)
```

### Standalone Single-Page Report

```python
from qreporting import generate_simple_report
import pandas as pd

# Create some sample data
data = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Value': [100, 200, 300]
})

# Generate a standalone report
report_path = generate_simple_report(
    content=data,
    report_name="Sample Metrics",
    output_dir="./individual_reports"
)

print(f"Report generated at: {report_path}")
```

## Package Structure

```
qreporting/
├── __init__.py        # Package exports and API definition
├── core.py            # Core functionality and implementation
├── templates/         # HTML and Jupyter notebook templates
│   ├── report_template.html             # Main HTML template
│   ├── report_template_icons.json       # Icon mapping configuration
│   └── generic_report_template.ipynb    # Notebook for content processing
```

## Code Organization

The codebase is organized into logical sections:

1. **Imports and Constants**: Libraries and configuration values
2. **Helper Functions**: Utility functions for common tasks
3. **Menu Structure Functions**: Functions for processing nested data into menus
4. **Content Processing Functions**: Transforms data into HTML via notebooks
5. **Report Generation Functions**: Creates full and simple reports
6. **HTML Content Generation Functions**: Specialized HTML generation

## Dependencies

- **Jupyter & Papermill**: For executing notebooks programmatically
- **Jinja2**: For HTML templating
- **Pandas**: For data handling
- **Tailwind CSS** (via CDN): For responsive styling
- **Font Awesome** (via CDN): For icons

## Customization

### Customizing Templates

You can modify the HTML and notebook templates in the `templates/` directory:

- `report_template.html`: Modify the overall layout and styling
- `report_template_icons.json`: Change icon mappings
- `generic_report_template.ipynb`: Customize how content is processed and displayed

### Adding Custom Icons

Edit `templates/report_template_icons.json` to add new icon mappings:

```json
{
    "_metadata": {
        "source": "Font Awesome",
        "version": "6.4.0"
    },
    "Dashboard": "home",
    "Reports": "chart-bar",
    "YourSection": "your-icon-name"
}
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
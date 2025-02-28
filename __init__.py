#!/usr/bin/env python
"""
Report Generator Module

This module provides functions for generating HTML reports from nested dictionaries,
using Jupyter notebooks via papermill for content processing.

Main functions:
- generate_report: Create a complete report with navigation and multiple pages
- generate_simple_report: Create a standalone single-page report
"""

from .core import (
    # Main report generation functions
    generate_report,
    generate_simple_report,
    
    # Content processing function
    process_report_content,
    
    # Constants
    DEFAULT_DEPTH,
    REPORT_TEMPLATE_PATH,
    NOTEBOOK_TEMPLATE_PATH,
    ICON_MAPPING_PATH
)

__all__ = [
    'generate_report',
    'generate_simple_report',
    'process_report_content',
    'DEFAULT_DEPTH',
    'REPORT_TEMPLATE_PATH',
    'NOTEBOOK_TEMPLATE_PATH',
    'ICON_MAPPING_PATH'
] 
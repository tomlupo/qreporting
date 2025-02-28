#!/usr/bin/env python
"""
Example script demonstrating how to use the report generator.
"""

import pandas as pd
import numpy as np
from core import generate_report

def main():
    """Run an example report generation."""
    # Create some example data
    sales_data = pd.DataFrame({
        'Month': pd.date_range(start='2023-01-01', periods=12, freq='M'),
        'Revenue': [95000, 102000, 115000, 125000, 140000, 142000, 
                   135000, 128000, 130000, 137000, 145000, 160000],
        'Expenses': [82000, 85000, 90000, 95000, 100000, 105000, 
                    102000, 98000, 99000, 105000, 110000, 120000],
        'New Customers': [120, 132, 141, 150, 180, 190, 170, 165, 172, 185, 195, 210]
    })
    
    # Calculate some derived metrics
    sales_data['Profit'] = sales_data['Revenue'] - sales_data['Expenses']
    sales_data['Profit Margin'] = (sales_data['Profit'] / sales_data['Revenue'] * 100).round(1)
    
    # Create quarterly summaries
    quarterly_data = sales_data.copy()
    quarterly_data['Quarter'] = quarterly_data['Month'].dt.quarter
    quarterly_data = quarterly_data.groupby('Quarter').agg({
        'Revenue': 'sum',
        'Expenses': 'sum',
        'New Customers': 'sum',
        'Profit': 'sum'
    }).reset_index()
    quarterly_data['Profit Margin'] = (quarterly_data['Profit'] / quarterly_data['Revenue'] * 100).round(1)
    
    # Create product data
    products = pd.DataFrame({
        'Product': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'Category': ['Electronics', 'Electronics', 'Furniture', 'Clothing', 'Accessories'],
        'Units Sold': [1234, 987, 654, 1456, 865],
        'Revenue': [123400, 98700, 65400, 87360, 43250],
        'Cost': [98720, 78960, 45780, 61152, 25950]
    })
    products['Profit'] = products['Revenue'] - products['Cost']
    products['Margin'] = (products['Profit'] / products['Revenue'] * 100).round(1)
    
    # Create customer segmentation data
    customer_segments = {
        'Enterprise': {
            'Count': 25,
            'Revenue': 450000,
            'Average Deal Size': 18000,
            'Retention Rate': '94%'
        },
        'Mid-Market': {
            'Count': 120,
            'Revenue': 720000,
            'Average Deal Size': 6000,
            'Retention Rate': '89%'
        },
        'Small Business': {
            'Count': 350,
            'Revenue': 875000,
            'Average Deal Size': 2500,
            'Retention Rate': '82%'
        },
        'Consumer': {
            'Count': 2800,
            'Revenue': 560000,
            'Average Deal Size': 200,
            'Retention Rate': '73%'
        }
    }
    
    # Regional data
    regions = pd.DataFrame({
        'Region': ['North America', 'Europe', 'Asia Pacific', 'Latin America'],
        'Q1 Sales': [320000, 250000, 180000, 80000],
        'Q2 Sales': [350000, 270000, 190000, 95000],
        'Q3 Sales': [330000, 265000, 200000, 90000],
        'Q4 Sales': [390000, 300000, 230000, 110000]
    })
    regions['Total Sales'] = regions.iloc[:, 1:5].sum(axis=1)
    regions['Growth'] = '+12.5%,+8.2%,+15.3%,-2.1%'.split(',')
    
    # Create the nested dictionary for the report
    report_data = {
        "Dashboard": {
            "Monthly Trend": sales_data
        },
        "Products": {
            "Overview": products,
            "Categories": products.groupby('Category').agg({
                'Units Sold': 'sum',
                'Revenue': 'sum',
                'Cost': 'sum',
                'Profit': 'sum'
            }).reset_index(),
        },
        "Settings": "Report configuration and settings"
    }
    
    # Generate the report
    generate_report(
        report_data,
        output_dir="./example_report",
        report_title="Sales Performance",
        depth=2,
    )
    
    print("Example report generated in ./example_report/")

if __name__ == "__main__":
    main() 
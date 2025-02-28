#!/usr/bin/env python
"""
Report Generator Tool

This script generates HTML reports from nested dictionaries using Jinja2 templates
and integrates with Jupyter notebooks via papermill for content processing.
"""

#------------------------------------------------------------------------------
# IMPORTS AND CONSTANTS
#------------------------------------------------------------------------------

import os
import sys
import shutil
import subprocess
import argparse
import dill
from typing import Dict, Any, Optional, Union, List
import jinja2
import papermill as pm
import pandas as pd
import json

# Constants
DEFAULT_DEPTH = 2
REPORT_TEMPLATE_PATH = "templates/report_template.html"
ICON_MAPPING_PATH = "templates/report_template_icons.json"
NOTEBOOK_TEMPLATE_PATH = "templates/generic_report_template.ipynb"  # Should be provided by user

#------------------------------------------------------------------------------
# HELPER FUNCTIONS
#------------------------------------------------------------------------------

def get_depth_for_key(depth_dict: Dict[str, int], key: str) -> int:
    """
    Get the depth value for a specific key from the depth dictionary.
    
    Args:
        depth_dict (Dict[str, int]): Dictionary mapping keys to depth values
        key (str): The key to look up
        
    Returns:
        int: The depth value for the key, or the default if not found
    """
    # If the key exists, return its depth
    if key in depth_dict:
        return depth_dict[key]
    
    # Otherwise check for a default, or use the global default
    return depth_dict.get('default', DEFAULT_DEPTH)

#------------------------------------------------------------------------------
# MENU STRUCTURE FUNCTIONS
#------------------------------------------------------------------------------

def flatten_dict_to_menu(
    data_dict: Dict[str, Any], 
    depth: Union[int, Dict[str, int]] = DEFAULT_DEPTH, 
    current_depth: int = 1,
    current_key: str = ""
) -> Dict[str, Any]:
    """
    Recursively process nested dictionary to create menu structure.
    
    Args:
        data_dict (Dict[str, Any]): The nested dictionary to process
        depth (Union[int, Dict[str, int]]): Maximum depth to process - either a fixed int or a dict
                                           mapping keys to depths
        current_depth (int): Current depth in the recursion
        current_key (str): Current top-level key being processed
        
    Returns:
        Dict[str, Any]: A menu structure dictionary
    """
    menu = {}
    
    # Handle depth as either int or dict
    max_depth = depth
    if isinstance(depth, dict):
        if current_depth == 1:
            # At top level, we don't have a key yet, so we process each key with its own depth
            for key, value in data_dict.items():
                key_depth = get_depth_for_key(depth, key)
                if isinstance(value, dict) and current_depth < key_depth:
                    # Process with the specific depth for this key
                    submenu = flatten_dict_to_menu(value, depth, current_depth + 1, key)
                    if submenu:  # Only add non-empty submenus
                        menu[key] = submenu
                else:
                    # For leaf nodes or when we've reached max depth
                    if current_depth >= key_depth:
                        # We've reached maximum depth, use an empty dict as placeholder
                        menu[key] = {}
                    else:
                        # For actual leaf nodes (non-dict values) at lower depths
                        menu[key] = value
            return menu
        else:
            # Not at top level, use the current_key to get the depth
            max_depth = get_depth_for_key(depth, current_key)
    
    # Process each item with the determined depth
    for key, value in data_dict.items():
        if isinstance(value, dict) and current_depth < max_depth:
            # Process nested dictionary recursively
            submenu = flatten_dict_to_menu(value, depth, current_depth + 1, current_key)
            if submenu:  # Only add non-empty submenus
                menu[key] = submenu
        else:
            # For leaf nodes or when we've reached max depth
            # If we're at the last depth level, always use an empty dict
            if current_depth >= max_depth:
                # We've reached maximum depth, use an empty dict as placeholder
                menu[key] = {}
            else:
                # For actual leaf nodes (non-dict values) at lower depths
                menu[key] = value
            
    return menu

#------------------------------------------------------------------------------
# CONTENT PROCESSING FUNCTIONS
#------------------------------------------------------------------------------

def process_report_content(
    content: Any, 
    report_name: str,
    temp_dir: str,
    notebook_template: str
) -> str:
    """
    Process report content through a Jupyter notebook template.
    
    Args:
        content (Any): The report content to process
        report_name (str): Name of the report
        temp_dir (str): Directory for temporary files
        notebook_template (str): Path to the notebook template
        
    Returns:
        str: HTML content generated from the notebook
    """
    # Create sanitized filename
    filename = f"{report_name}".lower().replace(' ', '_').replace('/', '-')
    
    # Paths for processing
    pickle_path = os.path.join(temp_dir, f"{filename}.pkl")
    executed_notebook_path = os.path.join(temp_dir, f"{filename}.ipynb")
    html_path = os.path.join(temp_dir, f"{filename}.html")
    
    # Save content to pickle
    with open(pickle_path, 'wb') as f:
        dill.dump(content, f)
    
    try:
        # Execute the notebook with papermill
        pm.execute_notebook(
            notebook_template,
            executed_notebook_path,
            parameters={
                'report_path': pickle_path,
                'title': report_name,
                'paths': sys.path
            }
        )
        
        # Convert notebook to HTML
        subprocess.run(
                [
                    "jupyter", "nbconvert",
                    "--to", "html",
                    executed_notebook_path,
                    "--output", os.path.basename(html_path),
                    "--no-input"
                ],
                check=True  # Ensures it raises an exception if the command fails
            )
        
        # Read the HTML content
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        return html_content
    
    except Exception as e:
        print(f"Error processing content for {report_name}: {e}")
        return f"<div class='error'>Error processing report: {str(e)}</div>"

def collect_all_content(
    data_dict: Dict[str, Any], 
    prefix: str = "",
    temp_dir: str = "",
    notebook_template: str = "",
    depth: Union[int, Dict[str, int]] = DEFAULT_DEPTH,
    current_depth: int = 1,
    content_dict: Optional[Dict[str, str]] = None,
    top_level_key: str = ""
) -> Dict[str, str]:
    """
    Recursively process all content in the nested dictionary and convert to HTML.
    Processes content for items at the target depth level or for leaf nodes at any level.
    
    Args:
        data_dict (Dict[str, Any]): The nested dictionary to process
        prefix (str): Prefix for the report name (for nested reports)
        temp_dir (str): Directory for temporary files
        notebook_template (str): Path to the notebook template
        depth (Union[int, Dict[str, int]]): Maximum depth to process - either a fixed int or a dict
        current_depth (int): Current depth in the recursion
        content_dict (Dict[str, str]): Dictionary to store the HTML content
        top_level_key (str): Current top-level key being processed
        
    Returns:
        Dict[str, str]: Dictionary mapping report paths to HTML content
    """
    if content_dict is None:
        content_dict = {}
    
    # Handle depth as either int or dict
    max_depth = depth
    if isinstance(depth, dict):
        if current_depth == 1:
            # At top level, process each key with its own depth
            for key, value in data_dict.items():
                # Get the depth for this specific key
                key_depth = get_depth_for_key(depth, key)
                new_prefix = f"{prefix}{key}" if prefix else key
                
                if current_depth == key_depth or not isinstance(value, dict):
                    # Process content at the target depth level for this key
                    content_dict[new_prefix] = process_report_content(
                        value,
                        new_prefix,
                        temp_dir,
                        notebook_template
                    )
                elif isinstance(value, dict) and current_depth < key_depth:
                    # Process nested dictionary recursively with this key's depth
                    collect_all_content(
                        value, 
                        f"{new_prefix}/", 
                        temp_dir, 
                        notebook_template,
                        depth,
                        current_depth + 1,
                        content_dict,
                        key
                    )
            return content_dict
        else:
            # Not at top level, use the top_level_key to get the depth
            max_depth = get_depth_for_key(depth, top_level_key)
    
    # Process each item with the determined depth
    for key, value in data_dict.items():
        report_name = f"{prefix}{key}" if prefix else key
        
        if current_depth == max_depth or not isinstance(value, dict):
            # Process content at the target depth level or for any non-dictionary value (leaf nodes)
            content_dict[report_name] = process_report_content(
                value,
                report_name,
                temp_dir,
                notebook_template
            )
        elif isinstance(value, dict) and current_depth < max_depth:
            # Process nested dictionary recursively
            collect_all_content(
                value, 
                f"{report_name}/", 
                temp_dir, 
                notebook_template,
                depth,
                current_depth + 1,
                content_dict,
                top_level_key
            )
            
    return content_dict

#------------------------------------------------------------------------------
# REPORT GENERATION FUNCTIONS
#------------------------------------------------------------------------------

def generate_report(
    data_dict: Dict[str, Any],
    output_dir: str,
    report_title: str = "Report",
    depth: Union[int, Dict[str, int]] = DEFAULT_DEPTH,
    notebook_template: str = NOTEBOOK_TEMPLATE_PATH,
    active_report: Optional[str] = None
) -> None:
    """
    Generate an HTML report from a nested dictionary.
    
    Args:
        data_dict (Dict[str, Any]): The nested dictionary with report data
        output_dir (str): Directory to save the generated report
        report_title (str): Title of the report
        depth (Union[int, Dict[str, int]]): Maximum depth for nested menus - either a fixed int or a dict
                                          mapping keys to depths. If a dict is provided, should include
                                          a 'default' key or DEFAULT_DEPTH will be used as fallback.
        notebook_template (str): Path to the Jupyter notebook template
        active_report (str, optional): The initial active report to display
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create temporary directory for processing
    temp_dir = os.path.join(output_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Create menu structure with empty dictionaries at target depth
        menu_structure = flatten_dict_to_menu(data_dict, depth)
        
        # Process content only for items at the target depth
        all_content = collect_all_content(
            data_dict,
            temp_dir=temp_dir,
            notebook_template=notebook_template,
            depth=depth
        )
        
        # Generate Table of Contents content
        toc_content = generate_table_of_contents(menu_structure)
        
        # Process Table of Contents through notebook template just like other content
        toc_html = process_report_content(
            toc_content,
            "Table of Contents",
            temp_dir,
            notebook_template
        )
        
        # Add Table of Contents to all_content
        all_content["Table of Contents"] = toc_html
        
        # Create links in the menu structure to the generated HTML files
        def add_content_links(menu_dict, prefix="", current_depth=1, top_key=""):
            """Recursively add links to HTML content files in the menu structure."""
            updated_menu = {}
            
            # Determine the max depth for this branch
            max_depth = depth
            if isinstance(depth, dict):
                if current_depth == 1:
                    # We're at the top level, so we'll process each key separately
                    for key, value in menu_dict.items():
                        # Get the depth for this specific key
                        key_depth = get_depth_for_key(depth, key)
                        item_path = f"{prefix}{key}" if prefix else key
                        item_filename = item_path.lower().replace(' ', '_').replace('/', '-') + '.html'
                        
                        if isinstance(value, dict):
                            if current_depth < key_depth - 1:
                                # Continue recursion for nested menus
                                updated_menu[key] = add_content_links(value, f"{item_path}/", current_depth + 1, key)
                            else:
                                # We're at the level just before target depth - add links to content files
                                linked_submenu = {}
                                for subkey in value.keys():
                                    sub_path = f"{item_path}/{subkey}"
                                    sub_filename = sub_path.lower().replace(' ', '_').replace('/', '-') + '.html'
                                    linked_submenu[subkey] = sub_filename
                                updated_menu[key] = linked_submenu
                        else:
                            # For non-dict values or empty placeholders at max depth
                            updated_menu[key] = item_filename
                    
                    return updated_menu
                else:
                    # Not at top level, use the top_key to get the depth
                    max_depth = get_depth_for_key(depth, top_key)
            
            # Process each item with the determined depth
            for key, value in menu_dict.items():
                item_path = f"{prefix}{key}" if prefix else key
                item_filename = item_path.lower().replace(' ', '_').replace('/', '-') + '.html'
                
                if isinstance(value, dict):
                    if current_depth < max_depth - 1:
                        # Continue recursion for nested menus
                        updated_menu[key] = add_content_links(value, f"{item_path}/", current_depth + 1, top_key)
                    else:
                        # We're at the level just before target depth - add links to content files
                        linked_submenu = {}
                        for subkey in value.keys():
                            sub_path = f"{item_path}/{subkey}"
                            sub_filename = sub_path.lower().replace(' ', '_').replace('/', '-') + '.html'
                            linked_submenu[subkey] = sub_filename
                        updated_menu[key] = linked_submenu
                else:
                    # For non-dict values or empty placeholders at max depth
                    updated_menu[key] = item_filename
            
            return updated_menu
        
        # Add links to content files in the menu structure
        linked_menu = add_content_links(menu_structure)
        
        # Set Table of Contents as default content if no active_report is specified
        if not active_report:
            active_content = all_content.get("Table of Contents")
        else:
            active_content = all_content.get(active_report, "")
        
        # Create Table of Contents link
        table_of_contents_link = "table_of_contents.html"
        
        # Load icon mappings
        icon_mappings = {}
        try:
            with open(ICON_MAPPING_PATH, 'r') as f:
                icon_mappings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load icon mappings: {e}")
            # Use default fallback if file cannot be loaded
            icon_mappings = {
                "Dashboard": "home",
                "Reports": "chart-bar",
                "Settings": "cog",
                "Table of Contents": "sitemap"
            }
        
        # Load Jinja template
        env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
        template = env.get_template(REPORT_TEMPLATE_PATH)
        
        # Render template
        html_output = template.render(
            menu_structure=linked_menu,
            active_content=active_content,
            active_report=active_report or "Table of Contents",
            report_title=report_title,
            table_of_contents_link=table_of_contents_link,
            default_icons=icon_mappings
        )
        
        # Write main index.html
        index_path = os.path.join(output_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        # Save all individual reports
        for report_name, content in all_content.items():
            # Create sanitized filename
            filename = report_name.lower().replace(' ', '_').replace('/', '-')
            report_path = os.path.join(output_dir, f"{filename}.html")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    except Exception as e:
        print(f"Error generating report: {e}")
        raise
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

def generate_simple_report(
    content: Any,
    report_name: str,
    output_dir: str,
    notebook_template: str = NOTEBOOK_TEMPLATE_PATH
) -> str:
    """
    Generate a simple HTML report file from data without generating the full report structure.
    
    This function processes a single piece of content and saves it as an HTML file.
    It's useful for generating standalone reports or individual report components.
    
    Args:
        content (Any): The content to process (can be any data type that the notebook template can handle)
        report_name (str): Name of the report (will be used in the title and filename)
        output_dir (str): Directory where the HTML file will be saved
        notebook_template (str): Path to the Jupyter notebook template for processing
        
    Returns:
        str: Path to the generated HTML file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create temporary directory for processing
    temp_dir = os.path.join(output_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Process the content to generate HTML
        html_content = process_report_content(
            content,
            report_name,
            temp_dir,
            notebook_template
        )
        
        # Create sanitized filename
        filename = report_name.lower().replace(' ', '_').replace('/', '-') + '.html'
        report_path = os.path.join(output_dir, filename)
        
        # Save the HTML content to a file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Report created successfully: {report_path}")
        return report_path
        
    except Exception as e:
        print(f"Error creating simple report: {e}")
        raise
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

#------------------------------------------------------------------------------
# HTML CONTENT GENERATION FUNCTIONS
#------------------------------------------------------------------------------

def generate_table_of_contents(menu_structure: Dict[str, Any]) -> str:
    """
    Generate a simple HTML structure for the Table of Contents.
    
    Args:
        menu_structure (Dict[str, Any]): The menu structure
        
    Returns:
        str: Simple HTML for the Table of Contents to be processed through the notebook template
    """
    # Create a function to recursively build the ToC HTML
    def build_toc_html(structure, current_path=""):
        html = "<ul>"
        for key, value in structure.items():
            # Build the full path for this item
            item_path = f"{current_path}/{key}" if current_path else key
            link_id = item_path.lower().replace(' ', '_').replace('/', '-')
            
            html += f'<li><strong>{key}</strong>'
            
            if isinstance(value, dict) and value:
                # For items with children
                html += build_toc_html(value, item_path)
            else:
                # For leaf items
                filename = link_id + '.html'
                html += f' - <a href="{filename}">{key}</a>'
            
            html += '</li>'
        
        html += "</ul>"
        return html

    # Return simple HTML that will be processed through the notebook
    #toc_html = "<h1>Table of Contents</h1>"
    toc_html = build_toc_html(menu_structure)
    
    return toc_html

def generate_table_of_contents_content(
    menu_structure: Dict[str, Any],
    data_dict: Dict[str, Any],
    depth: Union[int, Dict[str, int]]
) -> str:
    """
    Generate HTML content for the Table of Contents.
    
    Args:
        menu_structure (Dict[str, Any]): The menu structure
        data_dict (Dict[str, Any]): The original data dictionary
        depth (Union[int, Dict[str, int]]): The depth of the menu - either a fixed int or a dict
        
    Returns:
        str: HTML content for the Table of Contents
    """
    # Use the new simpler function
    return generate_table_of_contents(menu_structure)
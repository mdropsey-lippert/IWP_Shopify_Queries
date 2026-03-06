#!/usr/bin/env python3
"""
Script: This script is used to get the variants for a given vendor.
        Paginate the batches of 250 products from Shopify until end of list is reached. 
        For each product, get the variants and add them to a list. Return the list of variants.

Version: 1.0.0

Purpose: 
    - Building script to get the variants for a given vendor. This will be used to update the shipping profile for the variants in bulk.

Process is as follows:
    - Get the vendor name as input from the user.
    - Get the list of products for the given vendor from Shopify using the GraphQL API.
    - For each product, get the variants and add them to a list.
    - Return the list of variants.

Requirements:
    - pip install -r requirements.txt

Example:
    -
"""

# ------------ Imports ----------------
from utils import email_errors, email_vars
from dotenv import load_dotenv
from typing import List, Dict, Any, Set, Optional
import requests
import json
import os
# -------------------------------------

# ---------- Constants/Variables ----------------
DEBUG = False
HEADER_CONTENT_TYPE = 'application/json'
script_path = os.path.abspath(__file__)
WORKING_DIR = os.path.dirname(script_path)
# -----------------------------------------------

# print(WORKING_DIR)


def get_variants(vendor_name) -> Dict[str, Any]:
    """Function to get the variants for a given vendor from Shopify using the GraphQL API.
    Args:
        vendor_name (str): The name of the vendor to get the variants for."""

    # Build return variables
    response_list = []
    variant_dict = {}
    non_physical_item = {}

    # Use .env file to store the Shopify API credentials and other configuration settings.  Load the .env file to access the variables.
    load_dotenv()
    api_version = os.getenv('SHOPIFY_API_VERSION')
    api_key = os.getenv('SHOPIFY_API_KEY')
    url = os.getenv('SHOPIFY_STORE_URL') + 'admin/api/' + \
        api_version + '/graphql.json'

    # Use a Dictionary to store the headers.  Dict[str, str] forces the keys and values to be strings.
    header: Dict[str, str] = {
        'X-Shopify-Access-Token': api_key,
        'Content-Type': HEADER_CONTENT_TYPE}

    # Cursor will be used for pagination in the GraphQL query. Will be str or None.
    cursor: Optional[str] = None
    variant_count = 1
    # vendor_name = "'" + vendor_name + "'"
    # print(vendor_name)

    # Using a Dictionary to store the variables for GraphQL, forcing the keys to be strings and the values to be any type.
    variables: Dict[str, any] = {
        'first': 250,
        'query': f'vendor:\'{vendor_name}\' AND -tag:LocalPAI'
    }

    while True:
        # GraphQL query to get the products for a given vendor.  Will need to be paginated until hasNextPage is False.
        query = """query getProducts($first: Int!, $after: String, $query: String) {
            products(first: $first, after: $after, query: $query) {
                edges {
                node {
                    vendor
                    variants(first: 50) {
                    edges { node { id sku inventoryItem{
											requiresShipping
										}} }
                    }
                }
                }
                pageInfo { hasNextPage endCursor }
            }
            }"""

        # If cursor is not None, add it to the variables for the GraphQL query.
        if cursor:
            variables['after'] = cursor

        # Make the POST request to the Shopify GraphQL API.
        response = requests.post(
            url,
            headers=header,
            json={'query': query, 'variables': variables},
            timeout=60)

        # Check if the response is successful. If not, log the error and send an email.
        error_msg = ""
        response.raise_for_status()
        status = response.status_code
        if status != 200:
            error_msg = f"GraphQL query failed with status code {status}: {response.text}"

        # Check response for errors. If so, log the error and send an email.
        data = response.json()
        if "errors" in data and data["errors"]:
            error_msg = f"GraphQL query returned errors: {data['errors']}"

        if error_msg:
            send_to, subject, log_path = email_vars
            email_errors(send_to, subject, error_msg,
                         __file__, log_path)
            raise RuntimeError(error_msg)

        # Process the data to get the variants.
        # Assign the products and edges to variables.  Use .get() with default values to avoid KeyErrors if the expected keys are not in the response.
        products = (data.get("data") or {}).get("products") or {}
        edges = products.get("edges") or []

        # Loop through all of the edges array to get the variants for each product.  Return the variant_id and sku fields
        for edge in edges:
            node = edge.get("node") or {}
            vendor = node.get("vendor") or ""
            if vendor.casefold() != str(vendor_name).casefold():
                print(
                    f"Warning: Vendor name mismatch. Expected '{vendor_name}', but got '{vendor}'. Skipping this product.")
            else:
                variants = node.get("variants") or {}
                variant_edges = variants.get("edges") or []
                for variant_edge in variant_edges:
                    variant_node = variant_edge.get("node") or {}
                    variant_id = variant_node.get("id")
                    variant_sku = variant_node.get("sku")
                    inv_item = variant_node.get("inventoryItem") or {}
                    requires_shipping = inv_item.get("requiresShipping")
                    if requires_shipping is True:
                        variant_count += 1

                        # Assign results to a dictionary and append to the response list.
                        variant_dict[variant_id] = variant_sku
                    else:
                        non_physical_item[variant_id] = variant_sku
                        print(
                            f"Variant with ID '{variant_id}' and SKU '{variant_sku}' is NOT a physical item on Shopify.  Saving to file...")

        # Print results of combing through the response.
        print(
            f"Total variants retrieved for vendor '{vendor_name}': {variant_count - 1}")
        # print("Response list of variants:", response_list)

        # Check if the pagination continues.  Break the loop if neither of the page_info fields have values.
        page_info = products.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break

        # Set up small batch testing of logic.
        if DEBUG:
            if variant_count > 1000:
                print(
                    f"Exiting before fully complete for debugging purposes.  Expected to have {variant_count - 1} variants in the response list.")
                break

    return variant_dict, non_physical_item


def main():
    # print('main is running. This is where the main logic of the script will go.')
    # print(WORKING_DIR)
    output_dir = os.path.join(WORKING_DIR, r'script_files\output')
    output_file = os.path.join(output_dir, 'variants_by_vendor.json')
    invalid_output_file = os.path.join(output_dir, 'non_physical_items.json')
    """
    vendor_lookup_name = input(
        "Enter the vendor name to get the variants for: ")
    """
    vendor_lookup_name = "PAI Industries"

    # Write valid items to JSON file.
    with open(output_file, 'w') as result_file:
        response = get_variants(vendor_name=vendor_lookup_name)
        json.dump(response[0], result_file, indent=4)
    print(
        f"Variants for vendor: '{vendor_lookup_name}' have been written to {output_file}.")

    if response[1]:
        with open(invalid_output_file, 'w') as invalid_file:
            json.dump(response[1], invalid_file, indent=4)
        print(
            f"Non-physical items for vendor: '{vendor_lookup_name}' have been written to {invalid_output_file}.")


if __name__ == '__main__':
    main()
    print(f'Script {__file__} complete.')

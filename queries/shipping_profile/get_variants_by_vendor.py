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
# -----------------------------------------------


def get_variants(vendor_name):
    """Function to get the variants for a given vendor from Shopify using the GraphQL API.
    Args:
        vendor_name (str): The name of the vendor to get the variants for."""

    load_dotenv()
    cursor = Optional[str] = None
    api_version = os.getenv('SHOPIFY_API_VERSION')
    api_key = os.getenv('SHOPIFY_API_KEY')
    url = os.getenv('SHOPIFY_STORE_URL') + 'admin/api/' + \
        api_version + '/graphql.json'
    header = {
        'X-Shopify-Access-Token': api_key,
        'Content-Type': HEADER_CONTENT_TYPE}
    variables: Dict[str, any] = {
        'first': 250,
        'query': f'vendor:\'{vendor_name}\' AND -tag:LocalPAI'
    }
    query = """query getProducts($first: Int!, $after: String, $query: String) {
          products(first: $first, after: $after, query: $query) {
            edges {
              node {
                variants(first: 50) {
                  edges { node { id sku } }
                }
              }
            }
            pageInfo { hasNextPage endCursor }
          }
        }"""

    pass


def main():
    print('main is running. This is where the main logic of the script will go.')
    load_dotenv()
    print(os.getenv('SHOPIFY_API_KEY'))
    pass


if __name__ == '__main__':
    main()

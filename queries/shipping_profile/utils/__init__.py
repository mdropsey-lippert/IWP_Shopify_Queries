#!/usr/bin/env python3
"""
Set initial variables/package imports for all modules in shipping_profile folder.
This file is imported into all other modules to ensure consistency across the folder and to avoid hardcoding variables in multiple places.
"""
# ------------ Imports ----------------
from .lippert_email import email_errors
import os
# -------------------------------------


# ------------ Constants ----------------
DEBUG = False
EMAIL_RECIPIENTS = 'mdropsey@lippertent.com,austin.ashley@lippertent.com'
EMAIL_SUBJECT = 'IWP_SHOPIFY_QUERIES: Error in Shipping Profile Update Script'
EMAIL_MSG = 'Please see error log for details.'
LOG_PATH = r'.\script_files\logs'
WORKING_DIR = str(os.getcwd())
# ---------------------------------------


# ------------ Variables ----------------
email_vars = (EMAIL_RECIPIENTS, EMAIL_SUBJECT, LOG_PATH)
# ---------------------------------------

print('__init__.py loaded successfully. Shipping Profile Utils are ready to use.')

# End of __init__.py

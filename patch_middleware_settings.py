#!/usr/bin/env python3
"""
Patch script to add DomainRedirectMiddleware to Django settings.py
This script is automatically executed during deployment to ensure the middleware is active.
"""

import os
import re

def patch_settings():
      settings_file = 'go2events/settings.py'

    if not os.path.exists(settings_file):
              print(f"Error: {settings_file} not found")
              return False

    with open(settings_file, 'r') as f:
              content = f.read()

    # Check if middleware is already added
    if "'go2events.middleware.DomainRedirectMiddleware'" in content:
              print("Middleware already added to settings.py")
              return True

    # Find the MIDDLEWARE list and add our middleware
    # Look for the pattern: MIDDLEWARE = [
    pattern = r"(MIDDLEWARE\s*=\s*\[)"

    # Add our middleware as the first item after the opening bracket
    replacement = r"\1\n    'go2events.middleware.DomainRedirectMiddleware',"

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
              print("Error: Could not find MIDDLEWARE list in settings.py")
              return False

    with open(settings_file, 'w') as f:
              f.write(new_content)

    print("Successfully added DomainRedirectMiddleware to settings.py")
    return True

if __name__ == '__main__':
      patch_settings()
  

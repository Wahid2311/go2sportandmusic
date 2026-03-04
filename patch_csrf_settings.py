#!/usr/bin/env python
"""
Script to patch Django settings for CSRF_TRUSTED_ORIGINS at runtime.
This ensures the new domain is included in CSRF trusted origins.
"""

import os
import sys

def patch_csrf_settings():
    """Patch Django settings to include the new domain in CSRF_TRUSTED_ORIGINS"""
    
    # Set up Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'go2events.settings')
    
    try:
        import django
        from django.conf import settings
        
        # Add the new domain to CSRF_TRUSTED_ORIGINS if not already present
        current_origins = list(settings.CSRF_TRUSTED_ORIGINS) if hasattr(settings, 'CSRF_TRUSTED_ORIGINS') else []
        
        new_origins = [
            'https://go2sportandmusic.com',
            'https://www.go2sportandmusic.com',
        ]
        
        updated = False
        for origin in new_origins:
            if origin not in current_origins:
                current_origins.append(origin)
                updated = True
                print(f"✓ Added {origin} to CSRF_TRUSTED_ORIGINS")
        
        if updated:
            settings.CSRF_TRUSTED_ORIGINS = current_origins
            print(f"\n✓ CSRF_TRUSTED_ORIGINS updated successfully!")
            print(f"  Current origins: {settings.CSRF_TRUSTED_ORIGINS}")
        else:
            print("✓ All required origins already present in CSRF_TRUSTED_ORIGINS")
            
    except Exception as e:
        print(f"✗ Error patching CSRF settings: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail, just continue
        return False
    
    return True


if __name__ == '__main__':
    success = patch_csrf_settings()
    sys.exit(0 if success else 1)

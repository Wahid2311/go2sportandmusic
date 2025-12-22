"""
Stadium configuration for mapping section names to SVG data-section attributes
"""

# Mapping of SVG data-section values to common section name variations
SECTION_NAME_MAPPINGS = {
    # Longside sections
    'longside-lower-tier': [
        'Longside Lower Tier',
        'Main Stand Lower',
        'East Stand Lower',
        'West Stand Lower',
        'Central Lower Longside',
    ],
    'longside-upper-tier': [
        'Longside Upper Tier',
        'Main Stand Upper',
        'East Stand Upper',
        'West Stand Upper',
    ],
    
    # Shortside sections
    'shortside-lower-tier': [
        'Shortside Lower Tier',
        'North Stand Lower',
        'South Stand Lower',
        'Anfield Road Lower',
    ],
    'shortside-upper-tier': [
        'Shortside Upper Tier',
        'North Stand Upper',
        'South Stand Upper',
        'Anfield Road Upper',
    ],
    
    # VIP sections
    'vip-club-level': [
        'VIP Packages',
        'VIP Club Level',
        'Premium Seating',
        'Club Level Longside',
        'Club Level Shortside',
    ],
    'premium-level-hospitality': [
        'Premium Level Hospitality',
        'Hospitality',
        'Premium Seating',
        'Centenary Club',
        'Premier Club',
    ],
    'vip-hospitality-package': [
        'VIP Hospitality Package',
        'Brodies Lounge',
        'Executive Lounge',
        'Dugout Hospitality',
        'Joe\'s West',
        'Joe\'s East',
        'Legends',
        '1894 Club Bar',
        'Citizens',
        'The Mancunian',
        'The Chairman\'s Club',
        'The Tunnel Club',
        'Commonwealth Bar',
    ],
    
    'vip-93-20': [
        '93:20',
        '93:20 Lounge',
        '93 20',
        'The 93:20',
    ],
    # Away fans
    'away-fans-section': [
        'Away Fan Section',
        'Away Fans',
        'Away Section',
        'Away Supporters Only',
    ],
    
    # Specific stadium sections
    'kop-grandstand': [
        'Kop Grandstand',
        'The Kop',
    ],

    # Santiago Bernabeu sections
    'category-1-gol': [
        'Category 1 Gol',
        'Cat 1 Gol',
        'Gol',
    ],
    'category-2-fondo': [
        'Category 2 Fondo',
        'Cat 2 Fondo',
        'Fondo',
    ],
    'category-1-premium': [
        'Category 1 Premium',
        'Cat 1 Premium',
    ],
    'category-1-silver': [
        'Category 1 Silver',
        'Cat 1 Silver',
    ],
    'category-1': [
        'Category 1',
        'Cat 1',
    ],
    'category-2-lateral': [
        'Category 2 Lateral',
        'Cat 2 Lateral',
        'Lateral',
    ],
    'category-3': [
        'Category 3',
        'Cat 3',
    ],
    'category-1-superior': [
        'Category 1 Superior',
        'Cat 1 Superior',
    ],
    'category-2-superior': [
        'Category 2 Superior',
        'Cat 2 Superior',
    ],
}

# Reverse mapping for quick lookup
SVG_TO_SECTION_NAMES = {}
for svg_key, variations in SECTION_NAME_MAPPINGS.items():
    for variation in variations:
        SVG_TO_SECTION_NAMES[variation.lower()] = svg_key


def normalize_section_name(section_name):
    """
    Convert a section name to its SVG-compatible data-section attribute value
    
    Args:
        section_name (str): The section name from the database (e.g., "Longside Lower Tier")
    
    Returns:
        str: The SVG data-section value (e.g., "longside-lower-tier")
    """
    if not section_name:
        return None
    
    # Clean and lowercase the section name
    name_clean = section_name.strip().lower()
    
    # Try direct lookup first
    if name_clean in SVG_TO_SECTION_NAMES:
        return SVG_TO_SECTION_NAMES[name_clean]
    
    # Try partial matching
    for svg_key, variations in SECTION_NAME_MAPPINGS.items():
        for variation in variations:
            if variation.lower() in name_clean or name_clean in variation.lower():
                return svg_key
    
    # Fallback: convert to kebab-case
    # Replace spaces with hyphens and remove special characters
    return name_clean.replace(' ', '-').replace('_', '-')


def get_svg_key_from_stadium_name(stadium_name):
    """
    Auto-detect SVG key from stadium name
    
    Args:
        stadium_name (str): The stadium name (e.g., "Villa Park")
    
    Returns:
        str: The SVG key or None if not found
    """
    if not stadium_name:
        return None
    
    # Stadium name to SVG key mapping
    STADIUM_MAPPING = {
        'villa park': 'villaParkStadium',
        'old trafford': 'oldTraffordStadium',
        'emirates': 'emiratesStadium',
        'anfield': 'anfieldStadium',
        'elland': 'ellandStadium',
        'elland road': 'ellandStadium',
        'tottenham': 'tottenhamHotspurStadium',
        'spurs': 'tottenhamHotspurStadium',
        'hill dickinson': 'hillDickinsonStadium',
        'san siro': 'sanSiro',
        'molineux': 'molineux',
        'craven cottage': 'cravenCottage',
        'etihad': 'etihadStadium',
        'etihad stadium': 'etihadStadium',
        'santiago bernabéu': 'santiagoBernabeuStadium',
        'santiago bernabeu': 'santiagoBernabeuStadium',
        'riyadh metropolitano': 'riyadhMetropolitanoStadium',
        'riyadh metropolitano stadium': 'riyadhMetropolitanoStadium',
    }
    
    name_lower = stadium_name.lower().strip()
    
    # Try exact match first
    if name_lower in STADIUM_MAPPING:
        return STADIUM_MAPPING[name_lower]
    
    # Try partial match
    for key, svg in STADIUM_MAPPING.items():
        if key in name_lower:
            return svg
    
    return None

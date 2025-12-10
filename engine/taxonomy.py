"""
engine/taxonomy.py

Defines the Sector -> Industry hierarchy for the EvolveX system.
"""

TAXONOMY = {
    "Services": {
        "Tourism & Hospitality": {
            "focus": "Hotels, resorts, travel agencies, transport services, eco-tourism",
            "contribution": "Largest contributor to GDP"
        },
        "Financial Services": {
            "focus": "Banking (Commercial & Central), Insurance, Real Estate, Stock Market",
            "contribution": "Significant support for other industries"
        },
        "IT & Telecommunications": {
            "focus": "Software development, IT Enabled Services (ITES), Business Process Outsourcing (BPO), Telecommunication infrastructure",
            "contribution": "Fast-growing export revenue earner"
        },
        "Transportation & Logistics": {
            "focus": "Port services (Port of Colombo as a transshipment hub), air cargo, maritime services",
            "contribution": "Critical due to strategic geographic location"
        }
    },
    "Industry": {
        "Textiles & Apparel": {
            "focus": "Manufacturing and export of high-quality clothing",
            "contribution": "Dominant manufacturing industry"
        },
        "Processing of Commodities": {
            "focus": "Value addition to rubber, coconut, and tea products",
            "contribution": "Link between agriculture and industry"
        },
        "Construction": {
            "focus": "Infrastructure development, housing, commercial projects, real estate",
            "contribution": "Important for domestic growth"
        }
    },
    "Agriculture": {
        "Tea": {
            "focus": "Cultivation, processing, and export of Ceylon Tea",
            "contribution": "Major traditional export commodity"
        },
        "Rubber": {
            "focus": "Cultivation and sourcing for local/exported rubber products",
            "contribution": "Important raw material source"
        },
        "Coconut": {
            "focus": "Production of desiccated coconut, coir, copra, and coconut oil",
            "contribution": "Significant for both domestic use and export"
        }
    },
    "Other": {
        "Gem & Jewellery": {
            "focus": "Mining and export of precious stones, especially sapphires",
            "contribution": "Niche but high-value export"
        },
        "Foreign Employment": {
            "focus": "Earnings sent back by Sri Lankans working abroad",
            "contribution": "Crucial source of foreign currency"
        }
    }
}

# Flattened list of industries for classification
ALL_INDUSTRIES = []
for sector, industries in TAXONOMY.items():
    for ind_name in industries.keys():
        ALL_INDUSTRIES.append(ind_name)

# Thematic Categories (Tier 2)
THEMATIC_CATEGORIES = [
    "Macro/Economic Policy",
    "Extreme Weather Events",
    "Trade & Foreign Relations",
    "Corporate/Company News",
    "Regulatory & Governance",
    "ICT & Digital Services",
    "Market Trends",
    "Social/Political Issues"
]

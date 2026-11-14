"""
AgriOptima - Virtual Farmer Community Seed Service
Populates authentic localized and global agricultural discussions and chat messages.
"""

from ..models import CommunityPost, CommunityReply, CommunityChatMessage

SEED_POSTS = [
    {
        "author_name": "Harpreet S. Gill",
        "author_location": "Ludhiana, Punjab, India",
        "latitude": 30.9010,
        "longitude": 75.8573,
        "crop_type": "Wheat",
        "category": "fertilizer",
        "title": "Split Urea application before canal irrigation: Is 30% basal enough?",
        "content": "Running HD-3086 wheat on sandy loam. AgriOptima recommended 1.8 bags Urea and 1.3 bags DAP. I applied DAP basal at sowing with 30% Urea. Crown root initiation is coming in 5 days. Should I top-dress 40% Urea 24 hours before opening the tubewell or wait until post-irrigation?",
        "soil_metrics_json": "N: 48, P: 20, K: 42 kg/ha | pH: 7.2",
        "upvotes": 14,
        "replies": [
            {
                "author_name": "Gurmeet Dhillon",
                "author_location": "Khanna, Punjab, India",
                "content": "Harpreet veere, definitely apply 1 day before light irrigation so water carries dissolved nitrogen down into the active root zone (crown roots). If you broadcast after ponding, you risk losing 15-20% to ammonia volatilization under hot afternoon sun."
            },
            {
                "author_name": "Dr. Balwinder Singh (PAU)",
                "author_location": "Punjab Agri Extension",
                "content": "Agreed with Gurmeet. Just ensure soil is not completely dry. If temperature is above 26°C, apply in late evening right before water reaches the plot."
            }
        ]
    },
    {
        "author_name": "Mateo Rossi",
        "author_location": "Pergamino, Buenos Aires, Argentina",
        "latitude": -33.8900,
        "longitude": -60.5730,
        "crop_type": "Maize",
        "category": "alert",
        "title": "Heavy rain forecast (+65mm) in Pampas: High nitrate leaching warning",
        "content": "Attention maize growers in northern Buenos Aires & southern Santa Fe! Open-Meteo shows an intense storm front arriving Thursday night. Delay your planned side-dress UAN/Urea by 48-72 hours. Soil moisture is already at field capacity; any surface broadcast will wash into drainage canals.",
        "soil_metrics_json": "Rainfall: +65mm alert | Leaching Risk: CRITICAL",
        "upvotes": 28,
        "replies": [
            {
                "author_name": "Facundo Alvarez",
                "author_location": "Rojas, Argentina",
                "content": "Gracias Mateo! Saved me 40 hectares of side-dressing tomorrow morning. Holding tractors in the shed until Saturday."
            }
        ]
    },
    {
        "author_name": "Caleb Vance",
        "author_location": "Des Moines, Iowa, USA",
        "latitude": 41.5868,
        "longitude": -93.6250,
        "crop_type": "Maize",
        "category": "equipment",
        "title": "Tractor VRA GeoJSON test on John Deere Gen 4 display - Worked perfectly!",
        "content": "Exported the Multi-Zone Farm Field prescription from AgriOptima as GeoJSON, converted via shapefile tool, and loaded onto my 8R tractor. The variable rate controller modulated N-P-K cleanly across 4 field zones with 0 latency. Saved ~18% fertilizer on our ridge knoll where organic matter was already 4.2%.",
        "soil_metrics_json": "Zones: 4 | Area: 120 ha | Input Savings: $1,420",
        "upvotes": 35,
        "replies": [
            {
                "author_name": "David Miller",
                "author_location": "Ames, Iowa, USA",
                "content": "Did you need to smooth the boundary polygons between zones or did the rate controller step smoothly? Planning to test on our Case IH Pro 700 next week."
            },
            {
                "author_name": "Caleb Vance",
                "author_location": "Des Moines, Iowa, USA",
                "content": "Step was super smooth David. I set a 15-meter lookahead buffer in the terminal and it transitioned rates in under 1.5 seconds without lag."
            }
        ]
    },
    {
        "author_name": "Jean-Pierre Laurent",
        "author_location": "Beauceron Plains, France",
        "latitude": 48.4468,
        "longitude": 1.4889,
        "crop_type": "Wheat",
        "category": "fertilizer",
        "title": "Liming acidic clay soil (pH 5.4) before spring winter-wheat tillering",
        "content": "Our soil test came back with pH 5.4 and high exchangeable aluminum. AgriOptima flagged phosphorus fixation risk (aluminum phosphate lockout). We are calculating agricultural lime dosage. Anyone tried micro-pelletized calciprill at 250 kg/ha directly in furrow?",
        "soil_metrics_json": "pH: 5.4 | Al-Sat: 18% | P available: 12 kg/ha",
        "upvotes": 19,
        "replies": [
            {
                "author_name": "Henri Dubois",
                "author_location": "Eure-et-Loir, France",
                "content": "Jean-Pierre, pelletized lime works well for localized seedling protection, but for full field P bioavailability you'll eventually need a broadcast of 2.5 t/ha ground calcitic limestone after harvest."
            }
        ]
    },
    {
        "author_name": "Ananya Sharma",
        "author_location": "Nagpur, Maharashtra, India",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "crop_type": "Cotton",
        "category": "market",
        "title": "MOP (0-0-60) availability & boll-weight response in black cotton vertisol",
        "content": "Local cooperative society in Wardha just received fresh stock of MOP at subsidized rates (₹1,700/bag). If your cotton is at squaring or early flowering stage, don't skip potash. The SLSQP recipe called for 1.2 bags MOP and our lint fiber strength improved noticeably last season.",
        "soil_metrics_json": "Soil: Deep Black Vertisol | Crop: Cotton (Bt-II)",
        "upvotes": 22,
        "replies": []
    }
]

SEED_CHAT = [
    {
        "author_name": "Rajesh Patel",
        "author_location": "Ahmedabad, Gujarat",
        "channel": "nearby",
        "message": "Good morning farmers! Clear skies today. Starting second dose of micronutrient zinc spray on cotton."
    },
    {
        "author_name": "Vikram Chauhan",
        "author_location": "Karnal, Haryana",
        "channel": "nearby",
        "message": "Ground temperature touched 18°C this morning. Perfect window for sowing wheat PBW-826."
    },
    {
        "author_name": "Tyler Evans",
        "author_location": "Lincoln, Nebraska",
        "channel": "global",
        "message": "Moisture sensors showing 32% volumetric water content at 12 inches depth. Excellent soil moisture for winter dormancy."
    },
    {
        "author_name": "AgriOptima Bot",
        "author_location": "Precision AI Network",
        "channel": "alerts",
        "message": "⚠️ Weather Radar Advisory: Moderate rain front tracking across Central Plains. Check your 4R split schedule before top-dressing."
    }
]


def seed_community_if_empty():
    """Seeds the community database if no posts exist."""
    if CommunityPost.objects.count() > 0:
        return

    for p_data in SEED_POSTS:
        replies_data = p_data.pop("replies", [])
        post = CommunityPost.objects.create(**p_data)
        for r_data in replies_data:
            CommunityReply.objects.create(post=post, **r_data)

    if CommunityChatMessage.objects.count() == 0:
        for c_data in SEED_CHAT:
            CommunityChatMessage.objects.create(**c_data)

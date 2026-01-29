# Configuration and color scheme for the Skills Recommender App

# Color Scheme
COLORS = {
    "primary_dark": "#3e4f28",      # Dark olive
    "secondary": "#99a18b",          # Sage
    "background": "#e5e6de",         # Light cream
    "accent": "#738063",             # Moss
    "light_accent": "#c9cdc1",       # Pale sage
    "mid_accent": "#556443",         # Forest
    "white": "#ffffff",
    "text_dark": "#2d3a1f",          # Dark text
}

# Demo credentials
DEMO_CREDENTIALS = {
    "demo": "demo123",
    "Student 1": "demo123",
    "Student 2": "demo123",
}

# Skills categories - Media, Animation & Film focused
SKILLS_CATEGORIES = {
    "Animation & Motion": [
        "2D Animation", "3D Animation", "Motion Graphics", "Character Animation",
        "Stop Motion", "Rigging", "Storyboarding", "Animatics"
    ],
    "Video Production": [
        "Cinematography", "Video Editing", "Color Grading", "Sound Design",
        "Directing", "Screenwriting", "Documentary", "Live Streaming"
    ],
    "Visual Effects & Post": [
        "Compositing", "VFX", "Rotoscoping", "Matte Painting",
        "3D Modeling", "Texturing", "Lighting", "Rendering"
    ],
    "Design & Creative": [
        "Graphic Design", "UI/UX Design", "Illustration", "Typography",
        "Brand Design", "Concept Art", "Digital Painting", "Photo Editing"
    ],
    "Software & Tools": [
        "After Effects", "Premiere Pro", "DaVinci Resolve", "Final Cut Pro",
        "Maya", "Blender", "Cinema 4D", "Nuke", "Photoshop", "Illustrator"
    ],
}

# Interest areas for bubble selection
INTEREST_AREAS = [
    {"id": "film", "label": "Film & Cinema"},
    {"id": "animation", "label": "Animation"},
    {"id": "vfx", "label": "Visual Effects"},
    {"id": "motion", "label": "Motion Graphics"},
    {"id": "gaming", "label": "Game Cinematics"},
    {"id": "commercial", "label": "Commercials & Ads"},
    {"id": "music_video", "label": "Music Videos"},
    {"id": "documentary", "label": "Documentary"},
    {"id": "social", "label": "Social Media Content"},
    {"id": "broadcast", "label": "Broadcast & TV"},
    {"id": "corporate", "label": "Corporate Video"},
    {"id": "indie", "label": "Indie Films"},
]

# Experience levels
EXPERIENCE_LEVELS = {
    1: "Beginner",
    2: "Elementary",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert"
}

# App settings
APP_CONFIG = {
    "title": "Better Youth Creative Lab",
    "page_icon": None,
    "layout": "wide",
}

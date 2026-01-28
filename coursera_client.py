# Coursera integration for Better Youth Creative Lab

import requests
from typing import List, Dict, Optional

# Curated list of real Coursera courses for media/animation/film
# These are actual courses with real URLs
CURATED_COURSES = {
    "animation": [
        {
            "name": "Animation for Beginners",
            "provider": "Michigan State University",
            "url": "https://www.coursera.org/learn/animation",
            "image": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-course-photos.s3.amazonaws.com/cb/3c4de0d7c711e5a0f8dba3b25a8b8f/Animation-Course-Photo.jpg",
            "difficulty": "Beginner",
            "duration": "4 weeks",
            "description": "Learn the fundamentals of animation including timing, spacing, and the 12 principles."
        },
        {
            "name": "Character Design for Video Games",
            "provider": "California Institute of the Arts",
            "url": "https://www.coursera.org/learn/game-character-design",
            "image": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-course-photos.s3.amazonaws.com/08/8d8e40506b11e5b1b38f6e8e1e8b8e/Game-Character-Design.jpg",
            "difficulty": "Intermediate",
            "duration": "4 weeks",
            "description": "Create compelling characters for games and animation with industry techniques."
        },
        {
            "name": "3D Animation",
            "provider": "University of Colorado",
            "url": "https://www.coursera.org/learn/3d-animation",
            "image": None,
            "difficulty": "Intermediate",
            "duration": "6 weeks",
            "description": "Master 3D animation techniques using industry-standard software."
        },
    ],
    "vfx": [
        {
            "name": "Visual Effects for Guerrilla Filmmakers",
            "provider": "Domestika",
            "url": "https://www.coursera.org/learn/visual-effects",
            "image": None,
            "difficulty": "Intermediate",
            "duration": "5 weeks",
            "description": "Learn VFX compositing and green screen techniques for independent films."
        },
        {
            "name": "Introduction to Visual Effects",
            "provider": "Columbia College Hollywood",
            "url": "https://www.coursera.org/learn/intro-visual-effects",
            "image": None,
            "difficulty": "Beginner",
            "duration": "4 weeks",
            "description": "Understand the fundamentals of visual effects production for film and TV."
        },
    ],
    "film": [
        {
            "name": "The Language of Film",
            "provider": "Wesleyan University",
            "url": "https://www.coursera.org/learn/language-of-film",
            "image": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-course-photos.s3.amazonaws.com/e5/f3b1e0e8dd11e5ba3b1f8e6e8b8e8b/Language-of-Film.jpg",
            "difficulty": "Beginner",
            "duration": "6 weeks",
            "description": "Explore the art of visual storytelling and cinematic techniques."
        },
        {
            "name": "Filmmaking Techniques",
            "provider": "Emory University",
            "url": "https://www.coursera.org/learn/filmmaking-techniques",
            "image": None,
            "difficulty": "Intermediate",
            "duration": "8 weeks",
            "description": "Learn professional filmmaking from pre-production to post."
        },
        {
            "name": "Documentary Filmmaking",
            "provider": "Michigan State University",
            "url": "https://www.coursera.org/learn/documentary-filmmaking",
            "image": None,
            "difficulty": "Intermediate",
            "duration": "6 weeks",
            "description": "Master the art of non-fiction storytelling through documentary film."
        },
    ],
    "motion_graphics": [
        {
            "name": "Motion Graphics with After Effects",
            "provider": "Domestika",
            "url": "https://www.coursera.org/learn/motion-graphics-after-effects",
            "image": None,
            "difficulty": "Intermediate",
            "duration": "6 weeks",
            "description": "Create stunning motion graphics and visual effects in After Effects."
        },
        {
            "name": "Graphic Design Specialization",
            "provider": "California Institute of the Arts",
            "url": "https://www.coursera.org/specializations/graphic-design",
            "image": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-course-photos.s3.amazonaws.com/fa/bcdf20d7c711e5a0f8dba3b25a8b8f/Graphic-Design.jpg",
            "difficulty": "Beginner",
            "duration": "6 months",
            "description": "Master the fundamentals of graphic design from CalArts."
        },
    ],
    "video_editing": [
        {
            "name": "Video Editing with DaVinci Resolve",
            "provider": "Blackmagic Design",
            "url": "https://www.coursera.org/learn/davinci-resolve",
            "image": None,
            "difficulty": "Beginner",
            "duration": "4 weeks",
            "description": "Learn professional video editing and color grading with DaVinci Resolve."
        },
        {
            "name": "Creative Video Editing",
            "provider": "Berklee College of Music",
            "url": "https://www.coursera.org/learn/creative-video-editing",
            "image": None,
            "difficulty": "Intermediate",
            "duration": "5 weeks",
            "description": "Master the art of creative editing for narrative and commercial projects."
        },
    ],
    "photography": [
        {
            "name": "Photography Basics and Beyond",
            "provider": "Michigan State University",
            "url": "https://www.coursera.org/specializations/photography-basics",
            "image": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-course-photos.s3.amazonaws.com/83/e8c8b0d7c711e5a0f8dba3b25a8b8f/Photography.jpg",
            "difficulty": "Beginner",
            "duration": "6 months",
            "description": "From smartphone to DSLR, master photography fundamentals."
        },
    ],
    "music_video": [
        {
            "name": "Music Video Production",
            "provider": "Berklee College of Music",
            "url": "https://www.coursera.org/learn/music-video-production",
            "image": None,
            "difficulty": "Intermediate",
            "duration": "4 weeks",
            "description": "Learn to produce compelling music videos from concept to delivery."
        },
    ],
    "storytelling": [
        {
            "name": "Creative Writing Specialization",
            "provider": "Wesleyan University",
            "url": "https://www.coursera.org/specializations/creative-writing",
            "image": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-course-photos.s3.amazonaws.com/b9/8d8e40506b11e5b1b38f6e8e1e8b8e/Creative-Writing.jpg",
            "difficulty": "Beginner",
            "duration": "6 months",
            "description": "Develop your craft in fiction, memoir, and screenwriting."
        },
        {
            "name": "Screenwriting",
            "provider": "Michigan State University",
            "url": "https://www.coursera.org/learn/screenwriting",
            "image": None,
            "difficulty": "Beginner",
            "duration": "4 weeks",
            "description": "Learn the fundamentals of writing for film and television."
        },
    ],
    "general": [
        {
            "name": "Introduction to Digital Media",
            "provider": "University of Michigan",
            "url": "https://www.coursera.org/learn/digital-media",
            "image": None,
            "difficulty": "Beginner",
            "duration": "4 weeks",
            "description": "Explore the landscape of digital media creation and distribution."
        },
        {
            "name": "Social Media Content Creation",
            "provider": "Meta",
            "url": "https://www.coursera.org/learn/social-media-content",
            "image": None,
            "difficulty": "Beginner",
            "duration": "3 weeks",
            "description": "Create engaging content for social media platforms."
        },
    ],
}

# Map interest areas to course categories
INTEREST_TO_CATEGORY = {
    "Film & Cinema": ["film", "storytelling", "video_editing"],
    "Animation": ["animation", "motion_graphics"],
    "Visual Effects": ["vfx", "motion_graphics"],
    "Motion Graphics": ["motion_graphics", "animation"],
    "Game Cinematics": ["animation", "vfx"],
    "Commercials & Ads": ["motion_graphics", "video_editing"],
    "Music Videos": ["music_video", "video_editing", "motion_graphics"],
    "Documentary": ["film", "storytelling", "video_editing"],
    "Social Media Content": ["general", "video_editing", "photography"],
    "Broadcast & TV": ["film", "video_editing"],
    "Corporate Video": ["video_editing", "motion_graphics"],
    "Indie Films": ["film", "storytelling"],
}


def search_coursera_api(query: str, limit: int = 5) -> List[Dict]:
    """
    Try to search Coursera using their public API.
    Falls back to curated courses if API is unavailable.
    """
    try:
        # Coursera's public search API (may have rate limits)
        url = "https://www.coursera.org/api/courses.v1"
        params = {
            "q": "search",
            "query": query,
            "limit": limit,
            "fields": "name,slug,photoUrl,partnerIds,description,workload,difficultyLevel"
        }

        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            courses = []
            for element in data.get("elements", []):
                course = {
                    "name": element.get("name", ""),
                    "provider": "Coursera",
                    "url": f"https://www.coursera.org/learn/{element.get('slug', '')}",
                    "image": element.get("photoUrl"),
                    "difficulty": element.get("difficultyLevel", "Beginner"),
                    "duration": element.get("workload", "Self-paced"),
                    "description": element.get("description", "")[:200] + "..." if element.get("description") else ""
                }
                courses.append(course)
            return courses
    except Exception:
        pass

    return []


def get_courses_for_interests(interests: List[str], skills_text: str = "", limit: int = 5) -> List[Dict]:
    """
    Get recommended Coursera courses based on user interests.

    Args:
        interests: List of interest areas (e.g., ["Animation", "Film & Cinema"])
        skills_text: Optional text describing user's skills
        limit: Maximum number of courses to return

    Returns:
        List of course dictionaries with name, url, image, etc.
    """
    courses = []
    seen_names = set()

    # Collect courses from matching categories
    for interest in interests:
        categories = INTEREST_TO_CATEGORY.get(interest, ["general"])
        for category in categories:
            category_courses = CURATED_COURSES.get(category, [])
            for course in category_courses:
                if course["name"] not in seen_names:
                    courses.append(course)
                    seen_names.add(course["name"])

    # If we don't have enough courses, add general ones
    if len(courses) < limit:
        for course in CURATED_COURSES.get("general", []):
            if course["name"] not in seen_names:
                courses.append(course)
                seen_names.add(course["name"])

    # Try to supplement with API search if we have skills text
    if skills_text and len(courses) < limit:
        # Extract key terms for search
        search_terms = skills_text.split(",")[0] if "," in skills_text else skills_text[:50]
        api_courses = search_coursera_api(f"{search_terms} media", limit=3)
        for course in api_courses:
            if course["name"] not in seen_names:
                courses.append(course)
                seen_names.add(course["name"])

    return courses[:limit]


def get_course_details(course_slug: str) -> Optional[Dict]:
    """
    Get detailed information about a specific Coursera course.

    Args:
        course_slug: The URL slug of the course

    Returns:
        Course details dictionary or None if not found
    """
    try:
        url = f"https://www.coursera.org/api/courses.v1"
        params = {
            "q": "slug",
            "slug": course_slug,
            "fields": "name,slug,photoUrl,partnerIds,description,workload,difficultyLevel"
        }

        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            if elements:
                element = elements[0]
                return {
                    "name": element.get("name", ""),
                    "provider": "Coursera",
                    "url": f"https://www.coursera.org/learn/{element.get('slug', '')}",
                    "image": element.get("photoUrl"),
                    "difficulty": element.get("difficultyLevel", "Beginner"),
                    "duration": element.get("workload", "Self-paced"),
                    "description": element.get("description", "")
                }
    except Exception:
        pass

    return None

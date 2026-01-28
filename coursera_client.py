# Coursera integration for Better Youth Creative Lab
# Web scraper to fetch real courses from Coursera search results

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
import re

# Headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Map interest areas to search queries
INTEREST_TO_SEARCH = {
    "Film & Cinema": "filmmaking cinematography",
    "Animation": "animation 2d 3d",
    "Visual Effects": "visual effects vfx compositing",
    "Motion Graphics": "motion graphics after effects",
    "Game Cinematics": "game design animation",
    "Commercials & Ads": "video production advertising",
    "Music Videos": "music video production",
    "Documentary": "documentary filmmaking",
    "Social Media Content": "social media video content creation",
    "Broadcast & TV": "broadcast television production",
    "Corporate Video": "corporate video production",
    "Indie Films": "independent filmmaking screenwriting",
}

# Fallback curated courses in case scraping fails
FALLBACK_COURSES = [
    {
        "name": "Fundamentals of Graphic Design",
        "provider": "California Institute of the Arts",
        "url": "https://www.coursera.org/learn/fundamentals-of-graphic-design",
        "image": None,
        "difficulty": "Beginner",
        "duration": "4 weeks",
        "description": "Learn the fundamental skills of graphic design."
    },
    {
        "name": "Introduction to User Experience Design",
        "provider": "Georgia Institute of Technology",
        "url": "https://www.coursera.org/learn/user-experience-design",
        "image": None,
        "difficulty": "Beginner",
        "duration": "4 weeks",
        "description": "Learn the fundamentals of user experience design."
    },
    {
        "name": "Creative Writing Specialization",
        "provider": "Wesleyan University",
        "url": "https://www.coursera.org/specializations/creative-writing",
        "image": None,
        "difficulty": "Beginner",
        "duration": "6 months",
        "description": "Develop your craft in creative writing."
    },
    {
        "name": "Photography Basics",
        "provider": "Michigan State University",
        "url": "https://www.coursera.org/specializations/photography-basics",
        "image": None,
        "difficulty": "Beginner",
        "duration": "6 months",
        "description": "Learn photography fundamentals."
    },
    {
        "name": "Social Media Marketing",
        "provider": "Northwestern University",
        "url": "https://www.coursera.org/specializations/social-media-marketing",
        "image": None,
        "difficulty": "Beginner",
        "duration": "5 months",
        "description": "Master social media marketing."
    },
]


def scrape_coursera_search(query: str, limit: int = 10) -> List[Dict]:
    """
    Scrape Coursera search results for courses.

    Args:
        query: Search query string
        limit: Maximum number of courses to return

    Returns:
        List of course dictionaries
    """
    courses = []

    try:
        # Coursera search URL
        search_url = f"https://www.coursera.org/search?query={requests.utils.quote(query)}&index=prod_all_launched_products_term_optimization"

        response = requests.get(search_url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"Coursera search returned status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find course data in the page's JSON data
        # Coursera often embeds course data in script tags
        scripts = soup.find_all('script', type='application/json')

        for script in scripts:
            try:
                data = json.loads(script.string)
                # Look for course data in various possible structures
                courses_data = extract_courses_from_json(data, limit)
                if courses_data:
                    return courses_data
            except (json.JSONDecodeError, TypeError):
                continue

        # Alternative: Try to parse the HTML directly
        # Look for course cards
        course_cards = soup.find_all('div', class_=re.compile(r'card|result|course', re.I))

        for card in course_cards[:limit]:
            course = extract_course_from_card(card)
            if course and course.get('name') and course.get('url'):
                courses.append(course)

        # If HTML parsing didn't work, try the API endpoint
        if not courses:
            courses = try_coursera_api(query, limit)

    except requests.exceptions.RequestException as e:
        print(f"Error scraping Coursera: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return courses[:limit]


def extract_courses_from_json(data: dict, limit: int) -> List[Dict]:
    """Extract course information from Coursera's JSON data."""
    courses = []

    def search_for_courses(obj, depth=0):
        if depth > 10 or len(courses) >= limit:
            return

        if isinstance(obj, dict):
            # Check if this looks like a course object
            if 'name' in obj and ('slug' in obj or 'url' in obj):
                course = {
                    'name': obj.get('name', ''),
                    'provider': obj.get('partnerName', obj.get('partners', [{}])[0].get('name', 'Coursera') if isinstance(obj.get('partners'), list) else 'Coursera'),
                    'url': f"https://www.coursera.org/learn/{obj.get('slug', '')}" if obj.get('slug') else obj.get('url', ''),
                    'image': obj.get('imageUrl', obj.get('photoUrl', obj.get('image', None))),
                    'difficulty': obj.get('difficultyLevel', obj.get('level', 'Beginner')),
                    'duration': obj.get('workload', obj.get('duration', 'Self-paced')),
                    'description': (obj.get('description', '') or '')[:200],
                }
                if course['name'] and course['url']:
                    courses.append(course)

            # Recursively search
            for key, value in obj.items():
                search_for_courses(value, depth + 1)

        elif isinstance(obj, list):
            for item in obj:
                search_for_courses(item, depth + 1)

    search_for_courses(data)
    return courses


def extract_course_from_card(card) -> Dict:
    """Extract course information from an HTML card element."""
    course = {}

    try:
        # Try to find the course link and name
        link = card.find('a', href=re.compile(r'/learn/|/specializations/|/professional-certificates/'))
        if link:
            course['url'] = 'https://www.coursera.org' + link.get('href', '') if link.get('href', '').startswith('/') else link.get('href', '')
            course['name'] = link.get_text(strip=True) or link.get('aria-label', '')

        # Try to find the image
        img = card.find('img')
        if img:
            course['image'] = img.get('src') or img.get('data-src')

        # Try to find the provider
        provider_elem = card.find(string=re.compile(r'University|Institute|College|School', re.I))
        if provider_elem:
            course['provider'] = provider_elem.strip()
        else:
            course['provider'] = 'Coursera'

        # Try to find difficulty and duration
        course['difficulty'] = 'Beginner'
        course['duration'] = 'Self-paced'

        # Try to find description
        desc = card.find('p') or card.find('span', class_=re.compile(r'desc|summary', re.I))
        if desc:
            course['description'] = desc.get_text(strip=True)[:200]
        else:
            course['description'] = ''

    except Exception:
        pass

    return course


def try_coursera_api(query: str, limit: int) -> List[Dict]:
    """Try to fetch courses from Coursera's internal API."""
    courses = []

    try:
        # Coursera's internal search API
        api_url = "https://www.coursera.org/api/search/v1"
        params = {
            'q': query,
            'limit': limit,
            'start': 0,
            'entityTypeFilters': 'Courses,Specializations'
        }

        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()

            for element in data.get('elements', []):
                course = {
                    'name': element.get('name', ''),
                    'provider': element.get('partnerName', 'Coursera'),
                    'url': f"https://www.coursera.org/learn/{element.get('slug', '')}",
                    'image': element.get('imageUrl'),
                    'difficulty': element.get('difficultyLevel', 'Beginner'),
                    'duration': element.get('workload', 'Self-paced'),
                    'description': (element.get('description', '') or '')[:200],
                }
                if course['name']:
                    courses.append(course)

    except Exception:
        pass

    return courses


def get_courses_for_interests(interests: List[str], skills_text: str = "", limit: int = 10) -> List[Dict]:
    """
    Get courses from Coursera based on user interests.
    Scrapes Coursera search results and returns up to `limit` courses.

    Args:
        interests: List of interest areas
        skills_text: Optional text describing user's skills (used for search refinement)
        limit: Maximum number of courses to return (default 10 for model selection)

    Returns:
        List of course dictionaries
    """
    all_courses = []
    seen_urls = set()

    # Build search queries from interests
    search_queries = []
    for interest in interests:
        query = INTEREST_TO_SEARCH.get(interest, interest.lower())
        search_queries.append(query)

    # Add skills to search if provided
    if skills_text:
        # Extract key terms
        skills_terms = skills_text.replace('|', ' ').replace(',', ' ')[:100]
        search_queries.append(skills_terms)

    # If no interests, use a default query
    if not search_queries:
        search_queries = ["video production media creative"]

    # Search for each query
    for query in search_queries[:3]:  # Limit to 3 queries to avoid too many requests
        courses = scrape_coursera_search(query, limit=10)

        for course in courses:
            url = course.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_courses.append(course)

    # If scraping failed or returned too few results, use fallback
    if len(all_courses) < 3:
        print("Scraping returned few results, using fallback courses")
        for course in FALLBACK_COURSES:
            if course['url'] not in seen_urls:
                all_courses.append(course)
                seen_urls.add(course['url'])

    return all_courses[:limit]


def format_courses_for_model(courses: List[Dict]) -> str:
    """
    Format courses as a string for the AI model to select from.

    Args:
        courses: List of course dictionaries

    Returns:
        Formatted string describing all courses
    """
    if not courses:
        return "No courses found."

    formatted = "Available courses from Coursera:\n\n"

    for i, course in enumerate(courses, 1):
        formatted += f"{i}. **{course.get('name', 'Unknown')}**\n"
        formatted += f"   Provider: {course.get('provider', 'Coursera')}\n"
        formatted += f"   Level: {course.get('difficulty', 'Beginner')}\n"
        formatted += f"   Duration: {course.get('duration', 'Self-paced')}\n"
        formatted += f"   URL: {course.get('url', '')}\n"
        if course.get('description'):
            formatted += f"   Description: {course.get('description')}\n"
        formatted += "\n"

    return formatted

# Databricks RAG integration for Better Youth Creative Lab

import os
import json
import requests
from typing import Optional, List, Dict
import streamlit as st
from coursera_client import get_courses_for_interests, format_courses_for_model

# =============================================================================
# DATABRICKS CONFIGURATION
# These values are loaded from environment variables when deployed in Databricks
# For local development, set these environment variables or update the defaults
# =============================================================================
DATABRICKS_WORKSPACE_URL = os.environ.get("DATABRICKS_HOST", "")  # e.g., https://xxx.cloud.databricks.com
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
DATABRICKS_ENDPOINT_NAME = os.environ.get("DATABRICKS_SERVING_ENDPOINT", "")  # Your model serving endpoint name


class DatabricksClient:
    """Client for interacting with Databricks Model Serving endpoints."""

    def __init__(self):
        """
        Initialize the Databricks client using environment variables.
        When deployed in Databricks, these are automatically available.
        """
        self.workspace_url = DATABRICKS_WORKSPACE_URL.rstrip("/")
        self.token = DATABRICKS_TOKEN
        self.endpoint_name = DATABRICKS_ENDPOINT_NAME

    def is_configured(self) -> bool:
        """Check if the client is properly configured."""
        return bool(self.workspace_url and self.token and self.endpoint_name)

    def _build_prompt(self, user_profile: dict, available_courses: str = "") -> str:
        """
        Build a prompt for the RAG model based on user profile and available courses.

        Args:
            user_profile: Dictionary containing user skills, experience, and goals
            available_courses: Formatted string of courses scraped from Coursera

        Returns:
            Formatted prompt string
        """
        skills_text = user_profile.get("skills_text", ", ".join(user_profile.get("skills", [])))
        interests_text = ", ".join(user_profile.get("interests", []))
        experience_level = user_profile.get("experience_level", "Intermediate")
        goals = user_profile.get("goals", "")
        project_interests = user_profile.get("project_interests", "")

        prompt = f"""Based on the following creative professional's profile, select the most suitable courses and provide mentor recommendations:

**User Profile:**
- Interest Areas: {interests_text}
- Current Skills: {skills_text}
- Experience Level: {experience_level}
- Career Goals: {goals}
- What they want to create: {project_interests}

**Available Courses from Coursera:**
{available_courses}

**Your Task:**
1. **Select the TOP 5 most suitable courses** from the available courses above that best match this user's profile, interests, and goals. For each selected course, explain WHY it's a good fit for this user.

2. **Recommend 3 Mentor profiles** (you can create fictional but realistic mentor profiles) that would be ideal matches for this user. Include:
   - Name and title
   - Areas of expertise
   - Years of experience
   - Why they're a good match

3. **Create a Learning Path** with 5 steps tailored to help this user achieve their creative goals.

Format your response clearly with sections for Courses, Mentors, and Learning Path."""

        return prompt

    def get_recommendations(self, user_profile: dict) -> dict:
        """
        Get course and mentor recommendations from Databricks RAG model.
        First scrapes Coursera for relevant courses, then asks the model to select the best ones.

        Args:
            user_profile: Dictionary containing user skills, experience, and goals

        Returns:
            Dictionary with recommendations or error information
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Databricks client not configured. Please provide workspace URL, token, and endpoint name.",
                "recommendations": None
            }

        # Scrape Coursera for relevant courses based on user interests
        interests = user_profile.get("interests", [])
        skills_text = user_profile.get("skills_text", "")
        scraped_courses = get_courses_for_interests(interests, skills_text, limit=10)

        # Format courses for the model
        courses_text = format_courses_for_model(scraped_courses)

        # Store scraped courses for later use in rendering
        self._scraped_courses = scraped_courses

        prompt = self._build_prompt(user_profile, courses_text)

        # Build the API URL
        api_url = f"{self.workspace_url}/serving-endpoints/{self.endpoint_name}/invocations"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # Payload format for Databricks Model Serving
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                # Extract the response content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    return {
                        "success": True,
                        "error": None,
                        "recommendations": content,
                        "scraped_courses": scraped_courses,
                        "raw_response": result
                    }
                else:
                    return {
                        "success": True,
                        "error": None,
                        "recommendations": str(result),
                        "scraped_courses": scraped_courses,
                        "raw_response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}",
                    "recommendations": None
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "recommendations": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "recommendations": None
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "recommendations": None
            }

    def get_youtube_recommendations(self, user_profile: dict) -> dict:
        """
        Get YouTube video recommendations from Databricks vector database.

        Args:
            user_profile: Dictionary containing user skills, experience, and goals

        Returns:
            Dictionary with YouTube video recommendations or error information
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Databricks client not configured.",
                "videos": None
            }

        # Build query from user profile
        interests = user_profile.get("interests", [])
        skills_text = user_profile.get("skills_text", "")
        query = " ".join(interests) + " " + skills_text

        # Build the API URL for vector search endpoint
        # Adjust endpoint name as needed for your YouTube vector database
        youtube_endpoint = os.environ.get("DATABRICKS_YOUTUBE_ENDPOINT", self.endpoint_name)
        api_url = f"{self.workspace_url}/serving-endpoints/{youtube_endpoint}/invocations"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # Payload for vector search - adjust based on your endpoint configuration
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Find the top 5 YouTube tutorial videos for someone interested in: {query}. Return video title, channel name, URL, and brief description for each."
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.5
        }

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    return {
                        "success": True,
                        "error": None,
                        "videos": content,
                        "raw_response": result
                    }
                else:
                    return {
                        "success": True,
                        "error": None,
                        "videos": str(result),
                        "raw_response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}",
                    "videos": None
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "videos": None
            }


def get_mock_youtube_videos(user_profile: dict) -> list:
    """
    Generate mock YouTube video recommendations based on user profile.

    Args:
        user_profile: Dictionary containing user skills, experience, and goals

    Returns:
        List of YouTube video dictionaries
    """
    interests = user_profile.get("interests", [])
    skills_text = user_profile.get("skills_text", "")

    # Sample YouTube videos mapped to interests
    all_videos = [
        {
            "title": "After Effects Tutorial: Complete Motion Graphics Course",
            "channel": "Ben Marriott",
            "url": "https://www.youtube.com/watch?v=motion-graphics-101",
            "duration": "2:45:30",
            "views": "1.2M views",
            "description": "Learn motion graphics from scratch with practical projects and techniques.",
            "tags": ["Motion Graphics", "After Effects", "Animation"]
        },
        {
            "title": "Cinematography Masterclass - Camera Movement & Composition",
            "channel": "StudioBinder",
            "url": "https://www.youtube.com/watch?v=cinematography-101",
            "duration": "58:20",
            "views": "890K views",
            "description": "Master the art of cinematography with professional camera techniques.",
            "tags": ["Film & Cinema", "Cinematography", "Documentary"]
        },
        {
            "title": "Complete Blender 3D Animation Course for Beginners",
            "channel": "Blender Guru",
            "url": "https://www.youtube.com/watch?v=blender-animation",
            "duration": "3:12:45",
            "views": "2.1M views",
            "description": "Learn 3D animation in Blender from absolute beginner to intermediate.",
            "tags": ["Animation", "3D Animation", "Blender"]
        },
        {
            "title": "VFX Compositing in Nuke - Beginner to Pro",
            "channel": "ActionVFX",
            "url": "https://www.youtube.com/watch?v=nuke-compositing",
            "duration": "1:45:00",
            "views": "456K views",
            "description": "Professional VFX compositing techniques used in Hollywood films.",
            "tags": ["Visual Effects", "Compositing", "VFX"]
        },
        {
            "title": "DaVinci Resolve Color Grading - Complete Tutorial",
            "channel": "Casey Faris",
            "url": "https://www.youtube.com/watch?v=davinci-color",
            "duration": "1:23:15",
            "views": "1.5M views",
            "description": "Master color grading and color correction in DaVinci Resolve.",
            "tags": ["Film & Cinema", "Color Grading", "Video Editing"]
        },
        {
            "title": "YouTube Video Editing Tips for Content Creators",
            "channel": "Peter McKinnon",
            "url": "https://www.youtube.com/watch?v=youtube-editing",
            "duration": "18:42",
            "views": "3.2M views",
            "description": "Pro tips for editing engaging social media and YouTube content.",
            "tags": ["Social Media Content", "Video Editing", "Content Creation"]
        },
        {
            "title": "Character Animation Principles - 12 Principles Explained",
            "channel": "Animator Island",
            "url": "https://www.youtube.com/watch?v=12-principles",
            "duration": "45:30",
            "views": "780K views",
            "description": "Deep dive into the 12 principles of animation with examples.",
            "tags": ["Animation", "Character Animation", "2D Animation"]
        },
        {
            "title": "Music Video Production - Behind the Scenes",
            "channel": "Film Riot",
            "url": "https://www.youtube.com/watch?v=music-video-bts",
            "duration": "22:15",
            "views": "560K views",
            "description": "Learn how to produce professional music videos on any budget.",
            "tags": ["Music Videos", "Film & Cinema", "Video Production"]
        },
        {
            "title": "Game Cinematics - Creating Cutscenes in Unreal Engine",
            "channel": "Unreal Sensei",
            "url": "https://www.youtube.com/watch?v=game-cinematics",
            "duration": "1:10:00",
            "views": "340K views",
            "description": "Create stunning game cinematics using Unreal Engine's Sequencer.",
            "tags": ["Game Cinematics", "Animation", "3D Animation"]
        },
        {
            "title": "Documentary Filmmaking - Storytelling Techniques",
            "channel": "D4Darious",
            "url": "https://www.youtube.com/watch?v=documentary-tips",
            "duration": "28:45",
            "views": "420K views",
            "description": "Essential storytelling and interview techniques for documentaries.",
            "tags": ["Documentary", "Film & Cinema", "Storytelling"]
        },
    ]

    # Score videos based on user interests
    scored_videos = []
    for video in all_videos:
        score = 0
        for interest in interests:
            if interest in video["tags"]:
                score += 3
            if interest.lower() in video["title"].lower():
                score += 2
            if interest.lower() in video["description"].lower():
                score += 1
        # Also check skills
        for tag in video["tags"]:
            if tag.lower() in skills_text.lower():
                score += 2
        scored_videos.append((score, video))

    # Sort by score and return top 5
    scored_videos.sort(key=lambda x: x[0], reverse=True)
    return [video for _, video in scored_videos[:5]]


def get_mock_recommendations(user_profile: dict) -> dict:
    """
    Generate mock recommendations for testing without Databricks connection.

    Args:
        user_profile: Dictionary containing user skills, experience, and goals

    Returns:
        Dictionary with mock recommendations
    """
    skills = user_profile.get("skills", [])
    interests = user_profile.get("interests", [])
    experience = user_profile.get("experience_level", "Intermediate")

    # Generate contextual mock data based on user interests and skills
    courses = []
    mentors = []

    # Animation focused
    if any(i in interests for i in ["Animation", "Game Cinematics"]) or \
       any(s in skills for s in ["2D Animation", "3D Animation", "Character Animation", "Rigging"]):
        courses.extend([
            {
                "name": "Character Animation Masterclass",
                "description": "Learn the 12 principles of animation and bring characters to life with emotion and personality.",
                "difficulty": "Intermediate",
                "duration": "10 weeks",
                "relevance": "Perfect for developing your animation skills"
            },
            {
                "name": "3D Animation Pipeline for Film",
                "description": "Master the complete 3D animation workflow from pre-vis to final render.",
                "difficulty": "Advanced",
                "duration": "12 weeks",
                "relevance": "Industry-standard techniques used at major studios"
            }
        ])
        mentors.append({
            "name": "Maya Rodriguez",
            "title": "Lead Animator at Pixar",
            "expertise": ["Character Animation", "3D Animation", "Storyboarding"],
            "experience": "15 years",
            "match_reason": "Expert animator with feature film credits"
        })

    # VFX focused
    if any(i in interests for i in ["Visual Effects", "Film & Cinema"]) or \
       any(s in skills for s in ["Compositing", "VFX", "Nuke", "Rotoscoping"]):
        courses.extend([
            {
                "name": "Visual Effects Compositing with Nuke",
                "description": "Master node-based compositing for film and TV visual effects.",
                "difficulty": "Advanced",
                "duration": "8 weeks",
                "relevance": "Industry-standard VFX compositing skills"
            },
            {
                "name": "Practical VFX: Set Extensions & Environments",
                "description": "Create believable digital environments and seamless set extensions.",
                "difficulty": "Intermediate",
                "duration": "6 weeks",
                "relevance": "Essential skills for modern VFX work"
            }
        ])
        mentors.append({
            "name": "James Chen",
            "title": "VFX Supervisor at ILM",
            "expertise": ["Compositing", "VFX Supervision", "Nuke"],
            "experience": "18 years",
            "match_reason": "Worked on major blockbuster films"
        })

    # Motion Graphics focused
    if any(i in interests for i in ["Motion Graphics", "Commercials & Ads", "Social Media Content"]) or \
       any(s in skills for s in ["Motion Graphics", "After Effects", "Cinema 4D"]):
        courses.extend([
            {
                "name": "Motion Design for Brands",
                "description": "Create stunning motion graphics for commercials, social media, and brand content.",
                "difficulty": "Intermediate",
                "duration": "6 weeks",
                "relevance": "High-demand skills for commercial work"
            },
            {
                "name": "Cinema 4D for Motion Designers",
                "description": "Add 3D elements to your motion graphics toolkit with Cinema 4D.",
                "difficulty": "Intermediate",
                "duration": "8 weeks",
                "relevance": "Expand your capabilities into 3D motion"
            }
        ])
        mentors.append({
            "name": "Sarah Kim",
            "title": "Creative Director at Buck",
            "expertise": ["Motion Graphics", "After Effects", "Brand Design"],
            "experience": "12 years",
            "match_reason": "Award-winning motion designer"
        })

    # Film & Video Production focused
    if any(i in interests for i in ["Film & Cinema", "Documentary", "Music Videos", "Indie Films"]) or \
       any(s in skills for s in ["Cinematography", "Video Editing", "Directing", "Color Grading"]):
        courses.extend([
            {
                "name": "Cinematic Storytelling & Directing",
                "description": "Learn visual storytelling, shot composition, and directing techniques from industry pros.",
                "difficulty": "Intermediate",
                "duration": "10 weeks",
                "relevance": "Essential for aspiring filmmakers"
            },
            {
                "name": "Professional Color Grading with DaVinci Resolve",
                "description": "Master the art of color grading to give your films a professional cinematic look.",
                "difficulty": "Intermediate",
                "duration": "6 weeks",
                "relevance": "Transform your footage with professional color"
            }
        ])
        mentors.append({
            "name": "David Okonkwo",
            "title": "Independent Filmmaker",
            "expertise": ["Directing", "Cinematography", "Documentary"],
            "experience": "14 years",
            "match_reason": "Sundance award-winning director"
        })

    # Broadcast & TV focused
    if any(i in interests for i in ["Broadcast & TV", "Corporate Video"]):
        courses.extend([
            {
                "name": "Broadcast Graphics & Lower Thirds",
                "description": "Create professional broadcast graphics, lower thirds, and news packages.",
                "difficulty": "Intermediate",
                "duration": "4 weeks",
                "relevance": "Skills for broadcast and corporate video"
            }
        ])

    # Add general courses if few matches
    if len(courses) < 3:
        courses.extend([
            {
                "name": "Creative Portfolio Development",
                "description": "Build a standout portfolio that gets you noticed by studios and clients.",
                "difficulty": "Beginner",
                "duration": "4 weeks",
                "relevance": "Essential for landing your dream job"
            },
            {
                "name": "Freelance Business for Creatives",
                "description": "Learn to price your work, find clients, and build a sustainable creative business.",
                "difficulty": "Beginner",
                "duration": "3 weeks",
                "relevance": "Turn your skills into a career"
            },
            {
                "name": "Visual Storytelling Fundamentals",
                "description": "Master the art of telling compelling stories through visuals.",
                "difficulty": "Beginner",
                "duration": "6 weeks",
                "relevance": "Foundation for all visual media"
            }
        ])

    if len(mentors) < 2:
        mentors.extend([
            {
                "name": "Alex Thompson",
                "title": "Creative Director",
                "expertise": ["Creative Direction", "Portfolio Review", "Career Guidance"],
                "experience": "20 years",
                "match_reason": "Expert at helping creatives grow their careers"
            },
            {
                "name": "Lisa Park",
                "title": "Studio Owner & Producer",
                "expertise": ["Production", "Project Management", "Client Relations"],
                "experience": "16 years",
                "match_reason": "Understands both creative and business sides"
            }
        ])

    # Learning path based on experience
    if experience in ["Beginner", "Elementary"]:
        learning_path = [
            "1. Master the fundamentals of your chosen creative software",
            "2. Study the work of artists you admire and analyze their techniques",
            "3. Complete small personal projects to build your skills",
            "4. Start building your portfolio with your best work",
            "5. Connect with the creative community online and locally"
        ]
    elif experience in ["Intermediate"]:
        learning_path = [
            "1. Specialize in a specific area (VFX, animation, motion, etc.)",
            "2. Take on more challenging projects that push your skills",
            "3. Learn complementary skills to become more versatile",
            "4. Start networking with industry professionals",
            "5. Consider internships or junior positions at studios"
        ]
    else:
        learning_path = [
            "1. Develop your unique creative voice and style",
            "2. Lead projects and mentor junior artists",
            "3. Build relationships with studios and clients",
            "4. Consider teaching or creating tutorials",
            "5. Explore emerging technologies (AI, real-time, VR/AR)"
        ]

    return {
        "success": True,
        "error": None,
        "courses": courses[:5],
        "mentors": mentors[:3],
        "learning_path": learning_path,
        "is_mock": True
    }


def get_databricks_client():
    """Get a Databricks client instance using environment variables."""
    return DatabricksClient()

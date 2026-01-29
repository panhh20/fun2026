# Main Streamlit application for Better Youth Creative Lab

import streamlit as st
import os
import base64
from datetime import datetime
from config import COLORS, SKILLS_CATEGORIES, EXPERIENCE_LEVELS, APP_CONFIG, INTEREST_AREAS
from auth import is_authenticated, render_login_page, logout, get_current_user
from databricks_client import (
    DatabricksClient,
    get_mock_recommendations,
    get_databricks_client
)
from coursera_client import get_courses_for_interests

def get_coursera_image_base64():
    """Get the Coursera background image as base64 for embedding in HTML."""
    image_path = os.path.join(os.path.dirname(__file__), "assets", "coursera_bg.png")
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{data}"
    # Fallback to a simple placeholder color if image not found
    return None


def get_logo_path():
    """Get the logo path."""
    return os.path.join(os.path.dirname(__file__), "assets", "logo.png")


def apply_global_styles():
    """Apply global CSS styles to the app."""
    st.markdown(f"""
        <style>
        /* Hide Streamlit header bar */
        header[data-testid="stHeader"] {{
            display: none !important;
        }}
        #MainMenu {{
            visibility: hidden;
        }}
        footer {{
            visibility: hidden;
        }}

        .stApp {{
            background-color: {COLORS['background']};
        }}

        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {COLORS['primary_dark']};
        }}
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown {{
            color: {COLORS['white']} !important;
        }}
        /* Keep input text boxes readable */
        [data-testid="stSidebar"] input {{
            color: {COLORS['text_dark']} !important;
            background-color: {COLORS['white']} !important;
        }}
        [data-testid="stSidebar"] .stTextInput input {{
            color: {COLORS['text_dark']} !important;
            background-color: {COLORS['white']} !important;
        }}

        /* Header styling */
        .main-header {{
            background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['mid_accent']} 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: {COLORS['white']};
        }}
        .main-header h1 {{
            color: {COLORS['white']} !important;
        }}

        /* Card styling */
        .course-card {{
            background-color: {COLORS['white']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border-left: 4px solid {COLORS['primary_dark']};
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .course-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        .course-card h4 {{
            color: {COLORS['primary_dark']};
            margin-bottom: 0.5rem;
        }}
        .course-card h4 a {{
            color: {COLORS['primary_dark']};
            text-decoration: none;
        }}
        .course-card h4 a:hover {{
            text-decoration: underline;
        }}
        .course-card p {{
            color: {COLORS['text_dark']};
            margin-bottom: 0.25rem;
        }}
        .course-card-link {{
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        .course-image {{
            width: 100%;
            height: 120px;
            object-fit: cover;
            border-radius: 5px;
            margin-bottom: 0.75rem;
        }}
        .course-image-placeholder {{
            width: 100%;
            height: 120px;
            background-color: {COLORS['light_accent']};
            border-radius: 5px;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: {COLORS['secondary']};
            font-size: 2rem;
        }}
        .provider-tag {{
            display: inline-block;
            background-color: {COLORS['light_accent']};
            color: {COLORS['mid_accent']};
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-size: 0.75rem;
            margin-bottom: 0.5rem;
        }}

        .mentor-card {{
            background-color: {COLORS['white']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border-left: 4px solid {COLORS['accent']};
        }}
        .mentor-card h4 {{
            color: {COLORS['accent']};
            margin-bottom: 0.5rem;
        }}

        /* Tag styling */
        .skill-tag {{
            display: inline-block;
            background-color: {COLORS['light_accent']};
            color: {COLORS['primary_dark']};
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            margin: 0.25rem;
            font-size: 0.85rem;
        }}
        .difficulty-tag {{
            display: inline-block;
            background-color: {COLORS['secondary']};
            color: {COLORS['white']};
            padding: 0.25rem 0.5rem;
            border-radius: 5px;
            font-size: 0.8rem;
        }}

        /* Button styling */
        .stButton > button {{
            background-color: {COLORS['primary_dark']};
            color: {COLORS['white']};
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }}
        .stButton > button:hover {{
            background-color: {COLORS['mid_accent']};
        }}

        /* Section headers */
        .section-header {{
            color: {COLORS['primary_dark']};
            border-bottom: 2px solid {COLORS['accent']};
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }}

        /* Learning path */
        .learning-path {{
            background-color: {COLORS['light_accent']};
            padding: 1.5rem;
            border-radius: 10px;
            margin-top: 1rem;
        }}
        .learning-path ol {{
            color: {COLORS['text_dark']};
        }}

        /* Info box */
        .info-box {{
            background-color: {COLORS['light_accent']};
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}

        /* Interest bubbles */
        .bubble-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            padding: 1rem 0;
        }}
        .interest-bubble {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.25rem;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95rem;
            font-weight: 500;
            border: 2px solid {COLORS['secondary']};
            background-color: {COLORS['white']};
            color: {COLORS['primary_dark']};
        }}
        .interest-bubble:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(62, 79, 40, 0.2);
        }}
        .interest-bubble.selected {{
            background-color: {COLORS['primary_dark']};
            color: {COLORS['white']};
            border-color: {COLORS['primary_dark']};
        }}

        /* Sidebar button styling */
        [data-testid="stSidebar"] .stButton button {{
            font-size: 0.85rem !important;
        }}

        /* Profile page styles */
        .profile-avatar {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background-color: {COLORS['secondary']};
            margin: 0 auto 0.5rem auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: {COLORS['white']};
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .profile-avatar:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        .course-tracker-card {{
            background-color: {COLORS['white']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border-left: 4px solid {COLORS['primary_dark']};
        }}
        .course-tracker-card.completed {{
            border-left-color: #28a745;
        }}
        .course-tracker-card.in-progress {{
            border-left-color: {COLORS['accent']};
        }}
        .course-status-tag {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .status-completed {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status-in-progress {{
            background-color: {COLORS['light_accent']};
            color: {COLORS['mid_accent']};
        }}
        .certificate-upload {{
            background-color: {COLORS['light_accent']};
            padding: 1rem;
            border-radius: 5px;
            margin-top: 0.5rem;
        }}
        .stats-card {{
            background-color: {COLORS['white']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .stats-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: {COLORS['primary_dark']};
        }}
        .stats-label {{
            color: {COLORS['secondary']};
            font-size: 0.9rem;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with user info and logout."""
    init_course_tracking()
    logo_path = get_logo_path()

    with st.sidebar:
        # Show logo if it exists
        if os.path.exists(logo_path):
            st.image(logo_path, use_column_width=True)
        else:
            st.markdown(f"""
                <h2 style='color: {COLORS["white"]}; text-align: center;'>
                    Better Youth
                </h2>
                <p style='color: {COLORS["light_accent"]}; text-align: center; font-size: 0.9rem;'>
                    Creative Lab
                </p>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # User profile picture placeholder and info - clickable
        username = get_current_user()
        tracked_count = len(st.session_state.get('tracked_courses', {}))
        completed_count = len(st.session_state.get('completed_courses', {}))
        initial = username[0].upper() if username else 'U'

        # Centered profile avatar (clickable)
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <div id="profile-avatar" style='
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    background-color: {COLORS["secondary"]};
                    margin: 0 auto 0.75rem auto;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 3rem;
                    color: {COLORS["white"]};
                    cursor: pointer;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                '>
                    {initial}
                </div>
                <p style='color: {COLORS["light_accent"]}; margin: 0; text-align: center;'>
                    Logged in as: <strong>{username}</strong>
                </p>
                <p style='color: {COLORS["light_accent"]}; margin: 0.5rem 0 0 0; text-align: center; font-size: 0.8rem;'>
                    {tracked_count} in progress | {completed_count} completed
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Profile button (small, below the avatar info)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("View Profile", key="profile_btn", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()

        # Spacer to push logout to bottom
        st.markdown("<div style='flex-grow: 1; min-height: 100px;'></div>", unsafe_allow_html=True)

        # Logout button - smaller, at bottom
        st.markdown(f"""
            <style>
            [data-testid="stSidebar"] > div:first-child {{
                display: flex;
                flex-direction: column;
                height: 100vh;
            }}
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Logout", key="logout_btn", use_container_width=True):
                logout()
                st.rerun()


def render_skills_form():
    """Render the skills and interests questionnaire form."""
    st.markdown("""
        <div class="main-header">
            <h1>Better Youth Creative Lab</h1>
            <p>Tell us about your interests and skills in media, animation, and film - we'll recommend the perfect courses and mentors for you.</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize form data in session state
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    if 'selected_interests' not in st.session_state:
        st.session_state.selected_interests = []

    # Section 1: Interest Areas (Bubbles)
    st.markdown("<h3 class='section-header'>What areas interest you?</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #556443;'>Click to select your areas of interest</p>", unsafe_allow_html=True)

    # Create columns for interest bubbles
    cols = st.columns(4)
    for idx, interest in enumerate(INTEREST_AREAS):
        col_idx = idx % 4
        with cols[col_idx]:
            is_selected = interest['id'] in st.session_state.selected_interests
            if st.button(
                interest['label'],
                key=f"interest_{interest['id']}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                if is_selected:
                    st.session_state.selected_interests.remove(interest['id'])
                else:
                    st.session_state.selected_interests.append(interest['id'])

    # Show selected interests
    if st.session_state.selected_interests:
        selected_labels = [i['label'] for i in INTEREST_AREAS if i['id'] in st.session_state.selected_interests]
        st.markdown(f"<p><strong>Selected Interests:</strong> {', '.join(selected_labels)}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Section 2: Skills (Text inputs)
    st.markdown("<h3 class='section-header'>Tell us about your skills</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        current_skills = st.text_area(
            "What skills do you currently have?",
            placeholder="E.g., Video editing with Premiere Pro, basic After Effects, photography, storyboarding...",
            height=100,
            key="current_skills"
        )

        software_tools = st.text_area(
            "Software and tools you use",
            placeholder="E.g., Adobe Premiere, After Effects, DaVinci Resolve, Blender, Maya, Photoshop...",
            height=100,
            key="software_tools"
        )

    with col2:
        skills_to_learn = st.text_area(
            "What skills do you want to learn?",
            placeholder="E.g., 3D animation, VFX compositing, color grading, motion graphics...",
            height=100,
            key="skills_to_learn"
        )

        creative_strengths = st.text_area(
            "What are your creative strengths?",
            placeholder="E.g., Storytelling, visual design, attention to detail, working with clients...",
            height=100,
            key="creative_strengths"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Section 3: Experience & Goals
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 class='section-header'>Your Experience</h3>", unsafe_allow_html=True)

        # Experience level slider
        experience_value = st.slider(
            "Overall Experience Level",
            min_value=1,
            max_value=5,
            value=3,
            help="Rate your overall creative/technical experience"
        )
        experience_level = EXPERIENCE_LEVELS[experience_value]
        st.markdown(f"""
            <div class="info-box">
                <strong>Level:</strong> {experience_level}
            </div>
        """, unsafe_allow_html=True)

        # Years of experience
        years_experience = st.number_input(
            "Years of Experience",
            min_value=0,
            max_value=50,
            value=1,
            help="Total years in media/creative fields"
        )

    with col2:
        st.markdown("<h3 class='section-header'>Your Goals</h3>", unsafe_allow_html=True)

        # Career goals
        goals = st.text_area(
            "Career Goals",
            placeholder="E.g., Become a VFX artist at a major studio, Start my own animation channel...",
            height=80
        )

        # What they want to create
        project_interests = st.text_area(
            "What do you want to create?",
            placeholder="E.g., Short films, YouTube animations, music videos, commercials...",
            height=80
        )

    # Submit button
    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        submit = st.button("Get Recommendations", use_container_width=True, type="primary")

    if submit:
        # Combine all skills text inputs
        all_skills_text = []
        if current_skills:
            all_skills_text.append(current_skills)
        if software_tools:
            all_skills_text.append(software_tools)
        if skills_to_learn:
            all_skills_text.append(f"Want to learn: {skills_to_learn}")
        if creative_strengths:
            all_skills_text.append(f"Strengths: {creative_strengths}")

        combined_skills = " | ".join(all_skills_text) if all_skills_text else ""

        if not st.session_state.selected_interests and not combined_skills:
            st.error("Please select at least one interest area or describe your skills to get recommendations.")
        else:
            # Get interest labels for profile
            interest_labels = [i['label'] for i in INTEREST_AREAS if i['id'] in st.session_state.selected_interests]

            # Store form data
            st.session_state.user_profile = {
                "interests": interest_labels,
                "skills": [s.strip() for s in current_skills.split(",") if s.strip()] if current_skills else [],
                "skills_text": combined_skills,
                "software_tools": software_tools,
                "skills_to_learn": skills_to_learn,
                "creative_strengths": creative_strengths,
                "experience_level": experience_level,
                "years_experience": years_experience,
                "goals": goals,
                "project_interests": project_interests
            }
            st.session_state.form_submitted = True
            st.rerun()


def render_recommendations(client):
    """Render the recommendations page."""
    st.markdown("""
        <div class="main-header">
            <h1>Your Personalized Recommendations</h1>
            <p>Based on your creative interests and skills, here are courses and mentors perfect for you.</p>
        </div>
    """, unsafe_allow_html=True)

    user_profile = st.session_state.get('user_profile', {})

    # Show user profile summary
    with st.expander("Your Profile Summary", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if user_profile.get('interests'):
                st.write("**Interest Areas:**")
                interests_html = "".join([f'<span class="skill-tag">{i}</span>' for i in user_profile.get('interests', [])])
                st.markdown(interests_html, unsafe_allow_html=True)
            if user_profile.get('skills_text'):
                st.write("**Skills:**")
                st.write(user_profile.get('skills_text'))
        with col2:
            st.write(f"**Experience Level:** {user_profile.get('experience_level', 'N/A')}")
            st.write(f"**Years of Experience:** {user_profile.get('years_experience', 'N/A')}")
            if user_profile.get('goals'):
                st.write(f"**Goals:** {user_profile.get('goals')}")
            if user_profile.get('project_interests'):
                st.write(f"**Want to Create:** {user_profile.get('project_interests')}")

    # Get recommendations
    with st.spinner("Getting personalized recommendations..."):
        if client.is_configured():
            # Use Databricks RAG
            result = client.get_recommendations(user_profile)
            if result["success"]:
                st.markdown("""
                    <div class="info-box">
                        Recommendations powered by Databricks RAG
                    </div>
                """, unsafe_allow_html=True)
                # Display raw recommendations from RAG
                st.markdown("<h3 class='section-header'>AI-Generated Recommendations</h3>", unsafe_allow_html=True)
                st.markdown(result["recommendations"])
            else:
                st.error(f"Error getting recommendations: {result['error']}")
                st.info("Falling back to demo recommendations...")
                result = get_mock_recommendations(user_profile)
                render_mock_recommendations(result)
        else:
            # Use mock recommendations
            result = get_mock_recommendations(user_profile)
            render_mock_recommendations(result)

    # Navigation buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Skills Form", use_container_width=True):
            st.session_state.form_submitted = False
            st.session_state.current_page = "main"
            st.rerun()
    with col2:
        if st.button("Find Jobs", use_container_width=True, type="primary"):
            st.session_state.current_page = "jobs"
            st.rerun()
    with col3:
        tracked_count = len(st.session_state.get('tracked_courses', {}))
        completed_count = len(st.session_state.get('completed_courses', {}))
        if st.button(f"My Profile ({tracked_count + completed_count})", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()


def render_mock_recommendations(result):
    """Render the mock recommendations in a structured format."""
    init_course_tracking()
    user_profile = st.session_state.get('user_profile', {})

    # Get Coursera courses based on user interests
    interests = user_profile.get('interests', [])
    skills_text = user_profile.get('skills_text', '')
    coursera_courses = get_courses_for_interests(interests, skills_text, limit=5)

    # Get the Coursera background image
    coursera_img = get_coursera_image_base64()

    # Courses section
    st.markdown("<h3 class='section-header'>Recommended Courses from Coursera</h3>", unsafe_allow_html=True)

    if coursera_courses:
        for idx, course in enumerate(coursera_courses):
            # Use fixed Coursera image from assets
            if coursera_img:
                image_html = f'<img src="{coursera_img}" class="course-image" alt="Coursera Course">'
            else:
                image_html = '<div class="course-image-placeholder">C</div>'

            course_id = course.get('url', course.get('name', ''))
            is_tracked = course_id in st.session_state.tracked_courses or course_id in st.session_state.completed_courses

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"""
                    <a href="{course['url']}" target="_blank" class="course-card-link">
                        <div class="course-card">
                            {image_html}
                            <span class="provider-tag">{course.get('provider', 'Coursera')}</span>
                            <h4>{course['name']}</h4>
                            <p>{course.get('description', '')}</p>
                            <p><span class="difficulty-tag">{course.get('difficulty', 'Beginner')}</span> | {course.get('duration', 'Self-paced')}</p>
                        </div>
                    </a>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
                if is_tracked:
                    st.markdown(f"""
                        <p style='color: {COLORS["accent"]}; font-size: 0.85rem; text-align: center;'>
                            Already tracking
                        </p>
                    """, unsafe_allow_html=True)
                else:
                    if st.button("Add to Tracker", key=f"add_course_{idx}", use_container_width=True):
                        if add_course_to_tracker(course):
                            st.toast("Course added to your tracker!")
    else:
        # Fallback to mock courses if no Coursera courses found
        courses = result.get('courses', [])
        for idx, course in enumerate(courses):
            col1, col2 = st.columns([4, 1])

            with col1:
                if coursera_img:
                    fallback_image = f'<img src="{coursera_img}" class="course-image" alt="Course">'
                else:
                    fallback_image = '<div class="course-image-placeholder">C</div>'

                st.markdown(f"""
                    <div class="course-card">
                        {fallback_image}
                        <h4>{course['name']}</h4>
                        <p>{course['description']}</p>
                        <p><span class="difficulty-tag">{course['difficulty']}</span> | {course['duration']}</p>
                        <p><em>Why: {course['relevance']}</em></p>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
                mock_course = {
                    'name': course['name'],
                    'provider': 'Creative Lab',
                    'url': '#',
                    'difficulty': course['difficulty'],
                    'duration': course['duration']
                }
                course_id = course['name']
                is_tracked = course_id in st.session_state.tracked_courses or course_id in st.session_state.completed_courses

                if is_tracked:
                    st.markdown(f"""
                        <p style='color: {COLORS["accent"]}; font-size: 0.85rem; text-align: center;'>
                            Already tracking
                        </p>
                    """, unsafe_allow_html=True)
                else:
                    if st.button("Add to Tracker", key=f"add_mock_{idx}", use_container_width=True):
                        if add_course_to_tracker(mock_course):
                            st.toast("Course added to your tracker!")

    # Mentors section
    st.markdown("<h3 class='section-header'>Recommended Mentors</h3>", unsafe_allow_html=True)

    mentors = result.get('mentors', [])
    if mentors:
        cols = st.columns(len(mentors))
        for idx, mentor in enumerate(mentors):
            with cols[idx]:
                expertise_tags = "".join([f'<span class="skill-tag">{e}</span>' for e in mentor['expertise']])
                st.markdown(f"""
                    <div class="mentor-card">
                        <h4>{mentor['name']}</h4>
                        <p><strong>{mentor['title']}</strong></p>
                        <p>{mentor['experience']} experience</p>
                        <p>{expertise_tags}</p>
                        <p><em>{mentor['match_reason']}</em></p>
                    </div>
                """, unsafe_allow_html=True)

    # Learning path section
    st.markdown("<h3 class='section-header'>Suggested Learning Path</h3>", unsafe_allow_html=True)

    learning_path = result.get('learning_path', [])
    path_html = "<ol>"
    for step in learning_path:
        # Remove the number prefix if it exists
        step_text = step.lstrip("0123456789. ")
        path_html += f"<li>{step_text}</li>"
    path_html += "</ol>"

    st.markdown(f"""
        <div class="learning-path">
            {path_html}
        </div>
    """, unsafe_allow_html=True)


def init_course_tracking():
    """Initialize course tracking in session state."""
    if 'tracked_courses' not in st.session_state:
        st.session_state.tracked_courses = {}
    if 'completed_courses' not in st.session_state:
        st.session_state.completed_courses = {}


def add_course_to_tracker(course):
    """Add a course to the user's tracker."""
    init_course_tracking()
    course_id = course.get('url', course.get('name', ''))
    if course_id not in st.session_state.tracked_courses and course_id not in st.session_state.completed_courses:
        st.session_state.tracked_courses[course_id] = {
            'name': course.get('name', 'Unknown Course'),
            'provider': course.get('provider', 'Coursera'),
            'url': course.get('url', ''),
            'difficulty': course.get('difficulty', 'Beginner'),
            'duration': course.get('duration', 'Self-paced'),
            'added_date': datetime.now().strftime("%Y-%m-%d"),
            'status': 'in_progress'
        }
        return True
    return False


def mark_course_complete(course_id, certificate_data=None):
    """Mark a course as complete with optional certificate."""
    init_course_tracking()
    if course_id in st.session_state.tracked_courses:
        course = st.session_state.tracked_courses.pop(course_id)
        course['status'] = 'completed'
        course['completed_date'] = datetime.now().strftime("%Y-%m-%d")
        if certificate_data:
            course['certificate'] = certificate_data
        st.session_state.completed_courses[course_id] = course
        return True
    return False


def render_profile_page():
    """Render the user profile page with course tracker, attendance, resources, and mentor reviews."""
    init_course_tracking()
    init_attendance_tracking()
    init_resources_tracking()
    init_mentor_reviews()
    username = get_current_user()

    st.markdown(f"""
        <div class="main-header">
            <h1>{username}'s Profile</h1>
            <p>Track your learning journey, resources, and mentor feedback</p>
        </div>
    """, unsafe_allow_html=True)

    # Create tabs for Courses, Attendance, Resources, and Mentor Reviews
    tab1, tab2, tab3, tab4 = st.tabs(["My Courses", "Attendance", "Devices & Licenses", "Mentor Reviews"])

    with tab1:
        render_courses_tab()

    with tab2:
        render_attendance_tab()

    with tab3:
        render_resources_tab()

    with tab4:
        render_mentor_reviews_tab()

    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if st.button("Back to Recommendations", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()


def init_resources_tracking():
    """Initialize devices and licenses tracking in session state."""
    if 'resources' not in st.session_state:
        st.session_state.resources = {
            'licenses': [
                {
                    'id': 'lic_1',
                    'name': 'Coursera Plus',
                    'type': 'Learning Platform',
                    'status': 'active',
                    'assigned_date': '2025-09-01',
                    'expiry_date': '2026-08-31',
                    'notes': 'Full access to all Coursera courses'
                },
                {
                    'id': 'lic_2',
                    'name': 'Adobe Creative Cloud',
                    'type': 'Software',
                    'status': 'active',
                    'assigned_date': '2025-09-01',
                    'expiry_date': '2026-08-31',
                    'notes': 'Includes Premiere Pro, After Effects, Photoshop, Illustrator'
                },
                {
                    'id': 'lic_3',
                    'name': 'Blender',
                    'type': 'Software',
                    'status': 'active',
                    'assigned_date': '2025-09-01',
                    'expiry_date': None,
                    'notes': 'Free and open source - no license required'
                },
            ],
            'devices': [
                {
                    'id': 'dev_1',
                    'name': 'MacBook Pro 14"',
                    'type': 'Laptop',
                    'status': 'assigned',
                    'assigned_date': '2025-09-01',
                    'serial_number': 'MBP-2025-001',
                    'notes': 'Primary workstation for coursework'
                },
                {
                    'id': 'dev_2',
                    'name': 'Wacom Intuos Pro',
                    'type': 'Drawing Tablet',
                    'status': 'assigned',
                    'assigned_date': '2025-10-15',
                    'serial_number': 'WIP-2025-042',
                    'notes': 'For digital illustration and animation'
                },
            ],
            'requests': [
                {
                    'id': 'req_1',
                    'request_type': 'license',
                    'item_name': 'DaVinci Resolve Studio',
                    'status': 'pending',
                    'submitted_date': '2026-01-15',
                    'justification': 'Need advanced color grading features for my film project. The free version lacks noise reduction and HDR tools.',
                    'admin_notes': ''
                },
            ]
        }


def render_resources_tab():
    """Render the devices and licenses tracking tab."""
    resources = st.session_state.get('resources', {})
    licenses = resources.get('licenses', [])
    devices = resources.get('devices', [])
    requests = resources.get('requests', [])

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        active_licenses = sum(1 for l in licenses if l['status'] == 'active')
        st.markdown(
            f'<div class="stats-card"><div class="stats-number">{active_licenses}</div><div class="stats-label">Active Licenses</div></div>',
            unsafe_allow_html=True
        )

    with col2:
        assigned_devices = sum(1 for d in devices if d['status'] == 'assigned')
        st.markdown(
            f'<div class="stats-card"><div class="stats-number">{assigned_devices}</div><div class="stats-label">Assigned Devices</div></div>',
            unsafe_allow_html=True
        )

    with col3:
        pending_requests = sum(1 for r in requests if r['status'] == 'pending')
        st.markdown(
            f'<div class="stats-card"><div class="stats-number">{pending_requests}</div><div class="stats-label">Pending Requests</div></div>',
            unsafe_allow_html=True
        )

    with col4:
        total_resources = len(licenses) + len(devices)
        st.markdown(
            f'<div class="stats-card"><div class="stats-number">{total_resources}</div><div class="stats-label">Total Resources</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Licenses Section
    st.markdown("<h3 class='section-header'>Software Licenses</h3>", unsafe_allow_html=True)

    if licenses:
        for lic in licenses:
            status = lic['status']
            if status == 'active':
                status_color = "#28a745"
                status_bg = "#d4edda"
                status_text = "Active"
            elif status == 'expired':
                status_color = COLORS['mid_accent']
                status_bg = COLORS['light_accent']
                status_text = "Expired"
            else:
                status_color = COLORS['secondary']
                status_bg = COLORS['light_accent']
                status_text = status.capitalize()

            expiry_text = f"Expires: {lic['expiry_date']}" if lic.get('expiry_date') else "No expiration"

            html = f'''<div style="background-color: {COLORS["white"]}; padding: 1rem; border-radius: 5px; margin-bottom: 0.75rem; border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong style="color: {COLORS["primary_dark"]}; font-size: 1.1rem;">{lic["name"]}</strong>
                        <span style="background-color: {COLORS["light_accent"]}; color: {COLORS["mid_accent"]}; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.75rem; margin-left: 0.5rem;">{lic["type"]}</span>
                    </div>
                    <div style="background-color: {status_bg}; padding: 0.25rem 0.75rem; border-radius: 15px;">
                        <span style="color: {status_color}; font-weight: 500; font-size: 0.85rem;">{status_text}</span>
                    </div>
                </div>
                <p style="color: {COLORS["text_dark"]}; margin: 0.5rem 0 0.25rem 0; font-size: 0.9rem;">{lic.get("notes", "")}</p>
                <p style="color: {COLORS["secondary"]}; margin: 0; font-size: 0.8rem;">Assigned: {lic["assigned_date"]} | {expiry_text}</p>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="info-box"><p>No licenses assigned yet.</p></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Devices Section
    st.markdown("<h3 class='section-header'>Devices & Equipment</h3>", unsafe_allow_html=True)

    if devices:
        for dev in devices:
            status = dev['status']
            if status == 'assigned':
                status_color = "#28a745"
                status_bg = "#d4edda"
                status_text = "Assigned"
            elif status == 'maintenance':
                status_color = "#856404"
                status_bg = "#fff3cd"
                status_text = "In Maintenance"
            else:
                status_color = COLORS['secondary']
                status_bg = COLORS['light_accent']
                status_text = status.capitalize()

            serial_text = f"S/N: {dev['serial_number']}" if dev.get('serial_number') else ""

            html = f'''<div style="background-color: {COLORS["white"]}; padding: 1rem; border-radius: 5px; margin-bottom: 0.75rem; border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong style="color: {COLORS["primary_dark"]}; font-size: 1.1rem;">{dev["name"]}</strong>
                        <span style="background-color: {COLORS["light_accent"]}; color: {COLORS["mid_accent"]}; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.75rem; margin-left: 0.5rem;">{dev["type"]}</span>
                    </div>
                    <div style="background-color: {status_bg}; padding: 0.25rem 0.75rem; border-radius: 15px;">
                        <span style="color: {status_color}; font-weight: 500; font-size: 0.85rem;">{status_text}</span>
                    </div>
                </div>
                <p style="color: {COLORS["text_dark"]}; margin: 0.5rem 0 0.25rem 0; font-size: 0.9rem;">{dev.get("notes", "")}</p>
                <p style="color: {COLORS["secondary"]}; margin: 0; font-size: 0.8rem;">Assigned: {dev["assigned_date"]} | {serial_text}</p>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="info-box"><p>No devices assigned yet.</p></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Pending Requests Section
    if requests:
        st.markdown("<h3 class='section-header'>My Requests</h3>", unsafe_allow_html=True)

        for req in requests:
            status = req['status']
            if status == 'approved':
                status_color = "#28a745"
                status_bg = "#d4edda"
                status_text = "Approved"
            elif status == 'pending':
                status_color = "#856404"
                status_bg = "#fff3cd"
                status_text = "Pending Review"
            elif status == 'denied':
                status_color = COLORS['mid_accent']
                status_bg = COLORS['light_accent']
                status_text = "Denied"
            else:
                status_color = COLORS['secondary']
                status_bg = COLORS['light_accent']
                status_text = status.capitalize()

            req_type = "License" if req['request_type'] == 'license' else "Device"

            html = f'''<div style="background-color: {COLORS["white"]}; padding: 1rem; border-radius: 5px; margin-bottom: 0.75rem; border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong style="color: {COLORS["primary_dark"]}; font-size: 1.1rem;">{req["item_name"]}</strong>
                        <span style="background-color: {COLORS["light_accent"]}; color: {COLORS["mid_accent"]}; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.75rem; margin-left: 0.5rem;">{req_type} Request</span>
                    </div>
                    <div style="background-color: {status_bg}; padding: 0.25rem 0.75rem; border-radius: 15px;">
                        <span style="color: {status_color}; font-weight: 500; font-size: 0.85rem;">{status_text}</span>
                    </div>
                </div>
                <p style="color: {COLORS["text_dark"]}; margin: 0.5rem 0 0.25rem 0; font-size: 0.9rem;"><strong>Justification:</strong> {req["justification"]}</p>
                <p style="color: {COLORS["secondary"]}; margin: 0; font-size: 0.8rem;">Submitted: {req["submitted_date"]}</p>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)

            if req.get('admin_notes'):
                st.markdown(
                    f'<div style="background-color: {COLORS["light_accent"]}; padding: 0.75rem; border-radius: 5px; margin-top: -0.5rem; margin-bottom: 0.75rem;"><strong style="color: {COLORS["primary_dark"]};">Admin Response:</strong> <span style="color: {COLORS["text_dark"]};">{req["admin_notes"]}</span></div>',
                    unsafe_allow_html=True
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # Request Form
    st.markdown("<h3 class='section-header'>Request New Resource</h3>", unsafe_allow_html=True)

    with st.form("resource_request_form"):
        col1, col2 = st.columns(2)

        with col1:
            request_type = st.selectbox(
                "Request Type",
                options=["license", "device"],
                format_func=lambda x: "Software License" if x == "license" else "Device / Equipment"
            )

        with col2:
            if request_type == "license":
                item_name = st.text_input(
                    "License Name",
                    placeholder="e.g., DaVinci Resolve Studio, Maya, Houdini..."
                )
            else:
                item_name = st.text_input(
                    "Device Name",
                    placeholder="e.g., Camera, Microphone, External SSD..."
                )

        justification = st.text_area(
            "Justification",
            placeholder="Please explain why you need this resource and how it will support your coursework or projects...",
            height=100
        )

        related_course = st.text_input(
            "Related Course or Project (optional)",
            placeholder="e.g., Film Production course, Animation final project..."
        )

        submitted = st.form_submit_button("Submit Request", use_container_width=True)

        if submitted:
            if not item_name or not justification:
                st.error("Please provide both the item name and justification.")
            else:
                # Add the request to session state
                new_request = {
                    'id': f"req_{len(requests) + 1}",
                    'request_type': request_type,
                    'item_name': item_name,
                    'status': 'pending',
                    'submitted_date': datetime.now().strftime("%Y-%m-%d"),
                    'justification': justification + (f" (Related to: {related_course})" if related_course else ""),
                    'admin_notes': ''
                }
                st.session_state.resources['requests'].append(new_request)
                st.toast("Request submitted successfully!")
                st.rerun()


def init_attendance_tracking():
    """Initialize attendance tracking in session state."""
    if 'attendance_records' not in st.session_state:
        # Sample attendance data for demo
        st.session_state.attendance_records = {
            'weekly_classes': [
                {'date': '2026-01-27', 'class_name': 'Animation Fundamentals', 'status': 'present', 'notes': ''},
                {'date': '2026-01-20', 'class_name': 'Animation Fundamentals', 'status': 'present', 'notes': ''},
                {'date': '2026-01-13', 'class_name': 'Animation Fundamentals', 'status': 'absent', 'notes': 'Sick - notified in advance'},
                {'date': '2026-01-06', 'class_name': 'Animation Fundamentals', 'status': 'present', 'notes': ''},
                {'date': '2025-12-30', 'class_name': 'Animation Fundamentals', 'status': 'present', 'notes': ''},
                {'date': '2025-12-23', 'class_name': 'Animation Fundamentals', 'status': 'late', 'notes': 'Arrived 15 mins late'},
                {'date': '2025-12-16', 'class_name': 'Animation Fundamentals', 'status': 'present', 'notes': ''},
                {'date': '2025-12-09', 'class_name': 'Animation Fundamentals', 'status': 'present', 'notes': ''},
            ],
            'mentoring_sessions': [
                {'date': '2026-01-25', 'mentor': 'Sarah Chen', 'status': 'present', 'duration': '45 min', 'notes': ''},
                {'date': '2026-01-18', 'mentor': 'Sarah Chen', 'status': 'present', 'duration': '60 min', 'notes': ''},
                {'date': '2026-01-11', 'mentor': 'David Park', 'status': 'present', 'duration': '45 min', 'notes': ''},
                {'date': '2026-01-04', 'mentor': 'Sarah Chen', 'status': 'absent', 'duration': '0 min', 'notes': 'Rescheduled to next week'},
                {'date': '2025-12-28', 'mentor': 'Sarah Chen', 'status': 'present', 'duration': '50 min', 'notes': ''},
                {'date': '2025-12-21', 'mentor': 'David Park', 'status': 'present', 'duration': '45 min', 'notes': ''},
            ]
        }


def render_attendance_tab():
    """Render the attendance tracking tab."""
    records = st.session_state.get('attendance_records', {})
    weekly_classes = records.get('weekly_classes', [])
    mentoring_sessions = records.get('mentoring_sessions', [])

    # Colors from palette (no red)
    color_present = "#28a745"
    color_present_bg = "#d4edda"
    color_present_text = "#155724"
    color_late = "#856404"
    color_late_bg = "#fff3cd"
    color_absent = COLORS['mid_accent']  # Dark green instead of red
    color_absent_bg = COLORS['light_accent']  # Light sage instead of red
    color_absent_text = COLORS['primary_dark']  # Dark olive instead of red

    # Calculate summary stats
    total_weekly = len(weekly_classes)
    weekly_present = sum(1 for c in weekly_classes if c['status'] == 'present')
    weekly_late = sum(1 for c in weekly_classes if c['status'] == 'late')
    weekly_absent = sum(1 for c in weekly_classes if c['status'] == 'absent')

    total_mentoring = len(mentoring_sessions)
    mentoring_present = sum(1 for s in mentoring_sessions if s['status'] == 'present')
    mentoring_absent = sum(1 for s in mentoring_sessions if s['status'] == 'absent')

    overall_total = total_weekly + total_mentoring
    overall_attended = weekly_present + weekly_late + mentoring_present
    overall_rate = (overall_attended / overall_total * 100) if overall_total > 0 else 0

    # Overall Summary
    st.markdown("<h3 class='section-header'>Attendance Summary</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if overall_rate >= 80:
            rate_color = color_present
        elif overall_rate >= 60:
            rate_color = color_late
        else:
            rate_color = color_absent
        rate_display = f"{overall_rate:.0f}"
        st.markdown(
            f'<div class="stats-card"><div class="stats-number" style="color: {rate_color};">{rate_display}%</div><div class="stats-label">Overall Attendance</div></div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div class="stats-card"><div class="stats-number">{overall_attended}</div><div class="stats-label">Sessions Attended</div></div>',
            unsafe_allow_html=True
        )

    with col3:
        missed_total = weekly_absent + mentoring_absent
        st.markdown(
            f'<div class="stats-card"><div class="stats-number">{missed_total}</div><div class="stats-label">Sessions Missed</div></div>',
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f'<div class="stats-card"><div class="stats-number">{overall_total}</div><div class="stats-label">Total Sessions</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Weekly Classes Section
    st.markdown("<h3 class='section-header'>Weekly In-Person Classes</h3>", unsafe_allow_html=True)

    # Weekly class stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div style="background-color: {color_present_bg}; padding: 0.75rem; border-radius: 5px; text-align: center;"><strong style="color: {color_present_text};">{weekly_present} Present</strong></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div style="background-color: {color_late_bg}; padding: 0.75rem; border-radius: 5px; text-align: center;"><strong style="color: {color_late};">{weekly_late} Late</strong></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f'<div style="background-color: {color_absent_bg}; padding: 0.75rem; border-radius: 5px; text-align: center;"><strong style="color: {color_absent_text};">{weekly_absent} Absent</strong></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Weekly class details
    if weekly_classes:
        for record in weekly_classes:
            status = record['status']
            if status == 'present':
                s_color = color_present
                s_bg = color_present_bg
                s_text = 'Present'
            elif status == 'late':
                s_color = color_late
                s_bg = color_late_bg
                s_text = 'Late'
            else:
                s_color = color_absent
                s_bg = color_absent_bg
                s_text = 'Absent'

            notes_part = ""
            if record.get('notes'):
                notes_part = f' - <span style="color: {COLORS["secondary"]}; font-size: 0.85rem;">{record["notes"]}</span>'

            html = f'''<div style="display: flex; align-items: center; padding: 0.75rem; background-color: {COLORS["white"]}; border-radius: 5px; margin-bottom: 0.5rem; border-left: 4px solid {s_color};">
                <div style="flex: 1;">
                    <strong style="color: {COLORS["primary_dark"]};">{record["date"]}</strong>
                    <span style="color: {COLORS["text_dark"]}; margin-left: 1rem;">{record["class_name"]}</span>{notes_part}
                </div>
                <div style="background-color: {s_bg}; padding: 0.25rem 0.75rem; border-radius: 15px;">
                    <span style="color: {s_color}; font-weight: 500; font-size: 0.85rem;">{s_text}</span>
                </div>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mentoring Sessions Section
    st.markdown("<h3 class='section-header'>Mentoring Sessions</h3>", unsafe_allow_html=True)

    # Mentoring stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div style="background-color: {color_present_bg}; padding: 0.75rem; border-radius: 5px; text-align: center;"><strong style="color: {color_present_text};">{mentoring_present} Attended</strong></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div style="background-color: {color_absent_bg}; padding: 0.75rem; border-radius: 5px; text-align: center;"><strong style="color: {color_absent_text};">{mentoring_absent} Missed</strong></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Mentoring session details
    if mentoring_sessions:
        for record in mentoring_sessions:
            status = record['status']
            if status == 'present':
                s_color = color_present
                s_bg = color_present_bg
                s_text = 'Attended'
            else:
                s_color = color_absent
                s_bg = color_absent_bg
                s_text = 'Missed'

            duration_part = ""
            if record.get('duration') and record['duration'] != '0 min':
                duration_part = f' <span style="color: {COLORS["accent"]};">({record["duration"]})</span>'

            notes_part = ""
            if record.get('notes'):
                notes_part = f' - <span style="color: {COLORS["secondary"]}; font-size: 0.85rem;">{record["notes"]}</span>'

            html = f'''<div style="display: flex; align-items: center; padding: 0.75rem; background-color: {COLORS["white"]}; border-radius: 5px; margin-bottom: 0.5rem; border-left: 4px solid {s_color};">
                <div style="flex: 1;">
                    <strong style="color: {COLORS["primary_dark"]};">{record["date"]}</strong>
                    <span style="color: {COLORS["text_dark"]}; margin-left: 1rem;">with {record["mentor"]}</span>{duration_part}{notes_part}
                </div>
                <div style="background-color: {s_bg}; padding: 0.25rem 0.75rem; border-radius: 15px;">
                    <span style="color: {s_color}; font-weight: 500; font-size: 0.85rem;">{s_text}</span>
                </div>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)

    # Missed Classes Summary
    missed_weekly = [c for c in weekly_classes if c['status'] == 'absent']
    missed_mentoring = [s for s in mentoring_sessions if s['status'] == 'absent']

    if missed_weekly or missed_mentoring:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-header'>Missed Sessions Summary</h3>", unsafe_allow_html=True)

        missed_w_count = len(missed_weekly)
        missed_m_count = len(missed_mentoring)
        attention_html = f'''<div style="background-color: {color_absent_bg}; padding: 1rem; border-radius: 5px; border-left: 4px solid {color_absent};">
            <strong style="color: {color_absent_text};">Attention Required</strong>
            <p style="color: {COLORS["text_dark"]}; margin: 0.5rem 0 0 0;">
                You have missed {missed_w_count} weekly class(es) and {missed_m_count} mentoring session(s).
                Please reach out to your mentor if you need to discuss make-up options.
            </p>
        </div>'''
        st.markdown(attention_html, unsafe_allow_html=True)

        if missed_weekly:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Missed Weekly Classes:**")
            for record in missed_weekly:
                reason = f" - {record['notes']}" if record.get('notes') else ""
                st.markdown(f"- {record['date']}: {record['class_name']}{reason}")

        if missed_mentoring:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Missed Mentoring Sessions:**")
            for record in missed_mentoring:
                reason = f" - {record['notes']}" if record.get('notes') else ""
                st.markdown(f"- {record['date']}: Session with {record['mentor']}{reason}")


def init_mentor_reviews():
    """Initialize mentor reviews in session state."""
    if 'mentor_reviews' not in st.session_state:
        # Sample mentor reviews for demo
        st.session_state.mentor_reviews = [
            {
                'id': '1',
                'date': '2026-01-20',
                'mentor_name': 'Sarah Chen',
                'review_type': 'Weekly Review',
                'strengths': 'Excellent understanding of color theory and composition. Shows great creativity in project concepts.',
                'areas_for_improvement': 'Time management could be improved. Sometimes rushes final touches.',
                'action_plan': '1. Create a project timeline template\n2. Schedule buffer time for revisions\n3. Practice breaking down large projects into smaller milestones',
                'additional_notes': 'Great progress this week! Keep up the enthusiasm.',
                'positive_recognition': 'Outstanding work on the motion graphics assignment - very professional quality!'
            },
            {
                'id': '2',
                'date': '2026-01-15',
                'mentor_name': 'David Park',
                'review_type': 'Assignment Review',
                'strengths': 'Strong technical skills in After Effects. Good attention to keyframe timing.',
                'areas_for_improvement': 'Could explore more creative transitions. Try experimenting with 3D camera movements.',
                'action_plan': '1. Watch tutorials on advanced camera techniques\n2. Recreate 2 professional motion pieces for practice',
                'additional_notes': 'Ready to move on to more advanced projects.',
                'positive_recognition': None
            },
            {
                'id': '3',
                'date': '2026-01-10',
                'mentor_name': 'Sarah Chen',
                'review_type': 'Behavioral Note',
                'strengths': 'Very collaborative and supportive of other students. Takes feedback well.',
                'areas_for_improvement': 'Could speak up more in group critiques - your insights are valuable!',
                'action_plan': '1. Prepare at least one question or comment before each critique session',
                'additional_notes': None,
                'positive_recognition': 'Helped a fellow student troubleshoot their render issues - great teamwork!'
            }
        ]

    # Initialize career path suggestions
    if 'career_path' not in st.session_state:
        st.session_state.career_path = {
            'recommended_next_steps': [
                {'step': 'Complete Advanced Motion Graphics course', 'priority': 'High', 'status': 'in_progress'},
                {'step': 'Build a showreel with 5-7 best projects', 'priority': 'High', 'status': 'not_started'},
                {'step': 'Create 2 personal projects for portfolio', 'priority': 'Medium', 'status': 'in_progress'},
                {'step': 'Attend local creative industry meetups', 'priority': 'Medium', 'status': 'not_started'},
                {'step': 'Set up professional LinkedIn profile', 'priority': 'High', 'status': 'completed'},
                {'step': 'Apply for internships at motion design studios', 'priority': 'Medium', 'status': 'not_started'},
            ],
            'skills_to_develop': [
                {'skill': '3D Camera Animation', 'current_level': 'Beginner', 'target_level': 'Intermediate', 'mentor_notes': 'Focus on smooth camera movements and depth'},
                {'skill': 'Character Rigging', 'current_level': 'Not Started', 'target_level': 'Beginner', 'mentor_notes': 'Start with simple 2D character rigs'},
                {'skill': 'Sound Design', 'current_level': 'Beginner', 'target_level': 'Intermediate', 'mentor_notes': 'Learn to sync audio with motion'},
                {'skill': 'Client Communication', 'current_level': 'Intermediate', 'target_level': 'Advanced', 'mentor_notes': 'Practice presenting work and receiving feedback'},
                {'skill': 'Project Estimation', 'current_level': 'Beginner', 'target_level': 'Intermediate', 'mentor_notes': 'Learn to break down projects and estimate time'},
            ],
            'target_roles': ['Motion Designer', 'Junior Animator', 'Video Editor', 'VFX Artist'],
            'last_updated': '2026-01-20',
            'mentor_name': 'Sarah Chen'
        }


def render_courses_tab():
    """Render the courses tracking tab."""
    # Profile stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(st.session_state.tracked_courses)}</div>
                <div class="stats-label">Courses In Progress</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(st.session_state.completed_courses)}</div>
                <div class="stats-label">Courses Completed</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        total = len(st.session_state.tracked_courses) + len(st.session_state.completed_courses)
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{total}</div>
                <div class="stats-label">Total Courses</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Courses In Progress Section
    st.markdown("<h3 class='section-header'>Courses In Progress</h3>", unsafe_allow_html=True)

    if st.session_state.tracked_courses:
        for course_id, course in list(st.session_state.tracked_courses.items()):
            with st.container():
                st.markdown(f"""
                    <div class="course-tracker-card in-progress">
                        <span class="course-status-tag status-in-progress">In Progress</span>
                        <h4 style="color: {COLORS['primary_dark']}; margin-top: 0.5rem;">
                            <a href="{course['url']}" target="_blank" style="color: {COLORS['primary_dark']}; text-decoration: none;">
                                {course['name']}
                            </a>
                        </h4>
                        <p style="color: {COLORS['text_dark']};">{course['provider']} | {course['difficulty']} | {course['duration']}</p>
                        <p style="color: {COLORS['secondary']}; font-size: 0.85rem;">Started: {course['added_date']}</p>
                    </div>
                """, unsafe_allow_html=True)

                # Certificate upload section
                col1, col2 = st.columns([3, 1])
                with col1:
                    cert_key = f"cert_{hash(course_id) % 10000}"
                    uploaded_file = st.file_uploader(
                        f"Upload certificate for {course['name'][:30]}...",
                        type=['pdf', 'png', 'jpg', 'jpeg'],
                        key=cert_key
                    )
                with col2:
                    complete_key = f"complete_{hash(course_id) % 10000}"
                    if st.button("Mark Complete", key=complete_key, use_container_width=True):
                        cert_data = None
                        if uploaded_file:
                            cert_data = {
                                'filename': uploaded_file.name,
                                'type': uploaded_file.type,
                                'size': uploaded_file.size
                            }
                        mark_course_complete(course_id, cert_data)
                        st.toast(f"Congratulations! '{course['name']}' marked as complete!")
                        st.rerun()

                st.markdown("<hr style='border: none; border-top: 1px solid #e5e6de; margin: 1rem 0;'>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-box">
                <p>No courses in progress yet. Browse recommendations and add courses to start tracking!</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Completed Courses Section
    st.markdown("<h3 class='section-header'>Completed Courses</h3>", unsafe_allow_html=True)

    if st.session_state.completed_courses:
        for course_id, course in st.session_state.completed_courses.items():
            cert_info = ""
            if course.get('certificate'):
                cert_info = f"<p style='color: #28a745; font-size: 0.85rem;'>Certificate: {course['certificate']['filename']}</p>"

            st.markdown(f"""
                <div class="course-tracker-card completed">
                    <span class="course-status-tag status-completed">Completed</span>
                    <h4 style="color: {COLORS['primary_dark']}; margin-top: 0.5rem;">
                        <a href="{course['url']}" target="_blank" style="color: {COLORS['primary_dark']}; text-decoration: none;">
                            {course['name']}
                        </a>
                    </h4>
                    <p style="color: {COLORS['text_dark']};">{course['provider']} | {course['difficulty']} | {course['duration']}</p>
                    <p style="color: {COLORS['secondary']}; font-size: 0.85rem;">Completed: {course.get('completed_date', 'N/A')}</p>
                    {cert_info}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-box">
                <p>No completed courses yet. Keep learning and upload your certificates when you finish!</p>
            </div>
        """, unsafe_allow_html=True)


def render_mentor_reviews_tab():
    """Render the mentor reviews tab showing feedback from mentors."""
    st.markdown("<h3 class='section-header'>Mentor Feedback</h3>", unsafe_allow_html=True)

    reviews = st.session_state.get('mentor_reviews', [])

    if not reviews:
        st.markdown("""
            <div class="info-box">
                <p>No mentor reviews yet. Your mentor's feedback will appear here after your sessions.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(reviews)}</div>
                <div class="stats-label">Total Reviews</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        positive_count = sum(1 for r in reviews if r.get('positive_recognition'))
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{positive_count}</div>
                <div class="stats-label">Recognitions</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        mentors = set(r.get('mentor_name', '') for r in reviews)
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(mentors)}</div>
                <div class="stats-label">Mentors</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter options
    review_types = ['All'] + list(set(r.get('review_type', '') for r in reviews))
    selected_type = st.selectbox("Filter by Review Type", review_types)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display reviews
    filtered_reviews = reviews if selected_type == 'All' else [r for r in reviews if r.get('review_type') == selected_type]

    for review in filtered_reviews:
        review_type = review.get('review_type', 'Review')
        review_date = review.get('date', '')
        mentor_name = review.get('mentor_name', 'Mentor')

        # Review type badge color (no red - using dark greens)
        type_colors = {
            'Weekly Review': COLORS['primary_dark'],
            'Assignment Review': COLORS['accent'],
            'Behavioral Note': COLORS['mid_accent'],
            'Academic Concern': COLORS['mid_accent'],
            'Positive Recognition': '#28a745'
        }
        badge_color = type_colors.get(review_type, COLORS['secondary'])

        with st.expander(f"{review_type} - {review_date} (by {mentor_name})", expanded=False):
            # Positive Recognition (if any)
            if review.get('positive_recognition'):
                st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; border-left: 4px solid #28a745;">
                        <strong style="color: #155724;">Positive Recognition</strong>
                        <p style="color: #155724; margin: 0.5rem 0 0 0;">{review['positive_recognition']}</p>
                    </div>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                # Strengths
                if review.get('strengths'):
                    st.markdown(f"""
                        <div style="background-color: {COLORS['light_accent']}; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                            <strong style="color: {COLORS['primary_dark']};">Your Strengths</strong>
                            <p style="color: {COLORS['text_dark']}; margin: 0.5rem 0 0 0;">{review['strengths']}</p>
                        </div>
                    """, unsafe_allow_html=True)

            with col2:
                # Areas for Improvement
                if review.get('areas_for_improvement'):
                    st.markdown(f"""
                        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; border-left: 4px solid #ffc107;">
                            <strong style="color: #856404;">Areas for Improvement</strong>
                            <p style="color: {COLORS['text_dark']}; margin: 0.5rem 0 0 0;">{review['areas_for_improvement']}</p>
                        </div>
                    """, unsafe_allow_html=True)

            # Action Plan
            if review.get('action_plan'):
                st.markdown(f"""
                    <div style="background-color: {COLORS['white']}; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; border: 1px solid {COLORS['secondary']};">
                        <strong style="color: {COLORS['primary_dark']};">Action Plan / Next Steps</strong>
                        <p style="color: {COLORS['text_dark']}; margin: 0.5rem 0 0 0; white-space: pre-line;">{review['action_plan']}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Additional Notes
            if review.get('additional_notes'):
                st.markdown(f"""
                    <div style="background-color: {COLORS['background']}; padding: 1rem; border-radius: 5px;">
                        <strong style="color: {COLORS['secondary']};">Additional Notes</strong>
                        <p style="color: {COLORS['text_dark']}; margin: 0.5rem 0 0 0;">{review['additional_notes']}</p>
                    </div>
                """, unsafe_allow_html=True)

    # Career Path Suggestions Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>Career Path Suggestions</h3>", unsafe_allow_html=True)

    career_path = st.session_state.get('career_path', {})

    if career_path:
        # Last updated info
        st.markdown(
            f'<p style="color: {COLORS["secondary"]}; font-size: 0.85rem;">Last updated: {career_path.get("last_updated", "N/A")} by {career_path.get("mentor_name", "Mentor")}</p>',
            unsafe_allow_html=True
        )

        # Target roles
        if career_path.get('target_roles'):
            roles_html = " ".join([f'<span style="background-color: {COLORS["primary_dark"]}; color: {COLORS["white"]}; padding: 0.3rem 0.75rem; border-radius: 15px; margin-right: 0.5rem; font-size: 0.85rem;">{role}</span>' for role in career_path['target_roles']])
            st.markdown(
                f'<div style="margin-bottom: 1rem;"><strong style="color: {COLORS["primary_dark"]};">Target Roles:</strong> {roles_html}</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Two columns layout
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f'<h4 style="color: {COLORS["primary_dark"]}; margin-bottom: 1rem;">Recommended Next Steps</h4>',
                unsafe_allow_html=True
            )

            next_steps = career_path.get('recommended_next_steps', [])
            for step in next_steps:
                status = step.get('status', 'not_started')
                priority = step.get('priority', 'Medium')

                if status == 'completed':
                    status_icon = "&#10003;"
                    status_color = "#28a745"
                    status_bg = "#d4edda"
                elif status == 'in_progress':
                    status_icon = "&#8226;"
                    status_color = "#856404"
                    status_bg = "#fff3cd"
                else:
                    status_icon = "&#9675;"
                    status_color = COLORS['secondary']
                    status_bg = COLORS['light_accent']

                priority_color = COLORS['primary_dark'] if priority == 'High' else COLORS['accent'] if priority == 'Medium' else COLORS['secondary']

                html = f'''<div style="background-color: {COLORS["white"]}; padding: 0.75rem; border-radius: 5px; margin-bottom: 0.5rem; border-left: 4px solid {status_color};">
                    <div style="display: flex; align-items: center;">
                        <span style="color: {status_color}; font-size: 1.2rem; margin-right: 0.5rem;">{status_icon}</span>
                        <span style="color: {COLORS["text_dark"]}; flex: 1;">{step["step"]}</span>
                        <span style="background-color: {COLORS["light_accent"]}; color: {priority_color}; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem;">{priority}</span>
                    </div>
                </div>'''
                st.markdown(html, unsafe_allow_html=True)

        with col2:
            st.markdown(
                f'<h4 style="color: {COLORS["primary_dark"]}; margin-bottom: 1rem;">Skills to Develop</h4>',
                unsafe_allow_html=True
            )

            skills = career_path.get('skills_to_develop', [])
            for skill in skills:
                current = skill.get('current_level', 'Not Started')
                target = skill.get('target_level', 'Intermediate')
                notes = skill.get('mentor_notes', '')

                # Progress indicator
                levels = ['Not Started', 'Beginner', 'Intermediate', 'Advanced', 'Expert']
                current_idx = levels.index(current) if current in levels else 0
                target_idx = levels.index(target) if target in levels else 2
                progress_pct = (current_idx / max(target_idx, 1)) * 100

                html = f'''<div style="background-color: {COLORS["white"]}; padding: 0.75rem; border-radius: 5px; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                        <strong style="color: {COLORS["primary_dark"]};">{skill["skill"]}</strong>
                        <span style="color: {COLORS["secondary"]}; font-size: 0.8rem;">{current} → {target}</span>
                    </div>
                    <div style="background-color: {COLORS["light_accent"]}; border-radius: 5px; height: 6px; margin-bottom: 0.25rem;">
                        <div style="background-color: {COLORS["accent"]}; width: {progress_pct}%; height: 100%; border-radius: 5px;"></div>
                    </div>
                    <p style="color: {COLORS["secondary"]}; font-size: 0.8rem; margin: 0;">{notes}</p>
                </div>'''
                st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="info-box"><p>No career path suggestions yet. Your mentor will add recommendations during your review sessions.</p></div>',
            unsafe_allow_html=True
        )


def get_job_search_keywords():
    """Build job search keywords based on student profile, courses, and mentor feedback."""
    keywords = []

    # From user profile
    user_profile = st.session_state.get('user_profile', {})
    if user_profile.get('interests'):
        keywords.extend(user_profile['interests'])
    if user_profile.get('skills_text'):
        keywords.append(user_profile['skills_text'][:50])

    # From completed courses
    completed = st.session_state.get('completed_courses', {})
    for course in completed.values():
        keywords.append(course.get('name', ''))

    # From career path
    career_path = st.session_state.get('career_path', {})
    if career_path.get('target_roles'):
        keywords.extend(career_path['target_roles'])

    # From skills to develop
    if career_path.get('skills_to_develop'):
        for skill in career_path['skills_to_develop']:
            keywords.append(skill.get('skill', ''))

    return keywords


def get_sample_jobs(keywords):
    """Get sample job listings based on keywords. In production, this would search real job boards."""
    # Sample jobs that would be returned from a real search
    all_jobs = [
        {
            'title': 'Junior Motion Designer',
            'company': 'Creative Studios Inc.',
            'location': 'Los Angeles, CA (Hybrid)',
            'posted': '2 days ago',
            'url': 'https://www.linkedin.com/jobs/view/junior-motion-designer',
            'description': 'Looking for a creative motion designer to join our team. Experience with After Effects and Cinema 4D preferred.',
            'match_reasons': ['Motion Graphics', 'After Effects'],
            'salary': '$45,000 - $60,000'
        },
        {
            'title': 'Video Editor',
            'company': 'Digital Media Agency',
            'location': 'New York, NY (Remote)',
            'posted': '1 day ago',
            'url': 'https://www.linkedin.com/jobs/view/video-editor',
            'description': 'Edit video content for social media and marketing campaigns. Premiere Pro expertise required.',
            'match_reasons': ['Video Editing', 'Social Media Content'],
            'salary': '$40,000 - $55,000'
        },
        {
            'title': 'Junior Animator',
            'company': 'Animation House',
            'location': 'Vancouver, BC (On-site)',
            'posted': '3 days ago',
            'url': 'https://www.linkedin.com/jobs/view/junior-animator',
            'description': '2D/3D animation for commercials and short films. Looking for creative storytellers.',
            'match_reasons': ['Animation', 'Storytelling'],
            'salary': '$50,000 - $65,000'
        },
        {
            'title': 'VFX Artist Intern',
            'company': 'Film Production Co.',
            'location': 'Atlanta, GA (On-site)',
            'posted': '5 days ago',
            'url': 'https://www.linkedin.com/jobs/view/vfx-artist-intern',
            'description': 'Internship opportunity for aspiring VFX artists. Learn compositing and visual effects.',
            'match_reasons': ['Visual Effects', 'Compositing'],
            'salary': 'Paid Internship'
        },
        {
            'title': 'Content Creator',
            'company': 'Social Brand Agency',
            'location': 'Remote',
            'posted': '1 day ago',
            'url': 'https://www.linkedin.com/jobs/view/content-creator',
            'description': 'Create engaging video content for multiple platforms. TikTok and Instagram experience a plus.',
            'match_reasons': ['Social Media Content', 'Video Production'],
            'salary': '$35,000 - $50,000'
        },
        {
            'title': 'Graphic Designer / Video Editor',
            'company': 'Marketing Firm',
            'location': 'Chicago, IL (Hybrid)',
            'posted': '4 days ago',
            'url': 'https://www.linkedin.com/jobs/view/graphic-designer-video-editor',
            'description': 'Hybrid role creating both static and video content for clients. Adobe Suite proficiency required.',
            'match_reasons': ['Video Editing', 'Graphic Design'],
            'salary': '$45,000 - $60,000'
        },
        {
            'title': 'Motion Graphics Artist',
            'company': 'Broadcast Network',
            'location': 'Miami, FL (On-site)',
            'posted': '2 days ago',
            'url': 'https://www.linkedin.com/jobs/view/motion-graphics-artist',
            'description': 'Create on-air graphics and promos for TV network. Broadcast experience preferred.',
            'match_reasons': ['Motion Graphics', 'Broadcast & TV'],
            'salary': '$55,000 - $75,000'
        },
        {
            'title': 'Junior Film Editor',
            'company': 'Independent Film Studio',
            'location': 'Austin, TX (On-site)',
            'posted': '1 week ago',
            'url': 'https://www.linkedin.com/jobs/view/junior-film-editor',
            'description': 'Edit indie films and documentaries. DaVinci Resolve and color grading skills valued.',
            'match_reasons': ['Film & Cinema', 'Documentary'],
            'salary': '$40,000 - $55,000'
        },
        {
            'title': 'Freelance Animator',
            'company': 'Game Development Studio',
            'location': 'Remote',
            'posted': '3 days ago',
            'url': 'https://www.linkedin.com/jobs/view/freelance-animator',
            'description': 'Create character animations for mobile games. 2D animation and rigging skills needed.',
            'match_reasons': ['Animation', 'Game Cinematics'],
            'salary': '$30 - $50/hour'
        },
        {
            'title': 'Video Production Assistant',
            'company': 'Corporate Media Team',
            'location': 'Seattle, WA (On-site)',
            'posted': '6 days ago',
            'url': 'https://www.linkedin.com/jobs/view/video-production-assistant',
            'description': 'Support video production for corporate communications. Great entry-level opportunity.',
            'match_reasons': ['Corporate Video', 'Video Production'],
            'salary': '$35,000 - $45,000'
        },
    ]

    # Score jobs based on keyword matches
    scored_jobs = []
    for job in all_jobs:
        score = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in job['title'].lower():
                score += 3
            if keyword_lower in job['description'].lower():
                score += 2
            for reason in job['match_reasons']:
                if keyword_lower in reason.lower():
                    score += 2
        scored_jobs.append((score, job))

    # Sort by score and return top 10
    scored_jobs.sort(key=lambda x: x[0], reverse=True)
    return [job for _, job in scored_jobs[:10]]


def render_jobs_page():
    """Render the jobs recommendation page."""
    init_course_tracking()
    init_mentor_reviews()

    st.markdown("""
        <div class="main-header">
            <h1>Job Recommendations</h1>
            <p>Based on your skills, completed courses, and mentor feedback</p>
        </div>
    """, unsafe_allow_html=True)

    # Get search keywords
    keywords = get_job_search_keywords()

    # Show what we're searching for
    user_profile = st.session_state.get('user_profile', {})
    career_path = st.session_state.get('career_path', {})
    completed = st.session_state.get('completed_courses', {})

    with st.expander("Your Job Search Profile", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Interests:** {', '.join(user_profile.get('interests', ['Not set']))}")
            st.markdown(f"**Experience Level:** {user_profile.get('experience_level', 'Not set')}")
            if completed:
                st.markdown(f"**Completed Courses:** {len(completed)}")

        with col2:
            if career_path.get('target_roles'):
                st.markdown(f"**Target Roles:** {', '.join(career_path['target_roles'])}")
            if career_path.get('skills_to_develop'):
                skills = [s['skill'] for s in career_path['skills_to_develop'][:3]]
                st.markdown(f"**Developing Skills:** {', '.join(skills)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Job search
    st.markdown("<h3 class='section-header'>Recommended Jobs</h3>", unsafe_allow_html=True)

    with st.spinner("Searching for jobs matching your profile..."):
        jobs = get_sample_jobs(keywords)

    if jobs:
        st.markdown(
            f'<p style="color: {COLORS["secondary"]}; margin-bottom: 1rem;">Found {len(jobs)} jobs matching your profile</p>',
            unsafe_allow_html=True
        )

        for idx, job in enumerate(jobs):
            # Match reasons as tags
            match_tags = " ".join([
                f'<span style="background-color: {COLORS["light_accent"]}; color: {COLORS["mid_accent"]}; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.75rem; margin-right: 0.25rem;">{reason}</span>'
                for reason in job.get('match_reasons', [])
            ])

            html = f'''<div style="background-color: {COLORS["white"]}; padding: 1.25rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid {COLORS["primary_dark"]}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div>
                        <h4 style="color: {COLORS["primary_dark"]}; margin: 0 0 0.25rem 0;">
                            <a href="{job["url"]}" target="_blank" style="color: {COLORS["primary_dark"]}; text-decoration: none;">{job["title"]}</a>
                        </h4>
                        <p style="color: {COLORS["text_dark"]}; margin: 0; font-weight: 500;">{job["company"]}</p>
                    </div>
                    <span style="background-color: {COLORS["light_accent"]}; color: {COLORS["primary_dark"]}; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem;">{job["posted"]}</span>
                </div>
                <p style="color: {COLORS["secondary"]}; margin: 0.25rem 0; font-size: 0.9rem;">{job["location"]} | {job.get("salary", "Salary not listed")}</p>
                <p style="color: {COLORS["text_dark"]}; margin: 0.75rem 0; font-size: 0.9rem;">{job["description"]}</p>
                <div style="margin-top: 0.5rem;">
                    <span style="color: {COLORS["secondary"]}; font-size: 0.8rem;">Matches: </span>{match_tags}
                </div>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([2, 1, 1])
            with col3:
                st.link_button("Apply Now", job["url"], use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="info-box"><p>No jobs found matching your profile. Try completing more courses or updating your skills.</p></div>',
            unsafe_allow_html=True
        )

    # Tips section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>Job Search Tips</h3>", unsafe_allow_html=True)

    tips = [
        "Complete more courses to strengthen your profile and unlock more opportunities",
        "Build a portfolio showcasing your best work from completed projects",
        "Follow your mentor's career path suggestions to develop in-demand skills",
        "Network with industry professionals through LinkedIn and local meetups",
        "Apply to internships to gain real-world experience"
    ]

    for tip in tips:
        st.markdown(f'''
            <div style="background-color: {COLORS["light_accent"]}; padding: 0.75rem; border-radius: 5px; margin-bottom: 0.5rem; display: flex; align-items: center;">
                <span style="color: {COLORS["primary_dark"]}; margin-right: 0.75rem;">&#10003;</span>
                <span style="color: {COLORS["text_dark"]};">{tip}</span>
            </div>
        ''', unsafe_allow_html=True)

    # Navigation buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Recommendations", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()
    with col2:
        pass
    with col3:
        if st.button("View My Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()


def main():
    """Main application entry point."""
    # Page configuration - must be first Streamlit command
    st.set_page_config(
        page_title=APP_CONFIG["title"],
        page_icon=APP_CONFIG["page_icon"],
        layout=APP_CONFIG["layout"],
        initial_sidebar_state="expanded"
    )

    apply_global_styles()

    # Check authentication
    if not is_authenticated():
        render_login_page()
        return

    # Render sidebar
    render_sidebar()

    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "main"

    # Get Databricks client from environment variables
    client = get_databricks_client()

    # Page routing
    if st.session_state.current_page == "profile":
        render_profile_page()
    elif st.session_state.current_page == "jobs":
        render_jobs_page()
    elif st.session_state.get('form_submitted', False):
        render_recommendations(client)
    else:
        render_skills_form()


if __name__ == "__main__":
    main()

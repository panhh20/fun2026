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

        /* Sidebar profile button styling */
        [data-testid="stSidebar"] button[kind="secondary"]:first-of-type {{
            background-color: {COLORS['secondary']} !important;
            color: {COLORS['white']} !important;
            border-radius: 50% !important;
            width: 80px !important;
            height: 80px !important;
            font-size: 2rem !important;
            margin: 0 auto !important;
            display: block !important;
            border: none !important;
            padding: 0 !important;
        }}
        [data-testid="stSidebar"] button[kind="secondary"]:first-of-type:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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

        # Profile button (clicking navigates to profile page)
        if st.button(
            f"{username[0].upper() if username else 'U'}",
            key="profile_btn",
            help="Click to view your profile",
            use_container_width=False
        ):
            st.session_state.current_page = "profile"
            st.rerun()

        tracked_count = len(st.session_state.get('tracked_courses', {}))
        completed_count = len(st.session_state.get('completed_courses', {}))

        st.markdown(f"""
            <p style='color: {COLORS["light_accent"]}; margin: 0; text-align: center;'>
                Logged in as: <strong>{username}</strong>
            </p>
            <p style='color: {COLORS["light_accent"]}; margin: 0.5rem 0 0 0; text-align: center; font-size: 0.8rem;'>
                {tracked_count} in progress | {completed_count} completed
            </p>
            <p style='color: {COLORS["secondary"]}; margin: 0.25rem 0 0 0; text-align: center; font-size: 0.75rem;'>
                Click avatar to view profile
            </p>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Logout button
        if st.button("Logout", use_container_width=True):
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
            st.markdown("""
                <div class="info-box">
                    Using demo recommendations. Configure Databricks in the sidebar for personalized AI recommendations.
                </div>
            """, unsafe_allow_html=True)
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
        pass
    with col3:
        tracked_count = len(st.session_state.get('tracked_courses', {}))
        completed_count = len(st.session_state.get('completed_courses', {}))
        if st.button(f"My Courses ({tracked_count + completed_count})", use_container_width=True):
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
                            st.success(f"Added '{course['name'][:30]}...' to your tracker!")
                            st.rerun()
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
                            st.success(f"Added '{course['name'][:30]}...' to your tracker!")
                            st.rerun()

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
    """Render the user profile page with course tracker."""
    init_course_tracking()
    username = get_current_user()

    st.markdown(f"""
        <div class="main-header">
            <h1>{username}'s Profile</h1>
            <p>Track your learning journey and achievements</p>
        </div>
    """, unsafe_allow_html=True)

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
                    uploaded_file = st.file_uploader(
                        f"Upload certificate for {course['name'][:30]}...",
                        type=['pdf', 'png', 'jpg', 'jpeg'],
                        key=f"cert_{course_id[:20]}"
                    )
                with col2:
                    if st.button("Mark Complete", key=f"complete_{course_id[:20]}", use_container_width=True):
                        cert_data = None
                        if uploaded_file:
                            cert_data = {
                                'filename': uploaded_file.name,
                                'type': uploaded_file.type,
                                'size': uploaded_file.size
                            }
                        mark_course_complete(course_id, cert_data)
                        st.success(f"Congratulations! '{course['name']}' marked as complete!")
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

    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Back to Recommendations", use_container_width=True):
            st.session_state.current_page = "main"
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
    elif st.session_state.get('form_submitted', False):
        render_recommendations(client)
    else:
        render_skills_form()


if __name__ == "__main__":
    main()

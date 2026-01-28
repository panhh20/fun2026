# Authentication logic for Better Youth Creative Lab

import streamlit as st
import os
from config import DEMO_CREDENTIALS, COLORS

# Logo path
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")


def apply_auth_styles():
    """Apply custom CSS styles for the authentication page."""
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
        .login-container {{
            background-color: {COLORS['white']};
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: auto;
        }}
        .login-header {{
            color: {COLORS['primary_dark']};
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        .stButton > button {{
            background-color: {COLORS['primary_dark']};
            color: {COLORS['white']};
            width: 100%;
            padding: 0.5rem;
            border: none;
            border-radius: 5px;
            font-weight: bold;
        }}
        .stButton > button:hover {{
            background-color: {COLORS['mid_accent']};
        }}
        .demo-info {{
            background-color: {COLORS['light_accent']};
            padding: 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: {COLORS['text_dark']};
        }}
        </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables for authentication."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_error' not in st.session_state:
        st.session_state.login_error = None


def authenticate(username: str, password: str) -> bool:
    """
    Authenticate user with provided credentials.

    Args:
        username: The username to authenticate
        password: The password to verify

    Returns:
        True if authentication successful, False otherwise
    """
    if username in DEMO_CREDENTIALS and DEMO_CREDENTIALS[username] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.login_error = None
        return True
    else:
        st.session_state.login_error = "Invalid username or password"
        return False


def logout():
    """Log out the current user and reset session state."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_error = None
    # Clear other session data
    for key in list(st.session_state.keys()):
        if key not in ['authenticated', 'username', 'login_error']:
            del st.session_state[key]


def render_login_page():
    """Render the login page with form and demo credentials info."""
    apply_auth_styles()
    init_session_state()

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Show logo if it exists
        if os.path.exists(LOGO_PATH):
            logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
            with logo_col2:
                st.image(LOGO_PATH, width=375)

        st.markdown(f"""
            <h1 style='color: {COLORS["primary_dark"]}; text-align: center;'>
                Better Youth Creative Lab
            </h1>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Login form
        with st.form("login_form"):
            st.markdown(f"""
                <h3 style='color: {COLORS["mid_accent"]}; text-align: center;'>
                    Welcome
                </h3>
            """, unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if username and password:
                    if authenticate(username, password):
                        st.rerun()
                else:
                    st.session_state.login_error = "Please enter both username and password"

        # Show error if any
        if st.session_state.login_error:
            st.error(st.session_state.login_error)

        # Demo credentials info
        # st.markdown(f"""
        #     <div class="demo-info">
        #         <strong>Demo Credentials:</strong><br>
        #         Username: <code>demo</code> | Password: <code>demo123</code><br>
        #         Username: <code>admin</code> | Password: <code>admin123</code><br>
        #         Username: <code>user</code> | Password: <code>user123</code>
        #     </div>
        # """, unsafe_allow_html=True)


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    init_session_state()
    return st.session_state.authenticated


def get_current_user() -> str:
    """Get the current logged-in username."""
    return st.session_state.username

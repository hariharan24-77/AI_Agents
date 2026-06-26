def load_css():
    return """
    <style>

    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background-color: #DC3545;
        color: white;
    }

    </style>
    """
"""
Modern UI Styles and Themes for Heimdall
"""

# Color Palette
COLORS = {
    # Primary Colors
    'primary': '#667eea',
    'primary_dark': '#5a6fd8',
    'primary_light': '#7c8ef0',
    
    # Secondary Colors
    'secondary': '#764ba2',
    'secondary_dark': '#6a4190',
    'secondary_light': '#8257b0',
    
    # Neutral Colors
    'white': '#ffffff',
    'light_gray': '#f8f9fa',
    'gray': '#6c757d',
    'dark_gray': '#495057',
    'black': '#212529',
    
    # Status Colors
    'success': '#28a745',
    'warning': '#ffc107',
    'error': '#dc3545',
    'info': '#17a2b8',
    
    # AI Status Colors
    'idle': '#95a5a6',
    'listening': '#3498db',
    'processing': '#f39c12',
    'speaking': '#2ecc71'
}

# Light Theme
LIGHT_THEME = {
    'background': COLORS['white'],
    'surface': COLORS['light_gray'],
    'text_primary': COLORS['black'],
    'text_secondary': COLORS['gray'],
    'border': 'rgba(0, 0, 0, 0.1)',
    'shadow': 'rgba(0, 0, 0, 0.1)',
    'accent': COLORS['primary']
}

# Dark Theme
DARK_THEME = {
    'background': '#1a1a1a',
    'surface': '#2d2d2d',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'border': 'rgba(255, 255, 255, 0.1)',
    'shadow': 'rgba(0, 0, 0, 0.3)',
    'accent': COLORS['primary_light']
}

def get_main_window_style(dark_mode=False):
    """Get main window stylesheet"""
    theme = DARK_THEME if dark_mode else LIGHT_THEME
    
    return f"""
    QMainWindow {{
        background: {theme['background']};
        color: {theme['text_primary']};
        font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
    }}
    
    QFrame {{
        background: {theme['surface']};
        border: none;
    }}
    
    QLabel {{
        color: {theme['text_primary']};
        background: transparent;
    }}
    
    QScrollArea {{
        border: none;
        background: {theme['background']};
    }}
    
    QScrollBar:vertical {{
        background: {theme['border']};
        width: 8px;
        border-radius: 4px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background: {theme['text_secondary']};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {theme['text_primary']};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """

def get_sidebar_style(dark_mode=False):
    """Get sidebar stylesheet"""
    theme = DARK_THEME if dark_mode else LIGHT_THEME
    
    return f"""
    QFrame#sidebar {{
        background: {theme['surface']};
        border-right: 1px solid {theme['border']};
    }}
    
    QLabel#title {{
        color: {theme['accent']};
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }}
    
    QPushButton#nav_button {{
        background: transparent;
        color: {theme['text_secondary']};
        border: none;
        border-radius: 8px;
        font-size: 14px;
        text-align: left;
        padding: 15px 20px;
        margin: 2px 0;
    }}
    
    QPushButton#nav_button:hover {{
        background: {theme['border']};
        color: {theme['text_primary']};
    }}
    
    QPushButton#nav_button:checked {{
        background: rgba({theme['accent'].replace('#', '')}, 0.1);
        color: {theme['accent']};
        font-weight: 500;
    }}
    """

def get_chat_style(dark_mode=False):
    """Get chat area stylesheet"""
    theme = DARK_THEME if dark_mode else LIGHT_THEME
    
    return f"""
    QFrame#chat_message_user {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
        border-radius: 15px;
        color: white;
        padding: 10px 15px;
        margin: 5px 50px 5px 0;
    }}
    
    QFrame#chat_message_ai {{
        background: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 15px;
        color: {theme['text_primary']};
        padding: 10px 15px;
        margin: 5px 0 5px 50px;
    }}
    
    QLabel#avatar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
        border-radius: 20px;
        color: white;
        font-weight: bold;
        font-size: 16px;
    }}
    
    QLineEdit#message_input {{
        border: 2px solid {theme['border']};
        border-radius: 25px;
        padding: 0 20px;
        font-size: 14px;
        background: {theme['surface']};
        color: {theme['text_primary']};
    }}
    
    QLineEdit#message_input:focus {{
        border: 2px solid {theme['accent']};
        background: {theme['background']};
    }}
    """

def get_button_style(primary=False, dark_mode=False):
    """Get button stylesheet"""
    theme = DARK_THEME if dark_mode else LIGHT_THEME
    
    if primary:
        return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
            color: white;
            border: none;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            padding: 0 20px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary_dark']}, stop:1 {COLORS['secondary_dark']});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary_dark']}, stop:1 {COLORS['secondary_dark']});
            transform: translateY(1px);
        }}
        """
    else:
        return f"""
        QPushButton {{
            background: {theme['surface']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 20px;
            font-size: 14px;
            padding: 0 20px;
        }}
        QPushButton:hover {{
            background: {theme['border']};
            border: 1px solid {theme['text_secondary']};
        }}
        QPushButton:pressed {{
            background: {theme['text_secondary']};
            transform: translateY(1px);
        }}
        """

def get_status_indicator_style(status, dark_mode=False):
    """Get status indicator stylesheet"""
    color = COLORS.get(status, COLORS['idle'])
    
    return f"""
    QLabel {{
        background: {color};
        border-radius: 6px;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }}
    """

def get_header_style(dark_mode=False):
    """Get header stylesheet"""
    theme = DARK_THEME if dark_mode else LIGHT_THEME
    
    return f"""
    QFrame#header {{
        background: {theme['background']};
        border-bottom: 1px solid {theme['border']};
        padding: 0 30px;
    }}
    
    QLabel#header_title {{
        color: {theme['text_primary']};
        font-size: 18px;
        font-weight: bold;
    }}
    """

# Animation Styles
ANIMATIONS = {
    'fade_in': """
        QWidget {
            animation: fadeIn 0.3s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    """,
    
    'slide_in': """
        QWidget {
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    """,
    
    'pulse': """
        QWidget {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    """
}

# Responsive Breakpoints
BREAKPOINTS = {
    'mobile': 480,
    'tablet': 768,
    'desktop': 1024,
    'large': 1200
}
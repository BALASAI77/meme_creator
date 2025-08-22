import os
import streamlit as st
import pandas as pd
import langid
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import psycopg2
from psycopg2 import pool
import streamlit as st_version_check

# Custom CSS for enhanced UI
st.markdown("""
    <style>
        .stApp {
            background-color: #f0f2f6;
            font-family: 'Arial', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton > button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            transition: background-color 0.2s;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 12px;
            font-size: 16px;
        }
        .stSlider > div > div > div {
            background-color: #ddd;
        }
        .stSuccess {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
        }
        .stError {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
        }
        .image-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }
        .image-card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            padding: 10px;
            text-align: center;
            width: 180px;
            transition: transform 0.2s;
        }
        .image-card:hover {
            transform: scale(1.05);
        }
        .image-card img {
            border-radius: 5px;
            cursor: pointer;
        }
        .stDataFrame {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background-color: white;
        }
        h1, h2, h3 {
            color: #333;
        }
        .stSpinner > div {
            border-color: #4CAF50 transparent transparent transparent;
        }
        .stExpander {
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Check Streamlit version
try:
    st_version = st_version_check.__version__
    if st_version < "0.65.0":
        st.error(f"Streamlit version {st_version} is outdated. Please upgrade to version >=0.65.0 using 'pip install streamlit --upgrade'.")
        st.stop()
except AttributeError:
    st.error("Unable to verify Streamlit version. Ensure Streamlit is installed correctly.")
    st.stop()

# Set page configuration
st.set_page_config(page_title="Desi Meme Creator", page_icon="😂", layout="wide")

# App title
st.title("Desi Meme Creator")
st.markdown("Create personalized memes with Indian language support and build your own corpus!", unsafe_allow_html=True)

# Language code to name mapping
language_map = {
    'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali', 'mr': 'Marathi',
    'gu': 'Gujarati', 'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi', 'ur': 'Urdu',
    'or': 'Odia', 'as': 'Assamese', 'sat': 'Santali', 'en': 'English'
}

# Font mapping for Indian scripts
font_map = {
    'Hindi': 'NotoSansDevanagari-Regular.ttf',
    'Marathi': 'NotoSansDevanagari-Regular.ttf',
    'Tamil': 'NotoSansTamil-Regular.ttf',
    'Telugu': 'NotoSansTelugu-Regular.ttf',
    'Bengali': 'NotoSansBengali-Regular.ttf',
    'Odia': 'NotoSansOriya-Regular.ttf',
    'Gujarati': 'NotoSansGujarati-Regular.ttf',
    'Kannada': 'NotoSansKannada-Regular.ttf',
    'Malayalam': 'NotoSansMalayalam-Regular.ttf',
    'Punjabi': 'NotoSansGurmukhi-Regular.ttf',
    'Urdu': 'NotoSansArabic-Regular.ttf',
    'Assamese': 'NotoSansBengali-Regular.ttf',
    'Santali': 'NotoSansOlChiki-Regular.ttf',
    'English': 'NotoSans-Regular.ttf',
    'Unknown': 'NotoSans-Regular.ttf'
}

# Download fonts
font_urls = {
    'NotoSansDevanagari-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf',
    'NotoSansTamil-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Regular.ttf',
    'NotoSansTelugu-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTelugu/NotoSansTelugu-Regular.ttf',
    'NotoSansBengali-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf',
    'NotoSansOriya-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansOriya/NotoSansOriya-Regular.ttf',
    'NotoSansGujarati-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansGujarati/NotoSansGujarati-Regular.ttf',
    'NotoSansKannada-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Regular.ttf',
    'NotoSansMalayalam-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansMalayalam/NotoSansMalayalam-Regular.ttf',
    'NotoSansGurmukhi-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansGurmukhi/NotoSansGurmukhi-Regular.ttf',
    'NotoSansArabic-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf',
    'NotoSansOlChiki-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansOlChiki/NotoSansOlChiki-Regular.ttf',
    'NotoSans-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf'
}

for font_file, url in font_urls.items():
    if not os.path.exists(font_file):
        try:
            response = requests.get(url)
            with open(font_file, "wb") as f:
                f.write(response.content)
        except Exception as e:
            st.warning(f"Error downloading font {font_file}: {str(e)}. Using default font.")

# Database connection pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    if db_pool:
        st.success("Connected to PostgreSQL database!")
except Exception as e:
    st.error(f"Error connecting to database: {str(e)}")
    st.stop()

# Initialize database table
def init_db():
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meme_corpus (
                id SERIAL PRIMARY KEY,
                language VARCHAR(50),
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        db_pool.putconn(conn)
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        st.stop()

init_db()

# Function to add text with outline
def draw_text_with_outline(draw, text, x, y, font, fill_color="white", outline_color="black"):
    try:
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=fill_color)
    except Exception as e:
        st.error(f"Error rendering text on image: {str(e)}")
        st.stop()

# Function to create meme
def create_meme(image_input, text, font_size, language_name):
    try:
        img = Image.open(image_input) if isinstance(image_input, str) else Image.open(image_input)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        draw = ImageDraw.Draw(img)
        
        font_file = font_map.get(language_name, 'NotoSans-Regular.ttf')
        try:
            font = ImageFont.truetype(font_file, font_size)
        except Exception:
            font = ImageFont.load_default()
            st.warning(f"Font {font_file} not found. Using default font.")
        
        img_width, img_height = img.size
        text_width = draw.textlength(text.upper(), font=font)
        text_height = font_size
        x = (img_width - text_width) // 2
        y = img_height - text_height - 10
        draw_text_with_outline(draw, text.upper(), x, y, font)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return img_byte_arr
    except Exception as e:
        st.error(f"Error creating meme: {str(e)}")
        return None

# Function to detect language
def detect_language(text):
    try:
        if len(text.strip()) < 5:
            return "English"
        lang_code, confidence = langid.classify(text)
        if confidence > 0 or lang_code in language_map:
            return language_map.get(lang_code, "Unknown")
        return "English"
    except Exception as e:
        st.error(f"Error detecting language: {str(e)}")
        return "Unknown"

# Function to save text to database
def save_to_db(language, text):
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO meme_corpus (language, text) VALUES (%s, %s)",
            (language, text)
        )
        conn.commit()
        cursor.close()
        db_pool.putconn(conn)
        st.success(f"Text saved in {language} column of the database!")
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")

# Function to retrieve corpus
def get_corpus():
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("SELECT language, text, created_at FROM meme_corpus ORDER BY created_at DESC")
        df = pd.DataFrame(cursor.fetchall(), columns=['Language', 'Text', 'Created At'])
        cursor.close()
        db_pool.putconn(conn)
        return df
    except Exception as e:
        st.error(f"Error retrieving corpus: {str(e)}")
        return pd.DataFrame()

# Initialize session state for selected image and image name
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'selected_image_name' not in st.session_state:
    st.session_state.selected_image_name = None

# Sidebar for inputs
with st.sidebar:
    st.header("Create Your Meme")
    st.markdown("---")
    
    # Image input selection
    image_input_option = st.radio("Choose Image Input", ("Select Predefined Image", "Upload Custom Image"))

    # Predefined images for selection
    image_options = {
        "Meme 1": "images/meme1.jpg",
        "Meme 2": "images/meme2.jpg",
        "Meme 3": "images/meme3.jpg",
        "Meme 4": "images/meme4.jpg",
        "Meme 5": "images/meme5.jpg",
        "Meme 6": "images/meme6.jpg",
        "Meme 7": "images/meme7.jpg",
        "Meme 8": "images/meme8.jpg",
        "Meme 9": "images/meme9.jpg",
        "Meme 10": "images/meme10.jpg"
    }

    if image_input_option == "Select Predefined Image":
        st.subheader("Select a Meme Image")
        # Display images in a grid with custom styling
        cols = st.columns(2)  # Adjusted to 2 columns for better sidebar fit
        for idx, (img_name, img_path) in enumerate(image_options.items()):
            with cols[idx % 2]:
                try:
                    img = Image.open(img_path)
                    st.markdown(f'<div class="image-card">', unsafe_allow_html=True)
                    st.image(img, caption=img_name, use_container_width=True)
                    if st.button(f"Select {img_name}", key=f"select_{img_name}"):
                        st.session_state.selected_image = img_path
                        st.session_state.selected_image_name = img_name
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Error loading image {img_name}: {str(e)}")

        # Display confirmation message if a predefined image is selected
        if st.session_state.selected_image_name:
            st.success(f"{st.session_state.selected_image_name} is selected")
    else:
        st.subheader("Upload Your Image")
        uploaded_image = st.file_uploader("Upload a meme image (JPG/PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            st.session_state.selected_image = uploaded_image
            st.session_state.selected_image_name = None  # Reset for uploaded images
            st.success("Image uploaded successfully!")

    # Text input
    meme_text = st.text_input("Meme Caption (in any Indian language or English)", placeholder="e.g., मजेदार मीम, நகைச்சுவை")

    # Font size slider
    font_size = st.slider("Font Size", 20, 100, 50)

    # Generate meme button
    if st.button("Generate Meme"):
        if st.session_state.selected_image is not None and meme_text:
            with st.spinner("Creating meme and detecting language..."):
                language_name = detect_language(meme_text)
                meme_image = create_meme(st.session_state.selected_image, meme_text, font_size, language_name)
                if meme_image:
                    try:
                        st.subheader("Generated Meme")
                    except AttributeError:
                        st.markdown("## Generated Meme")
                    st.image(meme_image, caption="Your Meme", use_container_width=True)
                    
                    st.download_button(
                        label="Download Meme",
                        data=meme_image,
                        file_name="meme.png",
                        mime="image/png"
                    )
                
                    try:
                        st.subheader("Detected Language")
                    except AttributeError:
                        st.markdown("## Detected Language")
                    st.write(language_name)

                    save_to_db(language_name, meme_text)
        else:
            st.error("Please select or upload an image and enter a caption to generate a meme.")

# Clear database button
if st.button("Clear Database"):
    clear_db()

# Display corpus
df = get_corpus()
if not df.empty:
    try:
        st.subheader("Current Corpus")
    except AttributeError:
        st.markdown("## Current Corpus")
    st.dataframe(df)
else:            
    st.write("Corpus is empty.")

# Example inputs
try:
    st.subheader("Example Inputs")
except AttributeError:
    st.markdown("## Example Inputs")
st.write("""
- hiii (English)
- मजेदार मीम (Hindi: Funny meme)
- நகைச்சுவை (Tamil: Humor)
- ମଜାରେ ମ୶ (Odia: Funny meme)
- হাসিখুশি (Bengali: Happy)
- తమాషా మీమ్ (Telugu: Funny meme)
""")

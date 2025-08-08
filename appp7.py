import os
import streamlit as st
import pandas as pd
from langdetect import detect, LangDetectException
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import psycopg2
from psycopg2 import pool
import streamlit as st_version_check

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
st.set_page_config(page_title="Desi Meme Creator", page_icon="😂")

# App title and subheader
st.title("Desi Meme Creator")
try:
    st.subheader("Select an image and enter text to create a meme. The text's language will be detected and stored in a database.")
except AttributeError:
    st.markdown("## Select an image and enter text to create a meme. The text's language will be detected and stored in a database.")

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
def create_meme(image, text, font_size, language_name):
    try:
        img = Image.open(image)
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
        lang_code = detect(text)
        return language_map.get(lang_code, "Unknown")
    except LangDetectException as e:
        st.error(f"Error detecting language: {str(e)}")
        return "Unknown"
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

# Display images in a grid (2 rows of 5 columns)
st.subheader("Select a Meme Image")
# First row
cols1 = st.columns(5)  # 5 columns for first row
for idx, (img_name, img_path) in enumerate(list(image_options.items())[:5]):
    try:
        with cols1[idx]:
            img = Image.open(img_path)
            st.image(img, caption=img_name, use_column_width=True)
            if st.button(f"Select {img_name}", key=f"select_{img_name}"):
                selected_image = img_path
    except Exception as e:
        st.warning(f"Error loading image {img_name}: {str(e)}")

# Second row
cols2 = st.columns(5)  # 5 columns for second row
for idx, (img_name, img_path) in enumerate(list(image_options.items())[5:]):
    try:
        with cols2[idx]:
            img = Image.open(img_path)
            st.image(img, caption=img_name, use_column_width=True)
            if st.button(f"Select {img_name}", key=f"select_{img_name}"):
                selected_image = img_path
    except Exception as e:
        st.warning(f"Error loading image {img_name}: {str(e)}")

# Text input
meme_text = st.text_input("Meme Caption (in any Indian language or English)", placeholder="e.g., मजेदार मीम, நகைச்சுவை")

# Font size slider
font_size = st.slider("Font Size", 20, 100, 50)

# Generate meme button
if st.button("Generate Meme"):
    if 'selected_image' in locals() and selected_image is not None and meme_text:
        with st.spinner("Creating meme and detecting language..."):
            language_name = detect_language(meme_text)
            meme_image = create_meme(selected_image, meme_text, font_size, language_name)
            if meme_image:
                try:
                    st.subheader("Generated Meme")
                except AttributeError:
                    st.markdown("## Generated Meme")
                st.image(meme_image, caption="Your Meme", use_column_width=True)
                
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
        st.error("Please select an image and enter a caption to generate a meme.")

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

import os
import streamlit as st
import pandas as pd
from langdetect import detect, LangDetectException
from PIL import Image, ImageDraw, ImageFont
import io
import requests
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

# Set page configuration for the Desi Meme Creator
st.set_page_config(page_title="Desi Meme Creator", page_icon="😂")

# App title and subheader (with fallback)
st.title("Desi Meme Creator")
try:
    st.subheader("Upload an image and enter text to create a meme. The text's language will be detected and stored in a corpus.")
except AttributeError:
    st.markdown("## Upload an image and enter text to create a meme. The text's language will be detected and stored in a corpus.")

# Language code to name mapping for Indian languages and English
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
    'Assamese': 'NotoSansBengali-Regular.ttf',  # Assamese uses Bengali script
    'Santali': 'NotoSansOlChiki-Regular.ttf',
    'English': 'NotoSans-Regular.ttf',
    'Unknown': 'NotoSans-Regular.ttf'
}

# Download fonts for Indian scripts
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

# Function to add text with outline for visibility
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
        
        # Select font based on language
        font_file = font_map.get(language_name, 'NotoSans-Regular.ttf')
        try:
            font = ImageFont.truetype(font_file, font_size)
        except Exception:
            font = ImageFont.load_default()
            st.warning(f"Font {font_file} not found. Using default font (may not support Indian scripts well).")
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Calculate text size and position
        text_width = draw.textlength(text.upper(), font=font)
        text_height = font_size  # Approximate height
        x = (img_width - text_width) // 2
        y = img_height - text_height - 10  # Bottom placement
        
        # Draw text with outline
        draw_text_with_outline(draw, text.upper(), x, y, font)
        
        # Save meme to bytes
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
        if len(text.strip()) < 5:  # Handle short texts
            return "English"
        lang_code = detect(text)
        return language_map.get(lang_code, "Unknown")
    except LangDetectException as e:
        st.error(f"Error detecting language: {str(e)}")
        return "Unknown"
    except Exception as e:
        st.error(f"Error detecting language: {str(e)}")
        return "Unknown"

# Initialize CSV file for corpus storage (do not clear to retain previous responses)
csv_file = "meme_corpus.csv"
if not os.path.exists(csv_file):
    try:
        pd.DataFrame({'Unknown': []}).to_csv(csv_file, index=False)
    except Exception as e:
        st.error(f"Error creating CSV file: {str(e)}")
        st.stop()

# File uploader for meme image
uploaded_image = st.file_uploader("Upload a meme image (JPG/PNG)", type=["jpg", "jpeg", "png"])

# Text input for meme caption
meme_text = st.text_input("Meme Caption (in any Indian language or English)", placeholder="e.g., मजेदार मीम, நகைச்சுவை")

# Font size slider
font_size = st.slider("Font Size", 20, 100, 50)

# Button to generate meme
if st.button("Generate Meme"):
    if uploaded_image is not None and meme_text:
        with st.spinner("Creating meme and detecting language..."):
            # Detect language first to select appropriate font
            language_name = detect_language(meme_text)
            
            # Create meme
            meme_image = create_meme(uploaded_image, meme_text, font_size, language_name)
            if meme_image:
                try:
                    st.subheader("Generated Meme")
                except AttributeError:
                    st.markdown("## Generated Meme")
                st.image(meme_image, caption="Your Meme", use_column_width=True)
                
                # Provide download button
                st.download_button(
                    label="Download Meme",
                    data=meme_image,
                    file_name="meme.png",
                    mime="image/png"
                )
            
            # Display detected language
            try:
                st.subheader("Detected Language")
            except AttributeError:
                st.markdown("## Detected Language")
            st.write(language_name)

            # Store text in CSV
            try:
                df = pd.read_csv(csv_file)
                if not df.columns.size:
                    df = pd.DataFrame({'Unknown': []})
                if language_name not in df.columns:
                    df[language_name] = pd.NA
                new_row = {col: pd.NA for col in df.columns}
                new_row[language_name] = meme_text
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(csv_file, index=False)
                st.success(f"Text saved in {language_name} column of the corpus!")
            except Exception as e:
                st.error(f"Error saving to CSV: {str(e)}")
    else:
        st.error("Please upload an image and enter a caption to generate a meme.")

# Display current corpus
try:
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        if not df.empty and df.columns.size:
            try:
                st.subheader("Current Corpus")
            except AttributeError:
                st.markdown("## Current Corpus")
            st.dataframe(df)
        else:
            st.write("Corpus is empty.")
except Exception as e:
    st.error(f"Error displaying corpus: {str(e)}")

# Example inputs for reference
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
# Desi Meme Creator Project Report

## Overview

Desi Meme Creator is a Streamlit-based web application designed to create memes with captions in Indian languages or English, supporting both predefined and user-uploaded images. The app detects the caption’s language, overlays it on the image, and stores it in a PostgreSQL database to build a multilingual meme corpus.

## Development Process

- **Tech Stack**:
  - **Frontend/Backend**: Streamlit for the web interface and Python logic.
  - **Image Processing**: Pillow for overlaying text on images.
  - **Language Detection**: `langid` library for identifying caption languages.
  - **Database**: PostgreSQL with `psycopg2` for storing captions.
  - **Deployment**: Hosted on Render with a PostgreSQL database.
- **Key Features**:
  - Dual image input: 10 predefined images in a 5x2 grid or user-uploaded JPG/PNG images.
  - Language detection for Indian languages (e.g., Hindi, Tamil) and English.
  - Font size adjustment via a slider.
  - Database storage and display of captions in a corpus table.
  - “Clear Database” button for testing.
  - Confirmation messages for predefined image selection (e.g., “Meme 5 is selected”).
- **Development Timeline**:
  - Initial setup: Streamlit app with predefined image selection and basic meme generation.
  - Iterations: Added custom image upload, fixed `use_column_width` deprecation, resolved image selection issues with `st.session_state`, and implemented database clearing.
  - Finalized: 2025-08-08 with all features stable and deployed on Render.

## Challenges and Solutions

- **Challenge**: Streamlit’s deprecated `use_column_width` caused warnings.
  - **Solution**: Replaced with `use_container_width` to ensure compatibility.
- **Challenge**: Image selection not persisting across Streamlit reruns.
  - **Solution**: Used `st.session_state` to maintain selected image state.
- **Challenge**: Handling multiple Indian language fonts.
  - **Solution**: Downloaded Noto Sans fonts for various scripts (e.g., Devanagari, Tamil) and mapped them to detected languages.
- **Challenge**: Database management for testing.
  - **Solution**: Added a “Clear Database” button to truncate the `meme_corpus` table.

## Outcomes

- **Functionality**: The app successfully creates memes, detects languages, and stores captions, with a user-friendly interface.
- **Performance**: Optimized for Render’s free tier, with images &lt;500KB to reduce load times.
- **Usability**: Intuitive UI with radio buttons for image input, confirmation messages, and a corpus display.
- **Extensibility**: Open to contributions (see CONTRIBUTING.md) for new features like additional fonts or image effects.

## Future Improvements

- Add authentication for the “Clear Database” button to restrict access.
- Support more image formats (e.g., GIF).
- Enhance text styling (e.g., color, position options).
- Implement a search feature for the corpus table.

## Acknowledgments

- Built with guidance from Streamlit and PostgreSQL documentation.
- Fonts sourced from Google Noto Fonts.
- Inspired by open-source meme generator projects.

For more details, see README.md or open an issue on the repository.
# Desi Meme Creator

A web application built with Streamlit that allows users to create memes by selecting from 10 predefined images or uploading their own, adding captions in Indian languages or English, and downloading the result. The app detects the caption’s language and stores it in a PostgreSQL database for a multilingual meme corpus.

## Table of Contents

- Features
- Installation
- Usage
- Contributing
- License
- Contact

## Features

- Choose from 10 predefined meme images or upload a custom JPG/PNG image.
- Add captions in Indian languages (e.g., Hindi, Tamil, Telugu) or English.
- Automatic language detection using `langdetect`.
- Adjust font size for captions with a slider.
- Save captions to a PostgreSQL database.
- View the meme corpus in a table.
- Download generated memes as PNG files.
- Clear the database with a single button.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://code.swecha.org/yourusername/desi-meme-creator.git
   cd desi-meme-creator
   ```

2. **Install Dependencies**:

   - Ensure Python 3.10+ is installed.
   - Install required packages:

     ```bash
     pip install -r requirements.txt
     ```

3. **Set Up PostgreSQL**:

   - Create a PostgreSQL database (e.g., `meme_corpus_db`).
   - Set environment variables for database connection:

     ```bash
     export DB_NAME=meme_corpus_db
     export DB_USER=your_db_user
     export DB_PASSWORD=your_db_password
     export DB_HOST=your_db_host
     export DB_PORT=5432
     ```

4. **Prepare Images**:

   - Place 10 images named `meme1.jpg` to `meme10.jpg` in the `images/` folder.
   - Images should be JPG format, optimized (&lt;500KB each).

5. **Run the App Locally**:

   ```bash
   streamlit run app.py
   ```

   - Access at `http://localhost:8501`.

## Usage

1. **Select or Upload Image**:
   - Choose “Select Predefined Image” to pick from 10 images in a 5x2 grid.
   - Or select “Upload Custom Image” to upload a JPG/PNG file.
2. **Enter Caption**:
   - Input text in any Indian language (e.g., “मजेदार मीम” for Hindi, “நகைச்சுவை” for Tamil) or English.
3. **Adjust Font Size**:
   - Use the slider to set caption font size (20–100).
4. **Generate Meme**:
   - Click “Generate Meme” to create the meme with the caption overlaid.
   - Download the meme as a PNG file.
5. **View Corpus**:
   - Captions and detected languages are saved to the database and displayed in the “Current Corpus” table.
6. **Clear Database**:
   - Click “Clear Database” to remove all stored captions.

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines on how to contribute, including submitting issues and pull requests.

## License

This project is licensed under the MIT License. See LICENSE for details.
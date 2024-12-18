# DYSassist
A text to speech webapp made with flask. 

# DYSassist - "Read with Ease"

DYSassist is a web application that converts text documents (PDF and DOCX) into audiobooks, making reading more accessible for everyone, especially those with dyslexia or other reading challenges.

## Features

- **Secure User Authentication**: Personal account system with signup and login functionality
- **Document Upload**: Support for PDF and DOCX file formats
- **Text-to-Speech Conversion**: High-quality audio conversion using gTTS (Google Text-to-Speech)
- **Audio Playback**: Built-in audio player with download capability
- **Responsive Design**: User-friendly interface that works across devices

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite3
- **Document Processing**: 
  - PyPDF2 for PDF parsing
  - python-docx for DOCX parsing
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. Clone the repository:
console - bash  

    git clone https://github.com/yourusername/dysassist.git
    cd dysassist

2. Install required packages:
console - bash  
    pip install -r requirements.txt

3. Run the application:
console - bash
    python main.py


The application will be available at `http://localhost:5000`

## Usage

1. Create an account or log in
2. Upload your PDF or DOCX document
3. Click "Convert to Audiobook"
4. Listen to or download your audiobook

## Project Structure
console - bash
    dysassist/
    ├── main.py # Main application file
    ├── login.db # SQLite database
    ├── static/ # Static files (CSS, images)
    ├── templates/ # HTML templates
    ├── uploads/ # User uploaded files
    │ └── audio/ # Generated audiobooks
    └── requirements.txt # Project dependencies


## Security Features

- Secure file upload handling
- Session management
- Password protection
- Secure filename handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Text-to-Speech for audio conversion
- Flask framework
- All contributors and supporters of the project
    

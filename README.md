# WhatsApp Chat Analyzer

A web-based tool that provides detailed analytics and insights from WhatsApp chat exports. This tool helps you understand communication patterns, user engagement, and content analysis from your WhatsApp conversations.

Screenshots

![WhatsApp Chat Analyzer Screenshot](screenshots/ss.png?raw=true)
----
----
![WhatsApp Chat Analyzer Screenshot](screenshots/image.png?raw=true)

## Features

- **Basic Statistics**
  - Total message count
  - Number of participants
  - Media message analysis
  - Emoji usage statistics
  - Average response time calculation

- **User Activity Analysis**
  - Messages per user visualization
  - Active hours tracking
  - User engagement patterns
  - Conversation starter/closer analysis

- **Content Analysis**
  - Most used words
  - Popular emoji tracking
  - Word cloud visualization
  - Basic sentiment analysis

- **Time-based Analytics**
  - Time of day activity patterns
  - Message frequency analysis
  - Conversation streak tracking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/itssiddhant/Wanalyzer.git
cd Wanalyzer.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://127.0.0.2:5501`

## Usage

1. Export your WhatsApp chat:
   - Open WhatsApp
   - Go to the desired chat
   - Click on the three dots (⋮) > More > Export chat
   - Choose "Without Media"

2. Upload the exported text file:
   - Click "Choose File" on the web interface
   - Select your exported chat file
   - Click "Analyze"

3. View your analysis results in the interactive dashboard

## Technologies Used

- Frontend:
  - HTML5
  - Tailwind CSS
  - Chart.js for visualizations
  - JavaScript for interactivity

- Backend:
  - Python
  - Flask
  - pandas for data processing
  - NLTK for text analysis
  - TextBlob for sentiment analysis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

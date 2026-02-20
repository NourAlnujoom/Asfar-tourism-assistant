# Asfar - Jordan Tourism Assistant

A full-stack tourism assistant website designed specifically for visitors to Jordan. Asfar provides intelligent trip planning, weather information, crowd predictions, and audio guides for Jordan's most important sites.

## 🌟 Features

- **Intelligent Chatbot**: AI-powered assistant for trip planning, weather info, and hidden gems
- **Audio Guides**: Detailed audio tours of Jordan's top attractions
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **No Authentication Required**: All features are publicly accessible
- **Modern UI**: Clean, beautiful interface with Jordan-themed colors

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python with Flask
- **Styling**: Custom CSS with Google Fonts (Cairo & Poppins)
- **Responsive**: Mobile-first design approach

## 📁 Project Structure

```
Asfar/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── index.html        # Homepage
│   ├── chatbot.html      # Chatbot interface
│   ├── audio-guide.html  # Audio guides page
│   └── help.html         # Help center
└── static/              # Static assets
    ├── css/
    │   └── style.css     # Main stylesheet
    └── js/
        └── chatbot.js    # Chatbot functionality
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   # If you have git installed
   git clone <repository-url>
   cd Asfar
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 How to Use

### Homepage (`/`)
- Full-screen hero section with Jordan background
- General information about Asfar and Jordan
- Navigation to all features
- Call-to-action to start planning

### Chatbot (`/chatbot`)
- Interactive chat interface
- Ask about trip planning, weather, crowds, or hidden gems
- Examples:
  - "Plan a 5-day trip to Jordan"
  - "What's the weather like in Petra?"
  - "Show me hidden gems in Jordan"

### Audio Guide (`/audio-guide`)
- 8 detailed audio guides for Jordan's top sites:
  - Petra - The Rose City
  - Wadi Rum - Valley of the Moon
  - Dead Sea - The Lowest Point on Earth
  - Jerash - The Pompeii of the East
  - Amman Citadel - Heart of the Capital
  - Mount Nebo - Biblical Significance
  - Madaba - City of Mosaics
  - Karak Castle - Crusader Fortress

### Help Center (`/help`)
- Comprehensive FAQ section
- Usage tips and best practices
- Technical support information
- Contact and feedback options

## 🤖 Chatbot Features

The chatbot responds to different types of queries:

### Trip Planning
- Keywords: "trip", "plan", "itinerary", "visit", "go"
- Provides personalized itineraries and recommendations

### Weather & Crowds
- Keywords: "weather", "temperature", "hot", "cold", "crowd", "busy"
- Offers seasonal advice and crowd predictions

### Hidden Gems
- Keywords: "hidden", "gem", "secret", "local", "off the beaten"
- Reveals lesser-known attractions and local favorites

### General Queries
- Default responses for general questions about Jordan

## 🎨 Design Features

- **Jordan-themed Colors**: Green (#2c5530) and earth tones
- **Modern Typography**: Cairo (Arabic-inspired) and Poppins fonts
- **Responsive Layout**: Works on all device sizes
- **Smooth Animations**: Hover effects and transitions
- **Clean Cards**: Rounded corners and subtle shadows

## 🔧 Customization

### Adding New Chatbot Responses
Edit the response arrays in `app.py`:
```python
TRIP_RESPONSES = [
    "Your new trip planning response here",
    # Add more responses...
]
```

### Adding Audio Guides
1. Add new audio files to the static directory
2. Update `templates/audio-guide.html` with new entries
3. Include appropriate images and descriptions

### Styling Changes
Modify `static/css/style.css` to customize:
- Colors and themes
- Layout and spacing
- Typography and fonts
- Animations and effects

## 🌐 Future Enhancements

- **OpenWeatherMap Integration**: Real-time weather data
- **Machine Learning**: Crowd prediction using scikit-learn
- **Multi-language Support**: Arabic and other languages
- **Offline Mode**: Progressive Web App features
- **User Accounts**: Personalized trip planning
- **Real-time Updates**: Live information about sites

## 📱 Mobile Responsiveness

The website is fully responsive and optimized for:
- Desktop computers (1200px+)
- Tablets (768px - 1199px)
- Mobile phones (320px - 767px)

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change the port in app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Module not found errors**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

3. **Audio not playing**
   - Check browser audio settings
   - Ensure internet connection for audio files
   - Try different browsers

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📞 Support

For support or questions:
- Use the chatbot on the website
- Check the Help Center page
- Review the FAQ section

---

**Made with ❤️ for travelers exploring Jordan**

*Asfar - Your Personal Jordan Tourism Assistant* 
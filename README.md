# SmartFarmtrack 🌾

An intelligent farming assistant that combines AI capabilities with agricultural expertise to help farmers make better decisions.

## Features

- 🤖 **AI-Powered Chat Assistant**
  - Natural language processing using Dialogflow
  - Advanced responses with Gemini AI
  - Contextual farming advice and recommendations

- 🌱 **Crop Analysis**
  - Real-time crop health monitoring
  - Disease detection and solutions
  - Growth stage tracking

- ☁️ **Weather Integration**
  - Real-time weather updates
  - Crop-specific weather impact analysis
  - Precipitation forecasting

- 📊 **Resource Management**
  - Water usage optimization
  - Fertilizer scheduling
  - Smart irrigation recommendations

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/QuantumShrey/SmartFarmtrack.git
   cd SmartFarmtrack
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   - Copy `.env.example` to `.env`
   - Add your API keys and credentials:
     - GOOGLE_PROJECT_ID
     - GOOGLE_APPLICATION_CREDENTIALS
     - GEMINI_API_KEY

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   - Open `http://localhost:5000` in your browser
   - Use the chat widget for AI assistance
   - Navigate through different sections using the top menu

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: Google Dialogflow, Google Gemini
- **APIs**: OpenWeatherMap, Sentinel Hub

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

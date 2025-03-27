// Navigation handling
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            navLinks.forEach(l => l.classList.remove('active'));
            e.target.classList.add('active');
        });
    });
});

// Simulated weather data update (to be replaced with actual API calls)
function updateWeather() {
    // This will be replaced with actual API integration
    const weatherData = {
        current: {
            temp: Math.floor(Math.random() * 15) + 20,
            condition: ['Sunny', 'Cloudy', 'Rainy'][Math.floor(Math.random() * 3)]
        },
        forecast: [
            { day: 'Mon', temp: Math.floor(Math.random() * 10) + 20 },
            { day: 'Tue', temp: Math.floor(Math.random() * 10) + 20 },
            { day: 'Wed', temp: Math.floor(Math.random() * 10) + 20 }
        ]
    };

    // Update current weather
    document.querySelector('.temperature').textContent = `${weatherData.current.temp}°C`;
    document.querySelector('.description').textContent = weatherData.current.condition;

    // Update forecast
    const forecastItems = document.querySelectorAll('.forecast-item span:last-child');
    forecastItems.forEach((item, index) => {
        item.textContent = `${weatherData.forecast[index].temp}°C`;
    });
}

// Update weather every 5 minutes
updateWeather();
setInterval(updateWeather, 300000);

// Market price updates simulation
function updateMarketPrices() {
    const prices = document.querySelectorAll('.price-item .trend');
    prices.forEach(price => {
        const change = (Math.random() * 5 - 2.5).toFixed(1);
        const isUp = change > 0;
        price.className = `trend ${isUp ? 'up' : 'down'}`;
        price.innerHTML = `<i class="fas fa-arrow-${isUp ? 'up' : 'down'}"></i> ${Math.abs(change)}%`;
    });
}

// Update market prices every 3 minutes
updateMarketPrices();
setInterval(updateMarketPrices, 180000);

// AI Crop Monitoring Updates
function updateCropMonitoring() {
    // This will be replaced with actual AI API integration
    const cropHealth = Math.floor(Math.random() * 20) + 80; // Random health between 80-100%
    const healthMeter = document.querySelector('.health-meter .meter-fill');
    if (healthMeter) {
        healthMeter.style.width = `${cropHealth}%`;
        healthMeter.textContent = `${cropHealth}%`;
    }

    // Simulate pest detection alerts
    const pestAlert = document.querySelector('.status-item.warning');
    if (pestAlert && Math.random() > 0.7) { // 30% chance of pest alert
        pestAlert.style.display = 'flex';
    } else if (pestAlert) {
        pestAlert.style.display = 'none';
    }
}

// Resource Management Updates
function updateResourceMetrics() {
    // This will be replaced with actual sensor data integration
    const waterUsage = Math.floor(Math.random() * 30) + 50; // Random usage between 50-80%
    const fertilizerLevel = Math.floor(Math.random() * 40) + 10; // Random level between 10-50%

    const waterBar = document.querySelector('.metric:first-child .bar-fill');
    const fertilizerBar = document.querySelector('.metric:last-child .bar-fill');

    if (waterBar) {
        waterBar.style.width = `${waterUsage}%`;
        waterBar.textContent = `${waterUsage}%`;
        waterBar.className = `bar-fill ${waterUsage > 75 ? 'warning' : 'optimal'}`;
    }

    if (fertilizerBar) {
        fertilizerBar.style.width = `${fertilizerLevel}%`;
        fertilizerBar.textContent = `${fertilizerLevel}%`;
        fertilizerBar.className = `bar-fill ${fertilizerLevel < 30 ? 'warning' : 'optimal'}`;
    }

    // Update AI recommendations based on metrics
    const recommendation = document.querySelector('.ai-recommendation p');
    if (recommendation) {
        if (waterUsage > 75) {
            recommendation.textContent = 'AI Suggestion: Reduce irrigation by 15% based on forecasted rainfall';
        } else if (fertilizerLevel < 30) {
            recommendation.textContent = 'AI Suggestion: Schedule fertilizer application within next 48 hours';
        } else {
            recommendation.textContent = 'AI Suggestion: All resources at optimal levels';
        }
    }
}

// Initialize monitoring updates
updateCropMonitoring();
updateResourceMetrics();

// Update monitoring data every 2 minutes
setInterval(() => {
    updateCropMonitoring();
    updateResourceMetrics();
}, 120000);

// Crop Analysis Form Handling
document.getElementById('cropAnalysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading state
    const submitBtn = e.target.querySelector('.submit-btn');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    submitBtn.disabled = true;

    // Gather form data
    const formData = {
        cropType: document.getElementById('cropType').value,
        sowingMonth: document.getElementById('sowingMonth').value,
        soilMoisture: document.getElementById('soilMoisture').value,
        soilPh: document.getElementById('soilPh').value,
        soilType: document.getElementById('soilType').value,
        temperature: document.getElementById('temperature').value,
        rainfall: document.getElementById('rainfall').value,
        humidity: document.getElementById('humidity').value,
        timestamp: new Date().toISOString()
    };

    try {
        // Send data to backend
        const response = await fetch('http://localhost:5000/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // Display recommendations
            const recommendationsPanel = document.getElementById('aiRecommendations');
            const content = recommendationsPanel.querySelector('.recommendation-content');
            const timestamp = recommendationsPanel.querySelector('.timestamp');

            content.innerHTML = marked.parse(data.recommendations.content); // Using marked.js for markdown parsing
            timestamp.textContent = new Date(data.recommendations.timestamp).toLocaleString();
            recommendationsPanel.style.display = 'block';

            // Scroll to recommendations
            recommendationsPanel.scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.error || 'Failed to get recommendations');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to get recommendations. Please try again.');
    } finally {
        // Reset button state
        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;
    }
});

// Save recommendation to local storage
function saveRecommendation() {
    const recommendationsPanel = document.getElementById('aiRecommendations');
    const content = recommendationsPanel.querySelector('.recommendation-content').innerHTML;
    const timestamp = recommendationsPanel.querySelector('.timestamp').textContent;

    const savedRecommendations = JSON.parse(localStorage.getItem('farmtrack_recommendations') || '[]');
    savedRecommendations.push({
        content,
        timestamp,
        savedAt: new Date().toISOString()
    });

    localStorage.setItem('farmtrack_recommendations', JSON.stringify(savedRecommendations));

    // Show success message
    const saveBtn = recommendationsPanel.querySelector('.save-btn');
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved!';
    saveBtn.disabled = true;

    setTimeout(() => {
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    }, 2000);
}

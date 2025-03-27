// API base URL
const API_BASE_URL = 'http://localhost:5000';
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

// Load and display saved recommendations
function loadSavedRecommendations() {
    const savedRecommendations = JSON.parse(localStorage.getItem('farmtrack_recommendations') || '[]');
    const container = document.querySelector('.recommendations-list');
    const template = document.getElementById('recommendation-template');
    
    // Clear existing recommendations
    container.innerHTML = '';
    
    if (savedRecommendations.length === 0) {
        container.innerHTML = '<p>No saved recommendations yet.</p>';
        return;
    }
    
    savedRecommendations.forEach((rec, index) => {
        const card = template.content.cloneNode(true);
        
        // Set the content
        card.querySelector('.timestamp').textContent = new Date(rec.timestamp).toLocaleString();
        card.querySelector('.crop-type').textContent = rec.cropData.cropType;
        card.querySelector('.soil-type').textContent = rec.cropData.soilType;
        card.querySelector('.issues').textContent = rec.cropData.issues;
        card.querySelector('.ai-recommendation').innerHTML = marked.parse(rec.aiRecommendation);
        
        // Add delete button handler
        const deleteBtn = card.querySelector('.delete-btn');
        deleteBtn.onclick = () => deleteSavedRecommendation(index);
        
        container.appendChild(card);
    });
}

// Save a recommendation
function saveRecommendation(recommendation) {
    const savedRecommendations = JSON.parse(localStorage.getItem('farmtrack_recommendations') || '[]');
    savedRecommendations.unshift(recommendation);
    localStorage.setItem('farmtrack_recommendations', JSON.stringify(savedRecommendations));
    
    // Show success message
    const successMessage = document.createElement('div');
    successMessage.className = 'alert alert-success';
    successMessage.textContent = 'Analysis saved successfully!';
    document.body.insertBefore(successMessage, document.body.firstChild);
    
    setTimeout(() => {
        successMessage.remove();
    }, 3000);
}

// Delete a saved recommendation
function deleteSavedRecommendation(index) {
    const savedRecommendations = JSON.parse(localStorage.getItem('farmtrack_recommendations') || '[]');
    savedRecommendations.splice(index, 1);
    localStorage.setItem('farmtrack_recommendations', JSON.stringify(savedRecommendations));
    loadSavedRecommendations();
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error';
    errorDiv.textContent = message;
    document.body.insertBefore(errorDiv, document.body.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Get AI-powered crop analysis
async function getAIAnalysis(cropData) {
    try {
        const prompt = `Analyze the following crop data and provide recommendations:
            Crop Type: ${cropData.cropType}
            Soil Type: ${cropData.soilType}
            Current Issues: ${cropData.issues}`;

        const response = await fetch(`${GEMINI_API_URL}?key=${process.env.GEMINI_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text: prompt }]
                }]
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get AI analysis');
        }

        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    } catch (error) {
        console.error('AI Analysis Error:', error);
        throw error;
    }
}

// Handle form submission
document.getElementById('cropAnalysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const cropData = {
        cropType: form.cropType.value,
        soilType: form.soilType.value,
        issues: form.issues.value,
        timestamp: new Date().toISOString()
    };

    try {
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Analyzing...';

        // Send data to backend for analysis
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cropData)
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Failed to get recommendations');
        }

        // Display the recommendation immediately
        const aiRecommendationsPanel = document.getElementById('aiRecommendations');
        const recommendationContent = aiRecommendationsPanel.querySelector('.recommendation-content');
        const timestamp = aiRecommendationsPanel.querySelector('.timestamp');
        
        recommendationContent.innerHTML = marked.parse(result.recommendations.content);
        timestamp.textContent = new Date().toLocaleString();
        aiRecommendationsPanel.style.display = 'block';

        // Save recommendation
        const recommendation = {
            timestamp: cropData.timestamp,
            cropData,
            aiRecommendation: result.recommendations.content
        };

        // Update saved recommendations list
        saveRecommendation(recommendation);
        loadSavedRecommendations();
        
        // Reset form
        form.reset();
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to analyze crop data. Please try again.');
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
});

// Load saved recommendations when page loads
document.addEventListener('DOMContentLoaded', loadSavedRecommendations);

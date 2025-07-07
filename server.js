const express = require('express');
const app = express();
const PORT = process.env.PORT || 8080;

app.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Tenxsom AI with Vertex AI',
    project: process.env.GOOGLE_CLOUD_PROJECT || 'gen-lang-client-0874689591',
    ai: {
      provider: 'Google Vertex AI',
      region: 'us-east5',
      models: [
        'claude-sonnet-4@20250514',
        'claude-3-5-haiku@20241022', 
        'claude-opus-4@20250514'
      ]
    },
    features: [
      '24/7 Content Generation',
      'YouTube Automation',
      'Multi-platform Posting',
      'Cost Optimization'
    ]
  });
});

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date(),
    vertexAI: true
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Tenxsom AI with Vertex AI running on port ${PORT}`);
});
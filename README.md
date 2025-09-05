# ChefGPT Recipe Generator

A Flask-based web service that generates cooking recipes using a quantized T5 model, optimized for deployment on Azure App Service Basic B1.

## Features

- **Low CPU Usage**: Optimized for Azure App Service Basic B1 with CPU-only PyTorch
- **Quantized Model**: Uses dynamic quantization to reduce memory footprint
- **Efficient Processing**: Thread-safe model loading and inference
- **Health Monitoring**: Built-in health check endpoint
- **Error Handling**: Comprehensive error handling and logging

## API Endpoints

### POST /generate_recipe
Generate a recipe from a text prompt.

**Request Body:**
```json
{
  "prompt": "chicken pasta recipe",
  "max_length": 160,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "generated_recipe": "Recipe text here...",
  "prompt": "chicken pasta recipe",
  "parameters": {
    "max_length": 160,
    "temperature": 0.7
  }
}
```

### GET /health
Check the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": 1234567890.123
}
```

### GET /
Get service information and available endpoints.

## Local Development

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**
   ```bash
   python app.py
   ```

3. **Test the API:**
   ```bash
   curl -X POST http://localhost:5000/generate_recipe \
     -H "Content-Type: application/json" \
     -d '{"prompt": "chicken pasta recipe"}'
   ```


### Performance Optimization

The application is optimized for low CPU usage with the following features:

- **CPU-only PyTorch**: Uses CPU-optimized PyTorch builds
- **Dynamic Quantization**: Reduces model size and inference time
- **Threading**: Non-blocking model loading
- **Memory Management**: Automatic garbage collection
- **Single Worker**: Optimized for Basic B1 tier

### Monitoring

- Check `/health` endpoint for service status


## Model Requirements

The application expects the following files in the `models/` directory:

- `quantized_model_state_dict.pth` - Quantized model weights
- `tokenizer_config.json` - Tokenizer configuration
- `added_tokens.json` - Additional tokens
- `special_tokens_map.json` - Special tokens mapping
- `spiece.model` - SentencePiece model

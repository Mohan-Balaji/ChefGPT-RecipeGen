import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import re
import os
import logging
from flask import Flask, request, jsonify, render_template
import gc
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for model and tokenizer
tokenizer = None
model = None
device = torch.device("cpu")
model_loaded = False
model_lock = threading.Lock()

# Define the path to the model directory
MODEL_DIR = './models'

def clean_text(text):
    """Clean and preprocess input text"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove special characters and digits, keep only letters and spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower().strip()
    return text

def load_model():
    """Load the quantized model and tokenizer"""
    global tokenizer, model, model_loaded
    
    try:
        logger.info("Starting model loading...")
        
        # Load tokenizer
        tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
        logger.info("Tokenizer loaded successfully")
        
        # Load the base T5 model architecture
        model = T5ForConditionalGeneration.from_pretrained('t5-small')
        model.eval()
        logger.info("Base model loaded successfully")
        
        # Apply dynamic quantization for CPU optimization
        quantized_model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )
        
        # Load the quantized state dictionary
        quantized_state_dict_path = os.path.join(MODEL_DIR, 'quantized_model_state_dict.pth')
        if os.path.exists(quantized_state_dict_path):
            quantized_model.load_state_dict(
                torch.load(quantized_state_dict_path, map_location=device)
            )
            model = quantized_model
            logger.info("Quantized model state dictionary loaded successfully")
        else:
            logger.error(f"Quantized state dictionary not found at {quantized_state_dict_path}")
            return False
        
        # Move model to CPU and set to evaluation mode
        model.to(device)
        model.eval()
        
        # Clear cache to free memory
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()
        
        model_loaded = True
        logger.info("Model loading completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model_loaded = False
        return False

def generate_recipe(prompt, max_length=160, temperature=0.7):
    """Generate recipe using the quantized model"""
    if not model_loaded or not model or not tokenizer:
        return "Error: Model not loaded properly"
    
    try:
        # Clean the input prompt
        clean_prompt = clean_text(prompt)
        if not clean_prompt:
            return "Error: Invalid or empty prompt"
        
        # Tokenize input
        inputs = tokenizer(
            clean_prompt, 
            return_tensors='pt', 
            max_length=128,  # Reduced for efficiency
            truncation=True, 
            padding='max_length'
        )
        
        input_ids = inputs['input_ids'].to(device)
        attention_mask = inputs['attention_mask'].to(device)
        
        # Generate with optimized parameters for CPU
        with torch.no_grad():
            output = model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=max_length,
                num_return_sequences=1,
                temperature=temperature,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                early_stopping=True
            )
        
        # Decode the output
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Clean up memory
        del input_ids, attention_mask, output
        gc.collect()
        
        return generated_text
        
    except Exception as e:
        logger.error(f"Error during recipe generation: {e}")
        return f"Error during recipe generation: {str(e)}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'timestamp': time.time()
    })

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe_endpoint():
    """Main recipe generation endpoint"""
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 503
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing "prompt" in request body'}), 400
        
        prompt = data['prompt']
        if not prompt or not isinstance(prompt, str):
            return jsonify({'error': 'Invalid prompt'}), 400
        
        # Optional parameters
        max_length = data.get('max_length', 160)
        temperature = data.get('temperature', 0.7)
        
        # Validate parameters
        max_length = min(max(max_length, 50), 200)  # Limit between 50-200
        temperature = min(max(temperature, 0.1), 1.0)  # Limit between 0.1-1.0
        
        with model_lock:
            generated_recipe = generate_recipe(prompt, max_length, temperature)
        
        return jsonify({
            'generated_recipe': generated_recipe,
            'prompt': prompt,
            'parameters': {
                'max_length': max_length,
                'temperature': temperature
            }
        })
        
    except Exception as e:
        logger.error(f"Error in generate_recipe_endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/', methods=['GET'])
def index():
    """Main page with recipe generation interface"""
    return render_template('index.html', model_loaded=model_loaded)

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'service': 'ChefGPT Recipe Generator',
        'version': '1.0.0',
        'endpoints': {
            'POST /generate_recipe': 'Generate recipe from prompt',
            'GET /health': 'Health check',
            'GET /api': 'This information'
        },
        'model_loaded': model_loaded
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def initialize_app():
    """Initialize the application and load the model"""
    logger.info("Initializing ChefGPT Recipe Generator...")
    
    # Load model in a separate thread to avoid blocking
    def load_model_thread():
        global model_loaded
        with model_lock:
            model_loaded = load_model()
    
    # Start model loading
    model_thread = threading.Thread(target=load_model_thread)
    model_thread.daemon = True
    model_thread.start()
    
    # Wait a bit for model to start loading
    time.sleep(1)
    
    logger.info("Application initialized")

if __name__ == '__main__':
    initialize_app()
    
    # For local development
    app.run(
        debug=False,  # Set to False for production
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        threaded=True
    )

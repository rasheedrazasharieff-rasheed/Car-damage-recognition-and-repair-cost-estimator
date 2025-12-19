import os
import json
from collections import Counter
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)
app.secret_key = 'super_secret_base_key'  # Needed for flash messages

# Configuration
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MODEL_PATH = "models/model weights/best.pt"
PRICES_JSON_PATH = "car_parts_prices.json"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load YOLO Model
try:
    model = YOLO(MODEL_PATH)
    print("YOLO model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load Car Parts Prices from JSON
def load_prices():
    if os.path.exists(PRICES_JSON_PATH):
        with open(PRICES_JSON_PATH, 'r') as f:
            return json.load(f)
    return {}

CAR_DATA = load_prices()

# Helper: Map YOLO class IDs to Part Names
def get_part_name_from_id(class_id):
    # Based on your original code
    class_names = ['Bonnet', 'Bumper', 'Dickey', 'Door', 'Fender', 'Light', 'Windshield']
    if 0 <= class_id < len(class_names):
        return class_names[int(class_id)]
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    estimate_results = None
    detected_image_filename = None
    original_image_filename = None
    selected_brand = ""
    selected_model = ""

    if request.method == 'POST':
        # 1. Get Form Data
        selected_brand = request.form.get('carBrand')
        selected_model = request.form.get('carModel')
        file = request.files.get('image')

        # 2. Validate Inputs
        if not file or not file.filename:
            flash('No image selected.')
        elif not selected_brand or not selected_model:
            flash('Please select both Brand and Model.')
        else:
            # 3. Save Image
            filename = secure_filename(file.filename)
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_base.jpg')
            file.save(original_path)
            original_image_filename = 'uploaded_base.jpg'

            # 4. Run Detection
            if model:
                results = model(original_path)
                detected_objects = results[0].boxes
                class_ids = [int(box.cls.item()) for box in detected_objects]
                class_counts = Counter(class_ids)

                # Save Detected Image
                detected_filename = 'detected_base.jpg'
                detected_path = os.path.join(app.config['UPLOAD_FOLDER'], detected_filename)
                results[0].save(detected_path)
                detected_image_filename = detected_filename

                # 5. Calculate Prices
                estimate_results = calculate_cost(selected_brand, selected_model, class_counts)
            else:
                flash("Model not loaded.")

    # Pass the entire CAR_DATA to template so JS can handle the dropdown logic
    return render_template('index.html', 
                           car_data=CAR_DATA, 
                           estimate=estimate_results,
                           detected_img=detected_image_filename,
                           original_img=original_image_filename,
                           sel_brand=selected_brand,
                           sel_model=selected_model)

def calculate_cost(brand, car_model, class_counts):
    total_bill = 0
    parts_breakdown = []

    # Check if Brand/Model exists in JSON
    if brand in CAR_DATA and car_model in CAR_DATA[brand]:
        model_pricing = CAR_DATA[brand][car_model]

        for class_id, count in class_counts.items():
            part_name = get_part_name_from_id(class_id)
            
            if part_name and part_name in model_pricing:
                price_per_unit = model_pricing[part_name]
                part_total = price_per_unit * count
                total_bill += part_total
                
                parts_breakdown.append({
                    'part': part_name,
                    'count': count,
                    'price_each': price_per_unit,
                    'total': part_total
                })
            elif part_name:
                parts_breakdown.append({
                    'part': part_name,
                    'count': count,
                    'price_each': "N/A",
                    'total': 0
                })
    
    return {'breakdown': parts_breakdown, 'grand_total': total_bill}

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5001)
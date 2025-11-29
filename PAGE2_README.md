# Page 2: Product Input with AI Gap-Filling

## Overview
Page 2 allows users to input product data for LCA assessment in two ways:
1. **Natural Language Input**: Describe your product in plain English, and AI extracts structured data
2. **Structured Form**: Fill in specific fields directly

## Features

### 🤖 AI-Powered NLP Extraction
- Uses **Groq AI** (llama-3.3-70b-versatile model) to extract:
  - Product name
  - Material type (aluminum, steel, plastic, glass, paper, copper, composite)
  - Weight (converted to kg)
  - Recycled content percentage (0-100%)
  - Lifecycle stage (raw-material, manufacturing, distribution, use, end-of-life)
  - Processing details

Example input: `"500g aluminum can with 30% recycled content"`

### 📝 Structured Form Input
- **Product Name**: Text input
- **Material Type**: Dropdown selector
- **Weight**: Numeric input with unit (kg)
- **Recycled Content**: Slider (0-100%)
- **Lifecycle Stage**: Multi-select buttons
- **Processing Details**: Textarea for additional info

### 🔄 Intelligent Gap-Filling
When data is missing or incomplete:
1. **OpenLCA Query**: Fetches material-specific defaults from the selected dataset
2. **AI Gap-Filling**: Uses Groq AI to estimate missing values based on industry standards
3. **Default Values**: Applies fallback values for critical fields

Default recycled content by material:
- Aluminum: 30%
- Steel: 25%
- Plastic: 9%
- Glass: 33%
- Paper: 65%
- Copper: 35%

### 💡 Smart Hints
Six context-aware hint cards provide guidance:
- Material purity suggestions
- Energy source recommendations
- Transportation distance estimates
- Processing efficiency tips
- Waste reduction strategies
- End-of-life considerations

### 🌍 Global Averages
Displays industry-standard values for reference:
- Energy Intensity
- Carbon Footprint
- Water Usage
- Recycling Rate

## API Endpoints

### `/input-data` (GET)
Renders the product input page. Requires authentication.

### `/api/analyze-nlp` (POST)
Extracts structured data from natural language input.

**Request:**
```json
{
  "text": "500g aluminum can with 30% recycled content",
  "dataSource": "openlca"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "productName": "500g aluminum can with 30% recycled content",
    "materialType": "aluminum",
    "weight": 0.5,
    "weightUnit": "kg",
    "recycledContent": 30,
    "lifecycleStage": "manufacturing",
    "processingDetails": ""
  },
  "missingData": ["processingDetails"],
  "message": "Product data extracted successfully"
}
```

### `/api/analyze-structured` (POST)
Processes structured form input.

**Request:**
```json
{
  "productName": "Aluminum Beverage Can",
  "materialType": "aluminum",
  "weight": 0.5,
  "recycledContent": 30,
  "lifecycleStage": "manufacturing",
  "processingDetails": "Rolling, stamping, coating",
  "dataSource": "openlca"
}
```

**Response:**
```json
{
  "success": true,
  "data": { ... },
  "missingData": [],
  "message": "Product data processed successfully"
}
```

### `/api/gap-fill` (POST)
Fills missing data using AI and OpenLCA.

**Request:**
```json
{
  "data": {
    "productName": "Aluminum Can",
    "materialType": "aluminum",
    "weight": 0.5
  },
  "missingFields": ["recycledContent", "processingDetails"],
  "dataSource": "openlca"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "productName": "Aluminum Can",
    "materialType": "aluminum",
    "weight": 0.5,
    "recycledContent": 30,
    "processingDetails": "Rolling, extrusion, annealing"
  },
  "message": "Missing data filled successfully"
}
```

### `/api/openlca-data` (POST)
Retrieves material-specific data from OpenLCA.

**Request:**
```json
{
  "materialType": "aluminum"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recycledContent": 30,
    "density": 2.7,
    "processingDetails": "Rolling, extrusion, annealing"
  }
}
```

## Integration with Dataset Selection

Page 2 automatically retrieves the selected dataset from Page 1:
```javascript
const dataSource = sessionStorage.getItem('dataSource'); // 'openlca', 'ecoinvent', 'indian', or 'builtin'
```

This dataset is used for gap-filling queries to ensure consistency.

## Groq API Configuration

The backend uses the Groq API with:
- **Model**: llama-3.3-70b-versatile
- **Temperature**: 0.3 (for extraction), 0.2 (for gap-filling)
- **Max Tokens**: 500 (extraction), 300 (gap-filling)

Fallback: If Groq API fails, regex-based extraction is used.

## Error Handling

All endpoints return consistent error responses:
```json
{
  "success": false,
  "message": "Error description"
}
```

Common errors:
- No text provided (NLP)
- Invalid material type
- Groq API timeout
- OpenLCA connection failed

## File Structure

```
authentication/
├── app.py                          # Main Flask app with Page 2 routes
├── templates/
│   └── input.html                  # Page 2 HTML template
├── static/
│   ├── css/
│   │   └── input.css               # Page 2 styling
│   └── js/
│       └── input.js                # Page 2 frontend logic
```

## Testing

### Test NLP Extraction
```javascript
// In browser console on /input-data page
analyzeNLP();
```

Enter example text:
- `"500g aluminum can with 30% recycled content"`
- `"1kg steel beam for construction, manufacturing stage"`
- `"750ml plastic bottle made from PET, end-of-life recycling"`

### Test Structured Input
1. Select "Structured Form" mode
2. Fill in the form fields
3. Click "Analyze Product"

### Test Gap-Filling
1. Use NLP or structured input with missing data
2. System automatically identifies missing fields
3. Click "Fill Missing Data" to trigger gap-filling

## Next Steps (Page 3)
After data is analyzed and gap-filled, the user proceeds to:
- **Confirmation Page**: Review extracted/filled data, make manual corrections
- **LCA Calculation**: Run LCA assessment using the finalized data
- **Results Dashboard**: View environmental impact metrics

## Dependencies

Required Python packages:
- `Flask`: Web framework
- `requests`: HTTP library for Groq API
- `re`: Regular expressions for fallback extraction
- `json`: JSON parsing

Already installed in `requirements.txt`.

## Notes

- The OpenLCA integration currently uses default values. Future versions will implement actual JSON-RPC queries to the OpenLCA IPC Server.
- The Groq API key is embedded in the code. For production, move to environment variables.
- Session management ensures users are authenticated before accessing the page.

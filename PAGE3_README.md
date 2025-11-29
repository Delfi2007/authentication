# Page 3: Data Confirmation

## Overview
Page 3 allows users to review, verify, and edit all extracted/filled data before proceeding to the LCA analysis.

## Features

### ✅ Data Review Table
- **Product Name**: Editable text field
- **Material Type**: Dropdown selector (aluminum, steel, plastic, glass, paper, copper, composite)
- **Weight**: Numeric input with unit (kg)
- **Recycled Content**: Percentage (0-100%)
- **Lifecycle Stage**: Dropdown (raw-material, manufacturing, distribution, use, end-of-life)
- **Processing Details**: Text area for additional information

### 🏷️ Source Badges
Each field displays its data source:
- **AI Extracted** (Blue): Data extracted from natural language using Groq AI
- **System Default** (Yellow): Default values applied by the system
- **OpenLCA Data** (Green): Values from OpenLCA database
- **User Edited** (Blue): Manually edited by the user

### ✏️ Inline Editing
- Click the edit icon next to any field
- Modal dialog opens with appropriate input type
- Validation for numeric fields (weight, recycled content)
- Changes saved to session storage
- Source badge updates to "User Edited"

### 📝 Original Input Display
Shows the original text or form data entered in Page 2 for reference

### 🔄 Progress Tracking
Visual progress bar shows:
1. ✓ Dataset Selection (completed)
2. ✓ Product Input (completed)
3. **→ Confirm Data (current)**
4. Analysis (next)

## User Flow

1. **Land on Page**: Data automatically loaded from session storage
2. **Review Data**: Examine all extracted/filled values
3. **Edit if Needed**: Click edit icons to modify any field
4. **Confirm**: Click "Confirm & Continue" to proceed
5. **Redirect**: Navigate to Analysis page (Page 4)

## Technical Implementation

### Frontend (confirm.html + confirm.js)
- Loads product data from `sessionStorage.getItem('productData')`
- Loads original input from `sessionStorage.getItem('originalInput')`
- Displays data in editable table format
- Modal-based editing system
- Real-time validation

### Backend Routes (app.py)

#### `GET /confirm-data`
Renders the confirmation page. Requires authentication.

#### `POST /api/save-confirmed-data`
Saves confirmed product data to Flask session.

**Request:**
```json
{
  "productData": {
    "productName": "Aluminum Beverage Can",
    "materialType": "aluminum",
    "weight": 0.5,
    "recycledContent": 30,
    "lifecycleStage": "manufacturing",
    "processingDetails": "Rolling, stamping, coating"
  },
  "dataSource": "openlca"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Data saved successfully"
}
```

### Data Flow

```
Page 2 (Input) 
  ↓ [sessionStorage]
Page 3 (Confirm)
  ↓ [API POST]
Flask Session
  ↓
Page 4 (Analysis)
```

## Validation Rules

- **Product Name**: Cannot be empty
- **Weight**: Must be positive number
- **Recycled Content**: Must be between 0-100
- **Material Type**: Must be from predefined list
- **Lifecycle Stage**: Must be from predefined list

## UI/UX Features

### Responsive Design
- Desktop: Full table layout with 4 columns
- Tablet: Adjusted column widths
- Mobile: Stacked card layout

### Visual Feedback
- Hover effects on table rows
- Edit button animations
- Modal slide-up animation
- Loading overlay during save
- Toast notifications for actions

### Accessibility
- Keyboard navigation (Escape to close modal)
- Click outside modal to close
- Clear visual hierarchy
- Color-coded badges for easy scanning

## Integration Points

### From Page 2:
- Receives `productData` JSON object
- Receives `originalInput` text string
- Receives `dataSource` identifier

### To Page 4:
- Sends confirmed data via Flask session
- Passes data source for analysis context
- Maintains user authentication state

## Error Handling

- No data found: Redirect to Page 2 with warning
- Invalid data format: Show error and redirect
- Network errors: Display retry option
- Validation errors: Show specific field error

## Future Enhancements

- Bulk edit mode for multiple fields
- Data comparison with previous sessions
- Export data as JSON/CSV
- Undo/redo functionality
- Field-level comments/notes
- Confidence scores for AI-extracted data
- Side-by-side comparison with industry averages

## Testing Scenarios

1. **Complete NLP Flow**: Enter text → Extract → Gap-fill → Confirm
2. **Structured Form Flow**: Fill form → Analyze → Confirm
3. **Edit Field**: Click edit → Change value → Save → Verify update
4. **Validation**: Try invalid values (negative weight, >100% recycled)
5. **Navigation**: Back button, logout, continue button
6. **No Data**: Direct URL access without completing Page 2

## Files Structure

```
authentication/
├── templates/
│   └── confirm.html          # Page 3 HTML template
├── static/
│   ├── css/
│   │   └── confirm.css       # Page 3 styling
│   └── js/
│       └── confirm.js        # Page 3 logic
└── app.py                    # Backend routes
```

## Dependencies

- **Session Storage**: For temporary client-side data
- **Flask Session**: For server-side persistence
- **Fetch API**: For AJAX requests
- **CSS Grid**: For responsive table layout

## Security Considerations

- User authentication required for all pages
- Session data cleared on logout
- Server-side validation of all inputs
- XSS prevention in displayed values
- CSRF protection via Flask-Session

## Performance

- Instant data loading from session storage
- No external API calls on page load
- Optimized CSS with minimal reflows
- Lazy loading of modal content
- Debounced input validation

---

**Status**: ✅ Fully Implemented and Ready for Testing

**Next Page**: Page 4 (Analysis & Results) - Coming Soon

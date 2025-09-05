import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import cv2

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="OCR Magic ✨ | Text Extraction",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and modern styling
st.markdown("""
    <style>
    /* Dark theme background */
    .stApp {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: #ffffff;
    }
    
    /* Custom title styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 10px #667eea); }
        to { filter: drop-shadow(0 0 20px #764ba2); }
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #a0a0b8;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Upload area styling - FIXED FOR DEPLOYMENT */
    .uploadedFile {
        background: rgba(102, 126, 234, 0.1) !important;
        border: 2px dashed #667eea !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .uploadedFile:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        border-color: #764ba2 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* File uploader customization - ENHANCED FOR DEPLOYMENT */
    .stFileUploader > div {
        background: rgba(102, 126, 234, 0.05) !important;
        border-radius: 15px !important;
        border: 2px dashed rgba(102, 126, 234, 0.3) !important;
    }
    
    .stFileUploader > div > div {
        background: rgba(102, 126, 234, 0.05) !important;
        border-radius: 15px !important;
    }
    
    /* Fix file uploader text color for deployment */
    .stFileUploader label {
        color: #ffffff !important;
    }
    
    .stFileUploader > div > div > div > div {
        color: #ffffff !important;
    }
    
    .stFileUploader button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
    }
    
    /* Result cards */
    .result-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px 0 rgba(102, 126, 234, 0.4);
    }
    
    /* Text extraction results */
    .text-result {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        transition: all 0.2s ease;
    }
    
    .text-result:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: translateX(5px);
    }
    
    /* Loading animation */
    .loading-text {
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 2s linear infinite;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    /* Stats badges */
    .stat-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin: 0.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Custom buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 30px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to load the EasyOCR model
# We use @st.cache_resource to cache the model and load it only once
@st.cache_resource
def load_model():
    try:
        reader = easyocr.Reader(['en', 'hi'], gpu=False)  # Specify languages and disable GPU for broader compatibility
        return reader
    except Exception as e:
        st.error(f"Error loading OCR model: {e}")
        return None

# Function to preprocess image for better OCR results
def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy and ensure proper data types
    """
    try:
        # Ensure the image is in RGB format
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image if too large (helps with memory and processing)
        MAX_SIZE = (1000, 1000)
        image.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        
        # Convert to numpy array with proper data type
        img_array = np.array(image, dtype=np.uint8)
        
        # Ensure the array is contiguous in memory
        if not img_array.flags['C_CONTIGUOUS']:
            img_array = np.ascontiguousarray(img_array)
        
        # Validate the array shape and data type
        if len(img_array.shape) != 3 or img_array.shape[2] != 3:
            raise ValueError(f"Invalid image shape: {img_array.shape}")
        
        if img_array.dtype != np.uint8:
            img_array = img_array.astype(np.uint8)
        
        return img_array, image
        
    except Exception as e:
        st.error(f"Error preprocessing image: {e}")
        return None, None

# Initialize the EasyOCR reader
reader = load_model()

# --- Streamlit Web App Interface ---

# Animated header
st.markdown('<h1 class="main-header">✨ OCR Magic Studio ✨</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform Images to Text with AI-Powered Recognition</p>', unsafe_allow_html=True)

# Create columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Fancy upload section
    st.markdown("### 📤 Upload Your Image")
    st.markdown("*Supports JPG, JPEG, and PNG formats*")
    
    # File uploader with custom styling
    uploaded_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"],
        help="Drag and drop or click to browse",
        label_visibility="collapsed"
    )

# Main content area
if uploaded_file is not None and reader is not None:
    try:
        # Read and preprocess the uploaded image
        image = Image.open(uploaded_file)
        img_array, processed_image = preprocess_image(image)
        
        if img_array is None or processed_image is None:
            st.error("❌ Failed to process the uploaded image. Please try with a different image.")
        else:
            # Create two columns for image display
            img_col1, img_col2 = st.columns([1, 1])
            
            with img_col1:
                st.markdown("### 🖼️ Original Image")
                st.image(img_array, use_column_width=True)
                
                # Add image stats
                st.markdown(f"""
                <div style="margin-top: 1rem;">
                    <span class="stat-badge">📐 Size: {processed_image.size[0]}x{processed_image.size[1]}</span>
                    <span class="stat-badge">📁 Format: {uploaded_file.type}</span>
                    <span class="stat-badge">🔧 Data Type: {img_array.dtype}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Processing indicator
            with img_col2:
                st.markdown("### 🔍 Processing Status")
                
                # Create a progress indicator
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Initialize
                    progress_bar.progress(20)
                    status_text.markdown('<p class="loading-text">🎯 Analyzing image patterns...</p>', unsafe_allow_html=True)
                    
                    # Step 2: OCR Processing
                    progress_bar.progress(60)
                    status_text.markdown('<p class="loading-text">🧠 Applying OCR magic...</p>', unsafe_allow_html=True)
                    
                    # Perform OCR on the image with error handling
                    result = reader.readtext(img_array)
                    
                    # Step 3: Complete
                    progress_bar.progress(100)
                    status_text.success("✅ Text extraction complete!")
                    
                except Exception as ocr_error:
                    progress_bar.empty()
                    status_text.error(f"❌ OCR processing failed: {str(ocr_error)}")
                    st.error("Please try with a different image or contact support if the problem persists.")
                    result = []
            
            # Only proceed if OCR was successful
            if 'result' in locals():
                # Divider
                st.markdown("<hr>", unsafe_allow_html=True)
                
                # Results section
                results_col1, results_col2 = st.columns([1, 1])
                
                with results_col1:
                    st.markdown("### 📝 Extracted Text")
                    
                    if not result:
                        st.warning("🔍 No text was found in the image.")
                    else:
                        st.markdown(f'<div class="stat-badge">📊 Found {len(result)} text region(s)</div>', unsafe_allow_html=True)
                        
                        # Display each detected text with styling
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        for i, detection in enumerate(result, 1):
                            confidence = detection[2]
                            text = detection[1]
                            
                            # Create styled text display
                            confidence_color = "#4ade80" if confidence > 0.8 else "#fbbf24" if confidence > 0.5 else "#f87171"
                            
                            st.markdown(f"""
                            <div class="text-result">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <span style="color: #a0a0b8; font-size: 0.9rem;">Region {i}</span>
                                    <span style="color: {confidence_color}; font-weight: bold;">
                                        {confidence:.1%} confidence
                                    </span>
                                </div>
                                <div style="font-size: 1.2rem; color: #ffffff;">
                                    {text}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                
                with results_col2:
                    st.markdown("### 🎨 Visual Detection")
                    
                    if not result:
                        st.info("📍 Cannot draw bounding boxes as no text was found.")
                    else:
                        try:
                            # Create a copy of the image to draw on
                            annotated_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                            
                            # Draw bounding boxes and text on the image
                            for detection in result:
                                top_left = tuple([int(val) for val in detection[0][0]])
                                bottom_right = tuple([int(val) for val in detection[0][2]])
                                text = detection[1]
                                
                                # Draw the rectangle with gradient-like effect
                                annotated_image = cv2.rectangle(annotated_image, top_left, bottom_right, (234, 126, 102), 3)
                                # Inner rectangle for gradient effect
                                inner_tl = (top_left[0] + 2, top_left[1] + 2)
                                inner_br = (bottom_right[0] - 2, bottom_right[1] - 2)
                                annotated_image = cv2.rectangle(annotated_image, inner_tl, inner_br, (162, 75, 118), 1)
                            
                            # Convert back to RGB to display in Streamlit
                            annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
                            st.image(annotated_image_rgb, use_column_width=True)
                            
                            # Add export option
                            st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
                            if st.button("💾 Export Detected Text", key="export"):
                                text_output = "\n".join([detection[1] for detection in result])
                                st.download_button(
                                    label="📥 Download as TXT",
                                    data=text_output,
                                    file_name="extracted_text.txt",
                                    mime="text/plain"
                                )
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        except Exception as draw_error:
                            st.error(f"Error creating annotated image: {draw_error}")
    
    except Exception as e:
        st.error(f"❌ Error processing image: {e}")
        st.info("Please try uploading a different image or check if the image file is corrupted.")

elif uploaded_file is not None and reader is None:
    st.error("❌ OCR model failed to load. Please refresh the page and try again.")

else:
    # Welcome screen when no image is uploaded
    st.markdown("""
    <div class="result-card" style="text-align: center; padding: 3rem;">
        <h2 style="color: #667eea; margin-bottom: 1rem;">🚀 Ready to Extract Text?</h2>
        <p style="color: #a0a0b8; font-size: 1.1rem;">
            Upload an image above to begin the magic! Our AI-powered OCR engine supports:
        </p>
        <div style="margin-top: 2rem;">
            <span class="stat-badge">🌍 English Language</span>
            <span class="stat-badge">🇮🇳 Hindi Language</span>
            <span class="stat-badge">📸 Multiple Image Formats</span>
            <span class="stat-badge">⚡ Fast Processing</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #a0a0b8; padding: 1rem;">
    <p>Powered by EasyOCR • Made with 💜 using Streamlit</p>
</div>
""", unsafe_allow_html=True)

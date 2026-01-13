/**
 * Bangla PDF Editor - Frontend Application
 * All processing happens on server, this only handles UI and API calls
 */

// API Base URL
const API_BASE = window.location.origin;

// Application State
const AppState = {
    sessionId: null,
    pdfData: null,
    currentPage: 0,
    zoom: 1.0,
    selectedTextBox: null,
    modifications: [],
    undoStack: [],
    redoStack: []
};

// DOM Elements
const elements = {
    pdfUpload: document.getElementById('pdfUpload'),
    pdfCanvas: document.getElementById('pdfCanvas'),
    textOverlay: document.getElementById('textOverlay'),
    loadingMessage: document.getElementById('loadingMessage'),
    textEditPanel: document.getElementById('textEditPanel'),
    editTextArea: document.getElementById('editTextArea'),
    fontSelect: document.getElementById('fontSelect'),
    fontSize: document.getElementById('fontSize'),
    textColor: document.getElementById('textColor'),
    statusMessage: document.getElementById('statusMessage'),
    sessionInfo: document.getElementById('sessionInfo'),
    pageInfo: document.getElementById('pageInfo'),
    zoomLevel: document.getElementById('zoomLevel'),
    thumbnailContainer: document.getElementById('thumbnailContainer')
};

// Load Available Fonts from Server
async function loadAvailableFonts() {
    try {
        const response = await fetch(`${API_BASE}/api/fonts/list`);
        const result = await response.json();
        
        if (result.success && result.fonts && result.fonts.length > 0) {
            // Clear existing options except default ones
            while (elements.fontSelect.options.length > 3) {
                elements.fontSelect.remove(3);
            }
            
            // Add fonts from server
            result.fonts.forEach(font => {
                const option = document.createElement('option');
                option.value = font.name;
                option.text = font.name;
                elements.fontSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.log('Could not load fonts from server:', error);
    }
}

// Initialize Application
function initApp() {
    setupEventListeners();
    updateStatus('প্রস্তুত | Ready');
    loadAvailableFonts(); // Load fonts on startup
}

// Setup Event Listeners
function setupEventListeners() {
    // File Upload
    elements.pdfUpload.addEventListener('change', handleFileUpload);
    
    // Toolbar Buttons
    document.getElementById('undoBtn').addEventListener('click', handleUndo);
    document.getElementById('redoBtn').addEventListener('click', handleRedo);
    document.getElementById('zoomInBtn').addEventListener('click', () => handleZoom(0.1));
    document.getElementById('zoomOutBtn').addEventListener('click', () => handleZoom(-0.1));
    document.getElementById('prevPageBtn').addEventListener('click', () => navigatePage(-1));
    document.getElementById('nextPageBtn').addEventListener('click', () => navigatePage(1));
    document.getElementById('printPreviewBtn').addEventListener('click', handlePrintPreview);
    
    // Sidebar Buttons
    document.getElementById('saveBtn').addEventListener('click', handleSave);
    document.getElementById('downloadBtn').addEventListener('click', handleDownload);
    document.getElementById('addTextBtn').addEventListener('click', handleAddText);
    document.getElementById('deleteTextBtn').addEventListener('click', handleDeleteText);
    
    // Edit Panel
    document.getElementById('closeEditPanel').addEventListener('click', closeEditPanel);
    document.getElementById('applyEditBtn').addEventListener('click', applyTextEdit);
    document.getElementById('cancelEditBtn').addEventListener('click', closeEditPanel);
    document.getElementById('fontSizeInc').addEventListener('click', () => adjustFontSize(1));
    document.getElementById('fontSizeDec').addEventListener('click', () => adjustFontSize(-1));
    
    // Style Buttons
    document.querySelectorAll('.btn-style').forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });
}

// Handle File Upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    updateStatus('আপলোড হচ্ছে... | Uploading...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            AppState.sessionId = result.session_id;
            AppState.pdfData = result.pdf_data;
            AppState.currentPage = 0;
            
            updateStatus(result.message);
            updateSessionInfo();
            loadPDFPage(0);
            enableButtons();
            
            // Load thumbnails
            loadThumbnails();
        } else {
            updateStatus('ত্রুটি | Error: ' + result.error);
            alert(result.error);
        }
    } catch (error) {
        updateStatus('ত্রুটি | Error: ' + error.message);
        alert('Upload failed: ' + error.message);
    }
}

// Load PDF Page
async function loadPDFPage(pageNumber) {
    if (!AppState.sessionId) return;
    
    updateStatus('পেজ লোড হচ্ছে... | Loading page...');
    
    try {
        const response = await fetch(`${API_BASE}/api/page/render?t=${Date.now()}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                page_number: pageNumber,
                zoom: AppState.zoom
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Display page image
            const img = new Image();
            img.onload = () => {
                const canvas = elements.pdfCanvas;
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                elements.pdfCanvas.style.display = 'block';
                elements.loadingMessage.style.display = 'none';
                
                // Load text boxes for this page
                loadTextBoxes(pageNumber);
                
                updateStatus('প্রস্তুত | Ready');
            };
            img.src = result.image_data;
            
            // Update page info
            updatePageInfo();
        } else {
            updateStatus('ত্রুটি | Error: ' + result.error);
        }
    } catch (error) {
        updateStatus('ত্রুটি | Error: ' + error.message);
    }
}

// Load Text Boxes
function loadTextBoxes(pageNumber) {
    if (!AppState.pdfData) return;
    
    const pageData = AppState.pdfData.pages[pageNumber];
    if (!pageData) return;
    
    // Clear existing text boxes
    elements.textOverlay.innerHTML = '';
    
    // Make sure overlay matches canvas size exactly
    const canvas = elements.pdfCanvas;
    elements.textOverlay.style.width = canvas.width + 'px';
    elements.textOverlay.style.height = canvas.height + 'px';
    
    // Create text boxes from detected text
    pageData.text_blocks.forEach(block => {
        createTextBox(block);
    });
}

// Create Text Box Element
function createTextBox(textBlock) {
    const textBox = document.createElement('div');
    textBox.className = 'text-box';
    textBox.dataset.id = textBlock.id;
    textBox.dataset.text = textBlock.text;
    
    // Position and size from bbox - scaled to match canvas rendering
    const [x0, y0, x1, y1] = textBlock.bbox;
    
    // Scale factor based on zoom
    const scaleFactor = AppState.zoom || 1.0;
    
    textBox.style.left = (x0 * scaleFactor) + 'px';
    textBox.style.top = (y0 * scaleFactor) + 'px';
    textBox.style.width = ((x1 - x0) * scaleFactor) + 'px';
    textBox.style.height = ((y1 - y0) * scaleFactor) + 'px';
    
    // Store metadata
    textBox.dataset.font = textBlock.font;
    textBox.dataset.size = textBlock.size;
    textBox.dataset.color = textBlock.color;
    
    // Create tooltip for hover (requirement #2)
    const tooltip = document.createElement('div');
    tooltip.className = 'text-box-tooltip';
    const fontStyle = textBlock.bold ? 'Bold' : textBlock.italic ? 'Italic' : 'Regular';
    tooltip.innerHTML = `
        <strong>Text:</strong> ${textBlock.text}<br>
        <strong>Font:</strong> ${textBlock.font}<br>
        <strong>Size:</strong> ${textBlock.size}px<br>
        <strong>Style:</strong> ${fontStyle}<br>
        <strong>Color:</strong> ${textBlock.color}
    `;
    textBox.appendChild(tooltip);
    
    // Create move handle (requirement #7)
    const handle = document.createElement('div');
    handle.className = 'text-box-handle';
    handle.title = 'Drag to move | ড্র্যাগ করে সরান';
    handle.style.display = 'none'; // Show only when selected
    textBox.appendChild(handle);
    
    // Click to edit
    textBox.addEventListener('click', (e) => {
        e.stopPropagation();
        selectTextBox(textBox, textBlock);
    });
    
    // Drag to move functionality
    let isDragging = false;
    let startX, startY, startLeft, startTop;
    
    handle.addEventListener('mousedown', (e) => {
        e.stopPropagation();
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        startLeft = parseInt(textBox.style.left);
        startTop = parseInt(textBox.style.top);
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        textBox.style.left = (startLeft + deltaX) + 'px';
        textBox.style.top = (startTop + deltaY) + 'px';
    });
    
    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
    
    elements.textOverlay.appendChild(textBox);
}

// Select Text Box
function selectTextBox(textBox, textBlock) {
    // Remove previous selection and hide handles
    document.querySelectorAll('.text-box.selected').forEach(box => {
        box.classList.remove('selected');
        const handle = box.querySelector('.text-box-handle');
        if (handle) handle.style.display = 'none';
    });
    
    // Select current
    textBox.classList.add('selected');
    
    // Show move handle for selected box
    const handle = textBox.querySelector('.text-box-handle');
    if (handle) handle.style.display = 'flex';
    
    AppState.selectedTextBox = textBlock;
    
    // Store reference to the DOM element
    AppState.selectedTextBoxElement = textBox;
    
    // Open edit panel
    openEditPanel(textBlock);
}

// Open Edit Panel
function openEditPanel(textBlock) {
    elements.textEditPanel.style.display = 'block';
    elements.editTextArea.value = textBlock.text;
    elements.fontSize.value = Math.round(textBlock.size);
    elements.textColor.value = textBlock.color;
    
    // Load the detected font - use exact font name from PDF
    // First, populate font selector with available fonts if not done
    if (elements.fontSelect.options.length <= 3) {
        loadAvailableFonts();
    }
    
    // Set the font - try exact match first, then fallback
    const detectedFont = textBlock.font;
    let fontMatched = false;
    
    // Try exact match
    for (let option of elements.fontSelect.options) {
        if (option.value === detectedFont || option.text === detectedFont) {
            elements.fontSelect.value = option.value;
            fontMatched = true;
            break;
        }
    }
    
    // If no exact match, try partial match
    if (!fontMatched) {
        const fontLower = detectedFont.toLowerCase();
        for (let option of elements.fontSelect.options) {
            if (option.value.toLowerCase().includes(fontLower) || 
                option.text.toLowerCase().includes(fontLower)) {
                elements.fontSelect.value = option.value;
                fontMatched = true;
                break;
            }
        }
    }
    
    // If still no match, add the font as an option
    if (!fontMatched) {
        const newOption = document.createElement('option');
        newOption.value = detectedFont;
        newOption.text = detectedFont;
        elements.fontSelect.appendChild(newOption);
        elements.fontSelect.value = detectedFont;
    }
    
    // Set bold/italic styles based on detected flags
    if (textBlock.bold) {
        document.getElementById('boldBtn').classList.add('active');
    } else {
        document.getElementById('boldBtn').classList.remove('active');
    }
    
    if (textBlock.italic) {
        document.getElementById('italicBtn').classList.add('active');
    } else {
        document.getElementById('italicBtn').classList.remove('active');
    }
}

// Close Edit Panel
function closeEditPanel() {
    elements.textEditPanel.style.display = 'none';
    AppState.selectedTextBox = null;
    AppState.selectedTextBoxElement = null;
    
    // Remove selection and hide handles
    document.querySelectorAll('.text-box.selected').forEach(box => {
        box.classList.remove('selected');
        const handle = box.querySelector('.text-box-handle');
        if (handle) handle.style.display = 'none';
    });
}

// Apply Text Edit
async function applyTextEdit() {
    if (!AppState.selectedTextBox) return;
    
    updateStatus('সম্পাদনা প্রয়োগ হচ্ছে... | Applying edit...');
    
    const newText = elements.editTextArea.value;
    const font = elements.fontSelect.value;
    const fontSize = parseInt(elements.fontSize.value);
    const color = elements.textColor.value;
    
    // Get active styles
    const styles = [];
    document.querySelectorAll('.btn-style.active').forEach(btn => {
        if (btn.dataset.style) styles.push(btn.dataset.style);
    });
    
    // Get current position from the text box element if it was moved
    let position = {
        x: AppState.selectedTextBox.bbox[0],
        y: AppState.selectedTextBox.bbox[1]
    };
    
    if (AppState.selectedTextBoxElement) {
        position = {
            x: parseInt(AppState.selectedTextBoxElement.style.left) || position.x,
            y: parseInt(AppState.selectedTextBoxElement.style.top) || position.y
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/text/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                page_number: AppState.currentPage,
                text_box_id: AppState.selectedTextBox.id,
                new_text: newText,
                font: font,
                font_size: fontSize,
                color: color,
                style: styles.join(','),
                position: position,
                bbox: AppState.selectedTextBox.bbox
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateStatus(result.message);
            
            // Update the text block in memory
            AppState.selectedTextBox.text = newText;
            AppState.selectedTextBox.font = font;
            AppState.selectedTextBox.size = fontSize;
            AppState.selectedTextBox.color = color;
            
            closeEditPanel();
            
            // Reload page to show changes
            loadPDFPage(AppState.currentPage);
        } else {
            updateStatus('ত্রুটি | Error: ' + result.error);
            alert(result.error);
        }
    } catch (error) {
        updateStatus('ত্রুটি | Error: ' + error.message);
        alert('Edit failed: ' + error.message);
    }
}

// Handle Add Text
function handleAddText() {
    // Show modal to add text
    showModal('Add Text', `
        <label>টেক্সট | Text:</label>
        <textarea id="newTextInput" rows="3" style="width: 100%; margin-bottom: 1rem;"></textarea>
        <button onclick="submitNewText()" class="btn btn-primary">যোগ করুন | Add</button>
    `);
}

// Submit New Text
window.submitNewText = async function() {
    const text = document.getElementById('newTextInput').value;
    if (!text) return;
    
    // Add text at center of current page
    const canvas = elements.pdfCanvas;
    const x = canvas.width / 2;
    const y = canvas.height / 2;
    
    try {
        const response = await fetch(`${API_BASE}/api/text/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                page_number: AppState.currentPage,
                text: text,
                position: { x, y },
                font: 'helv',
                font_size: 12,
                color: '#000000'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateStatus(result.message);
            closeModal();
            loadPDFPage(AppState.currentPage);
        }
    } catch (error) {
        alert('Failed to add text: ' + error.message);
    }
};

// Handle Delete Text
async function handleDeleteText() {
    if (!AppState.selectedTextBox) {
        alert('দয়া করে একটি টেক্সট বক্স নির্বাচন করুন | Please select a text box first');
        return;
    }
    
    if (!confirm('আপনি কি নিশ্চিত? | Are you sure?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/text/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                page_number: AppState.currentPage,
                text_box_id: AppState.selectedTextBox.id
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateStatus(result.message);
            closeEditPanel();
            loadPDFPage(AppState.currentPage);
        }
    } catch (error) {
        alert('Failed to delete text: ' + error.message);
    }
}

// Handle Save
async function handleSave() {
    if (!AppState.sessionId) return;
    
    updateStatus('সংরক্ষণ হচ্ছে... | Saving...');
    
    try {
        const response = await fetch(`${API_BASE}/api/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateStatus(result.message);
            alert(result.message);
        }
    } catch (error) {
        updateStatus('ত্রুটি | Error: ' + error.message);
        alert('Save failed: ' + error.message);
    }
}

// Handle Download
async function handleDownload() {
    if (!AppState.sessionId) return;
    
    updateStatus('ডাউনলোড হচ্ছে... | Downloading...');
    
    // First save, then download
    await handleSave();
    
    // Open download link
    window.location.href = `${API_BASE}/api/download/${AppState.sessionId}`;
    
    updateStatus('ডাউনলোড সম্পূর্ণ | Download complete');
}

// Navigate Pages
function navigatePage(direction) {
    const newPage = AppState.currentPage + direction;
    
    if (newPage >= 0 && newPage < AppState.pdfData.num_pages) {
        AppState.currentPage = newPage;
        loadPDFPage(newPage);
    }
}

// Handle Zoom
function handleZoom(delta) {
    AppState.zoom = Math.max(0.25, Math.min(2.0, AppState.zoom + delta));
    elements.zoomLevel.textContent = Math.round(AppState.zoom * 100) + '%';
    loadPDFPage(AppState.currentPage);
}

// Adjust Font Size
function adjustFontSize(delta) {
    const current = parseInt(elements.fontSize.value);
    elements.fontSize.value = Math.max(6, Math.min(72, current + delta));
}

// Handle Undo
function handleUndo() {
    if (AppState.undoStack.length === 0) return;
    
    const action = AppState.undoStack.pop();
    AppState.redoStack.push(action);
    
    // Reload page
    loadPDFPage(AppState.currentPage);
    updateStatus('আনডু করা হয়েছে | Undo complete');
}

// Handle Redo
function handleRedo() {
    if (AppState.redoStack.length === 0) return;
    
    const action = AppState.redoStack.pop();
    AppState.undoStack.push(action);
    
    // Reload page
    loadPDFPage(AppState.currentPage);
    updateStatus('রেডো করা হয়েছে | Redo complete');
}

// Load Thumbnails
async function loadThumbnails() {
    if (!AppState.pdfData) return;
    
    elements.thumbnailContainer.innerHTML = '';
    
    for (let i = 0; i < AppState.pdfData.num_pages; i++) {
        const thumbnail = document.createElement('div');
        thumbnail.className = 'thumbnail';
        if (i === AppState.currentPage) thumbnail.classList.add('active');
        
        thumbnail.innerHTML = `
            <div class="thumbnail-label">Page ${i + 1}</div>
        `;
        
        thumbnail.addEventListener('click', () => {
            AppState.currentPage = i;
            loadPDFPage(i);
            
            // Update active thumbnail
            document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('active'));
            thumbnail.classList.add('active');
        });
        
        elements.thumbnailContainer.appendChild(thumbnail);
    }
}

// Update Status
function updateStatus(message) {
    elements.statusMessage.textContent = message;
}

// Update Session Info
function updateSessionInfo() {
    if (AppState.sessionId) {
        elements.sessionInfo.textContent = `Session: ${AppState.sessionId.substring(0, 8)}...`;
    }
}

// Update Page Info
function updatePageInfo() {
    if (AppState.pdfData) {
        elements.pageInfo.textContent = `Page ${AppState.currentPage + 1} / ${AppState.pdfData.num_pages}`;
    }
}

// Enable Buttons
function enableButtons() {
    const buttons = [
        'saveBtn', 'downloadBtn', 'addTextBtn', 'deleteTextBtn',
        'highlightBtn', 'signatureBtn', 'imageBtn', 'watermarkBtn', 'drawBtn',
        'addPageBtn', 'deletePageBtn', 'rotatePageBtn',
        'mergeBtn', 'splitBtn', 'exportBtn',
        'undoBtn', 'redoBtn', 'zoomInBtn', 'zoomOutBtn',
        'prevPageBtn', 'nextPageBtn', 'gridBtn', 'rulerBtn', 'printPreviewBtn'
    ];
    
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.disabled = false;
    });
}

// Handle Print Preview
function handlePrintPreview() {
    if (!AppState.sessionId) return;
    
    updateStatus('প্রিন্ট প্রিভিউ খোলা হচ্ছে... | Opening print preview...');
    
    // Create print preview window
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    
    if (!printWindow) {
        alert('দয়া করে পপ-আপ ব্লকার নিষ্ক্রিয় করুন | Please disable popup blocker');
        return;
    }
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Print Preview - বাংলা পিডিএফ এডিটর</title>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    background: #f0f0f0;
                }
                .page-container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #667eea;
                }
                h1 {
                    color: #667eea;
                    margin: 0 0 10px 0;
                }
                .info {
                    color: #666;
                    margin-bottom: 20px;
                }
                .page-preview {
                    margin: 20px 0;
                    text-align: center;
                }
                .page-preview img {
                    max-width: 100%;
                    border: 1px solid #ddd;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .page-label {
                    margin: 10px 0;
                    font-weight: bold;
                    color: #333;
                }
                .actions {
                    text-align: center;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }
                button {
                    padding: 10px 20px;
                    margin: 0 5px;
                    font-size: 14px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 600;
                }
                .btn-print {
                    background: #667eea;
                    color: white;
                }
                .btn-print:hover {
                    background: #5568d3;
                }
                .btn-close {
                    background: #6b7280;
                    color: white;
                }
                .btn-close:hover {
                    background: #4b5563;
                }
                @media print {
                    body {
                        background: white;
                        padding: 0;
                    }
                    .page-container {
                        box-shadow: none;
                        padding: 0;
                        max-width: 100%;
                    }
                    .header, .actions {
                        display: none;
                    }
                    .page-preview {
                        page-break-after: always;
                    }
                    .page-label {
                        display: none;
                    }
                }
            </style>
        </head>
        <body>
            <div class="page-container">
                <div class="header">
                    <h1>🖨️ প্রিন্ট প্রিভিউ | Print Preview</h1>
                    <p>বাংলা পিডিএফ এডিটর | Bangla PDF Editor</p>
                </div>
                <div class="info">
                    <p><strong>Session:</strong> ${AppState.sessionId.substring(0, 8)}...</p>
                    <p><strong>Total Pages:</strong> ${AppState.pdfData.num_pages}</p>
                    <p><strong>Current Page:</strong> ${AppState.currentPage + 1}</p>
                </div>
                <div id="pages-container">
                    <p style="text-align: center;">লোড হচ্ছে... | Loading...</p>
                </div>
                <div class="actions">
                    <button class="btn-print" onclick="window.print()">🖨️ প্রিন্ট করুন | Print</button>
                    <button class="btn-close" onclick="window.close()">✕ বন্ধ করুন | Close</button>
                </div>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    
    // Load all pages
    const pagesContainer = printWindow.document.getElementById('pages-container');
    pagesContainer.innerHTML = '';
    
    // Render all pages for print preview
    for (let i = 0; i < AppState.pdfData.num_pages; i++) {
        const pageDiv = printWindow.document.createElement('div');
        pageDiv.className = 'page-preview';
        pageDiv.innerHTML = `
            <div class="page-label">Page ${i + 1} of ${AppState.pdfData.num_pages}</div>
            <p style="text-align: center;">Loading page ${i + 1}...</p>
        `;
        pagesContainer.appendChild(pageDiv);
        
        // Fetch and display each page
        fetch(`${API_BASE}/api/page/render`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                page_number: i,
                zoom: 1.0
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                pageDiv.innerHTML = `
                    <div class="page-label">Page ${i + 1} of ${AppState.pdfData.num_pages}</div>
                    <img src="${result.image_data}" alt="Page ${i + 1}" />
                `;
            }
        })
        .catch(error => {
            pageDiv.innerHTML = `<p style="color: red;">Error loading page ${i + 1}</p>`;
        });
    }
    
    updateStatus('প্রিন্ট প্রিভিউ খোলা হয়েছে | Print preview opened');
}

// Show Modal
function showModal(title, content) {
    const modal = document.getElementById('modalOverlay');
    const modalContent = document.getElementById('modalContent');
    
    modalContent.innerHTML = `
        <h2 style="margin-bottom: 1rem;">${title}</h2>
        ${content}
        <button onclick="closeModal()" class="btn" style="margin-top: 1rem;">বন্ধ করুন | Close</button>
    `;
    
    modal.style.display = 'flex';
}

// Close Modal
window.closeModal = function() {
    document.getElementById('modalOverlay').style.display = 'none';
};

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+Z - Undo
    if (e.ctrlKey && e.key === 'z') {
        e.preventDefault();
        handleUndo();
    }
    
    // Ctrl+Y - Redo
    if (e.ctrlKey && e.key === 'y') {
        e.preventDefault();
        handleRedo();
    }
    
    // Ctrl+S - Save
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        handleSave();
    }
    
    // Escape - Close panel
    if (e.key === 'Escape') {
        closeEditPanel();
        closeModal();
    }
    
    // Arrow keys - Navigate pages
    if (e.key === 'ArrowLeft') {
        navigatePage(-1);
    }
    if (e.key === 'ArrowRight') {
        navigatePage(1);
    }
});

// Initialize on load
document.addEventListener('DOMContentLoaded', initApp);

// ============================================================================
// Menu Bar & Ribbon Functions
// ============================================================================

// Toggle menu dropdown
function toggleMenu(menuItem) {
    // Close all other menus
    document.querySelectorAll('.menu-item').forEach(item => {
        if (item !== menuItem) {
            item.classList.remove('active');
        }
    });
    
    // Toggle this menu
    menuItem.classList.toggle('active');
}

// Close menus when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.menu-item')) {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
    }
});

// Switch ribbon tabs
function switchRibbonTab(tabButton, tabName) {
    // Remove active from all tabs and contents
    document.querySelectorAll('.ribbon-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.ribbon-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Activate clicked tab and corresponding content
    tabButton.classList.add('active');
    document.getElementById('ribbon-' + tabName).classList.add('active');
}

// Toggle dropdown in ribbon
function toggleDropdown(button) {
    const dropdown = button.closest('.ribbon-dropdown');
    dropdown.classList.toggle('active');
    
    // Close when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function closeDropdown(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
                document.removeEventListener('click', closeDropdown);
            }
        });
    }, 0);
}

// Placeholder functions (connect to existing functions)
function savePDF() {
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) saveBtn.click();
}

function downloadPDF() {
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) downloadBtn.click();
}

function undo() {
    handleUndo();
}

function redo() {
    handleRedo();
}

function addText() {
    const addTextBtn = document.getElementById('addTextBtn');
    if (addTextBtn) addTextBtn.click();
}

function deleteText() {
    const deleteTextBtn = document.getElementById('deleteTextBtn');
    if (deleteTextBtn) deleteTextBtn.click();
}

function zoomIn() {
    const zoomInBtn = document.getElementById('zoomInBtn');
    if (zoomInBtn) zoomInBtn.click();
}

function zoomOut() {
    const zoomOutBtn = document.getElementById('zoomOutBtn');
    if (zoomOutBtn) zoomOutBtn.click();
}

function showHelp() {
    alert('Bangla PDF Editor\nVersion 1.0.0\n\nKeyboard Shortcuts:\nCtrl+S: Save\nCtrl+Z: Undo\nCtrl+Y: Redo');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+S - Save
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        savePDF();
    }
    // Ctrl+Z - Undo
    else if (e.ctrlKey && e.key === 'z') {
        e.preventDefault();
        undo();
    }
    // Ctrl+Y - Redo
    else if (e.ctrlKey && e.key === 'y') {
        e.preventDefault();
        redo();
    }
    // F1 - Help
    else if (e.key === 'F1') {
        e.preventDefault();
        showHelp();
    }
});

console.log('Menu bar and ribbon toolbar initialized');

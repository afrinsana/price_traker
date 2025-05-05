import { createOverlay } from './overlay';
import { extractProductData } from './scrapers';

// Main content script
class ContentScript {
  constructor() {
    this.productData = null;
    this.init();
  }

  async init() {
    this.productData = extractProductData();
    this.createUI();
    this.setupListeners();
  }

  createUI() {
    createOverlay(this.productData);
  }

  setupListeners() {
    chrome.runtime.onMessage.addListener(this.handleMessages.bind(this));
    document.addEventListener('click', this.handleClicks.bind(this));
  }

  handleMessages(request, sender, sendResponse) {
    if (request.action === 'GET_PRODUCT_DATA') {
      sendResponse(this.productData);
    }
  }

  // ... other methods
}

new ContentScript();

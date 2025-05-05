import { initializeAlarms } from './alarms';
import { setupContextMenu } from './contextMenu';
import { handleNotifications } from './notifications';
import { syncWithBackend } from './sync';

// Initialize extension background services
chrome.runtime.onInstalled.addListener(() => {
  initializeAlarms();
  setupContextMenu();
  console.log('Price Tracker Pro installed');
});

// Message handling
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'TRACK_PRODUCT':
      handleTrackProduct(request.data, sendResponse);
      return true;
    case 'GET_TRACKED_PRODUCTS':
      handleGetTrackedProducts(sendResponse);
      return true;
    case 'CHECK_PRICE':
      handleCheckPrice(request.data, sendResponse);
      return true;
  }
});

// Track product handler
async function handleTrackProduct(productData, sendResponse) {
  try {
    // Save to local storage
    await chrome.storage.local.set({ 
      [productData.url]: productData 
    });
    
    // Sync with backend
    await syncWithBackend('add', productData);
    
    // Schedule price checks
    chrome.alarms.create(`priceCheck-${productData.url}`, {
      periodInMinutes: 360 // 6 hours
    });
    
    sendResponse({ success: true });
  } catch (error) {
    sendResponse({ success: false, error: error.message });
  }
}

// ... other background handlers
function initAnalytics() {
  trackSearch();
  trackResources();
  trackMap();
  // Print Resources
  $('#print').click(function() {
    logEvent('Print', 'Print - Resources');
  });
  // Catalog Feedback
  $('.feedback').click(function() {
    logEvent('Feedback', 'Feedback - Click');
  });
  // Page Translate
  $('#google_translate_element select option:selected').change(function() {
    logEvent('Translate', 'Language', $(this.text()));
  });
}

function trackSearch() {
  // Categories
  $('.checkbox-category:checkbox').change(function(){
    if (this.checked) {
      logEvent('Search', 'Category', $(this).attr('data-analytics-label'));
    }
  });

  $('.btn-category').click(function() {
    if (!$(this).hasClass('active')) {
      logEvent('Search', 'Category', $(this).attr('data-analytics-label'));
    }
  });

  // Features
  $('.feature').click(function() {
    if (!$(this).hasClass('active')) {
      logEvent('Search', 'Feature', $(this).attr('data-analytics-label'));
    }
  });

  // Required Documents
  $('.checkbox-requirement:checkbox').change(function(){
    if (this.checked) {
      logEvent('Search', 'Required Documents', $(this).attr('data-analytics-label'));
    }
  });

  // Location
  logEvent('Search', 'Location', $('.location').text());
}

function trackResources() {

  // Expand Resource
  $('.resource-header').click(function() {
    if ($(this).closest('.resource').children('.resource-content').css('display') == 'block') {
      logEvent('Resource', 'Expand', $(this).find('.resource-name').text());
    }
  });

}

function trackMap() {

  // Expand Resource
  $('.map-expand').click(function() {
    logEvent('Map', 'Expand', $(this).parent('.map-point').chidren('.map-name').text());
  });

  // Click Through
  $('.map-name').click(function() {
    logEvent('Map', 'Click-Through', $(this).text());
  });
}

function logEvent(category, action, label) {
  ga('send', 'event', category, action, label);
}

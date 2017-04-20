function initAnalytics() {
  trackSearch();
  trackResources();
  $('#print').click(function() {
    logEvent('Print', 'Print - Resources');
  });
  $('.feedback').click(function() {
    logEvent('Feedback', 'Feedback - Click');
  })
}

function trackSearch() {
  // Categories
  $('.checkbox-category:checkbox').change(function(){
    if (this.checked) {
      logEvent('Search', 'Category', $(this).attr('data-analytics-label'));
    }
  });

  $('.btn-category').click(function(){
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
}

function trackResources() {

}

function logEvent(category, action, label) {
  ga('send', 'event', category, action, label);
}

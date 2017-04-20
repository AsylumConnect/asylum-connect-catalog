function initAnalytics() {
  trackSearch();
}

function trackSearch() {
  // Categories
  $('.checkbox-category:checkbox').change(function(){
    if (this.checked) {
      ga('send', 'event', 'Search', 'Category', $(this).attr('data-analytics-label'));
    }
  });
  


  // Features
  $('.feature').click(function() {
    if (!$(this).hasClass('active')) {
      ga('send', 'event', 'Search', 'Feature', $(this).attr('data-analytics-label'));
    }
  });

  // Required Documents
  $('.checkbox-requirement:checkbox').change(function(){
    if (this.checked) {
      ga('send', 'event', 'Search', 'Required Documents', $(this).attr('data-analytics-label'));
    }
  });
}

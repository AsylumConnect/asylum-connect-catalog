from flask.ext.assets import Bundle

app_css = Bundle(
    'app.scss',
    filters='scss',
    output='styles/app.css'
)

app_js = Bundle(
    'app.js',
    filters='jsmin',
    output='scripts/app.js'
)

vendor_css = Bundle(
    'vendor/map.css',
    'vendor/semantic.min.css',
    output='styles/vendor.css'
)

vendor_js = Bundle(
    'vendor/async.js',
    'vendor/address-autocomplete.js',
    'vendor/jquery.min.js',
    'vendor/map.js',
    'vendor/papaparse.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    filters='jsmin',
    output='scripts/vendor.js'
)

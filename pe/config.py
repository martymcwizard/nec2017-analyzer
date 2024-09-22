# pe/config.py

# Thresholds for excluding headers and footers in text extraction
# These ratios represent the proportion of the page height
# HEADER_THRESHOLD_RATIO: Fraction from the top of the page to define the header area
# FOOTER_THRESHOLD_RATIO: Fraction from the top of the page to define the footer area's starting point
HEADER_THRESHOLD_RATIO = 0.0   # Top 6.8% of the page
FOOTER_THRESHOLD_RATIO = 1.0   # Bottom 7.7% of the page (1 - 0.077)

# Other configuration constants can be added here in the future

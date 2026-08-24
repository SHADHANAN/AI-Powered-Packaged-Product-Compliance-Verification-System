import re

# Flags
RE_FLAGS = re.IGNORECASE | re.MULTILINE

# MRP Patterns
MRP_PATTERNS = [
    re.compile(r"(?:M\.?R\.?P\.?|MAX(?:IMUM)?\s*RETAIL\s*PRICE|PRICE|INCL(?:USIVE)?\s*OF\s*ALL\s*TAXES)\s*[:\-.]?\s*(?:RS\.?|INR|₹)?\s*([0-9]+(?:[.,][0-9]{1,2})?)", RE_FLAGS),
    re.compile(r"(?:RS\.?|INR|₹)\s*([0-9]+(?:[.,][0-9]{1,2})?)", RE_FLAGS),
    re.compile(r"\b([0-9]+(?:[.,][0-9]{1,2})?)\s*(?:RS\.?|INR|₹)", RE_FLAGS),
]

# Net Quantity and Units
QUANTITY_PATTERNS = [
    re.compile(r"(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT|CONTENT|VOLUME|MASS)|NET)\s*[:\-.]?\s*([0-9]+(?:[.,][0-9]+)?)\s*(KG|G|GM|GMS|GRAM|GRAMS|MG|MILLIGRAMS?|L|LT|LTR|LTRS|LITRE|LITER|LITRES|LITERS|ML|MILLILITRE|MILLILITER|MILLILITRES|MILLILITERS|N|PCS|UNITS?|PIECES?)\b", RE_FLAGS),
    re.compile(r"\b([0-9]+(?:[.,][0-9]+)?)\s*(KG|G|GM|GMS|GRAM|GRAMS|MG|L|LT|LTR|LTRS|LITRE|LITER|LITRES|LITERS|ML)\b", RE_FLAGS),
]

# Date of Manufacture Patterns
MFD_PATTERNS = [
    re.compile(r"(?:DATE\s*OF\s*(?:MFG|MFD|MANUFACTURE|PACKING|PKD)|MFD\.?|MFG\.?|MANUFACTURED\s*(?:ON)?|PKD\.?|PACKED\s*(?:ON)?)\s*[:\-./]?\s*([0-9]{1,2}[/\-.][0-9]{1,2}[/\-.][0-9]{2,4}|[A-Z]{3,9}[/\-.\s]+[0-9]{2,4}|[0-9]{1,2}[/\-.][0-9]{2,4})", RE_FLAGS),
]

# Expiry / Use-by / Best-before Patterns
EXPIRY_PATTERNS = [
    re.compile(r"(?:USE\s*BY|BEST\s*BEFORE|EXP(?:IRY)?(?:\s*DATE|\s*DT|\.)?|VALID\s*UPTO)\s*[:\-./]?\s*([0-9]{1,2}[/\-.][0-9]{1,2}[/\-.][0-9]{2,4}|[A-Z]{3,9}[/\-.\s]+[0-9]{2,4}|[0-9]{1,2}[/\-.][0-9]{2,4}|[0-9]+\s*(?:MONTHS?|DAYS?|WEEKS?|YEARS?)(?:\s*(?:FROM|OF)\s*(?:MFG|MFD|PACKING|DATE|MANUFACTURE))?)", RE_FLAGS),
]

# Date of Import Patterns
IMPORT_DATE_PATTERNS = [
    re.compile(r"(?:DATE\s*OF\s*IMPORT|IMPORT\s*DATE|IMPORTED\s*ON)\s*[:\-./]?\s*([0-9]{1,2}[/\-.][0-9]{1,2}[/\-.][0-9]{2,4}|[A-Z]{3,9}[/\-.\s]+[0-9]{2,4}|[0-9]{1,2}[/\-.][0-9]{2,4})", RE_FLAGS),
]

# Batch / Lot Number Patterns
BATCH_PATTERNS = [
    re.compile(r"(?:BATCH\s*(?:NO|NUM|NUMBER|\.)?|LOT\s*(?:NO|NUM|NUMBER|\.)?|B\.?\s*NO\.?)\s*[:\-.]?\s*([A-Z0-9\-_/]{3,35})", RE_FLAGS),
]

# Country of Origin Patterns
ORIGIN_PATTERNS = [
    re.compile(r"(?:COUNTRY\s*OF\s*ORIGIN|MADE\s*IN|PRODUCT\s*OF|PRODUCED\s*IN|ORIGIN)\s*[:\-.]?\s*([A-Za-z \t]{2,35})", RE_FLAGS),
]

# Manufacturer Patterns
MANUFACTURER_PATTERNS = [
    re.compile(r"(?:MFD\.?\s*&\s*MKTG\.?\s*BY|MANUFACTURED\s*(?:&|AND)?\s*MARKETED\s*BY|MANUFACTURED\s*BY|MFD\.?\s*BY|MFG\.?\s*BY|PRODUCED\s*BY|PACKED\s*BY|MANUFACTURER)\s*[:\-.]?\s*([^\n\r]+)", RE_FLAGS),
]

# Importer Patterns
IMPORTER_PATTERNS = [
    re.compile(r"(?:IMPORTED\s*(?:&|AND)?\s*MARKETED\s*BY|IMPORTED\s*BY|IMPORTER\s*NAME|IMPORTER)\s*[:\-.]?\s*([^\n\r]+)", RE_FLAGS),
]

# Customer Care Patterns
CUSTOMER_CARE_PATTERNS = [
    re.compile(r"(?:CUSTOMER\s*CARE|CONSUMER\s*CARE|FOR\s*FEEDBACK|FEEDBACK\s*(?:&|AND)?\s*QUERIES|GRIEVANCE|CONTACT\s*US|TOLL\s*FREE|HELPLINE|CALL\s*US)\s*[:\-.]?\s*([^\n\r]+)", RE_FLAGS),
]

PHONE_PATTERN = re.compile(r"\b(?:1800[-\s]?[0-9]{2,4}[-\s]?[0-9]{3,4}|(?:\+91|0)?[-\s]?[6-9][0-9]{4}[-\s]?[0-9]{5}|[0-9]{3,5}[-\s][0-9]{6,8})\b")
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Food License / FSSAI Patterns
FSSAI_PATTERNS = [
    re.compile(r"(?:FSSAI\s*(?:LIC(?:ENSE)?\s*(?:NO|NUM|\.)?)?|LIC(?:ENSE)?\s*(?:NO|NUM|\.)?)\s*[:\-.]?\s*([0-9]{14}|[0-9]{10,15})", RE_FLAGS),
]

# Ingredients Patterns
INGREDIENTS_PATTERNS = [
    re.compile(r"(?:INGREDIENTS?)\s*[:\-.]?\s*([^\n\r]+(?:\n(?![A-Z\s]{3,}:)[^\n\r]+)*)", RE_FLAGS),
]

# Allergen Patterns
ALLERGEN_PATTERNS = [
    re.compile(r"(?:ALLERGEN\s*(?:INFORMATION|ADVICE|DECLARATION)?|CONTAINS)\s*[:\-.]?\s*([^\n\r]+)", RE_FLAGS),
]

# Storage Instructions Patterns
STORAGE_PATTERNS = [
    re.compile(r"(?:STORAGE\s*INSTRUCTIONS?|STORE\s*(?:IN\s*A?)?)\s*[:\-.]?\s*([^\n\r]+)", RE_FLAGS),
]

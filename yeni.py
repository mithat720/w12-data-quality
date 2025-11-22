import pandas as pd
import sys

print("=== DATA QUALITY VALIDATION ===")

# CSV'yi oku - TEST DATA kullan
try:
    df = pd.read_csv('test_amazon_orders.csv')  # Küçük test datası
    df.columns = df.columns.str.strip()
    print("SUCCESS: CSV loaded")
    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
except Exception as e:
    print(f"ERROR: {e}")
    # Fallback: orijinal dosyayı dene
    try:
        df = pd.read_csv('amazon_orders.csv', low_memory=False)
        df.columns = df.columns.str.strip()
        print("SUCCESS: Original CSV loaded as fallback")
        print(f"Data shape: {df.shape}")
    except:
        sys.exit(1)

errors = []
warnings = []

print("\n--- Running Validations ---")

# 1. Null kontrolü
null_counts = df.isnull().sum()
if null_counts.any():
    for col, count in null_counts[null_counts > 0].items():
        warnings.append(f"Null values in {col}: {count}")
        print(f"WARNING: {count} null values in {col}")
else:
    print("PASS: No null values found")

# 2. Order ID kontrolü
if 'Order ID' in df.columns:
    unique_count = df['Order ID'].nunique()
    total_count = len(df)
    if unique_count == total_count:
        print("PASS: All Order IDs are unique")
    else:
        errors.append(f"Duplicate Order IDs: {unique_count} unique out of {total_count}")
        print(f"ERROR: Duplicate Order IDs found - {unique_count} unique out of {total_count}")
else:
    warnings.append("Order ID column not found")

# 3. Quantity kontrolü
if 'Qty' in df.columns:
    if (df['Qty'] < 0).any():
        errors.append("Negative quantities found in Qty column")
        print("ERROR: Negative quantities found")
    else:
        print("PASS: All quantities are positive")
else:
    warnings.append("Qty column not found")

# 4. Amount kontrolü
if 'Amount' in df.columns:
    if (df['Amount'] < 0).any():
        errors.append("Negative amounts found in Amount column")
        print("ERROR: Negative amounts found")
    else:
        print("PASS: All amounts are positive")
else:
    warnings.append("Amount column not found")

# 5. Currency kontrolü - NaN değerleri handle et
if 'currency' in df.columns:
    # NaN değerleri temizle
    valid_currencies = df['currency'].dropna()
    if len(valid_currencies) > 0 and not (valid_currencies == 'INR').all():
        invalid_currency = valid_currencies[valid_currencies != 'INR'].unique()
        errors.append(f"Invalid currencies found: {list(invalid_currency)}")
        print(f"ERROR: Invalid currencies found: {list(invalid_currency)}")
    elif len(valid_currencies) == 0:
        errors.append("All currency values are NaN")
        print("ERROR: All currency values are NaN")
    else:
        print("PASS: All currencies are INR")
else:
    warnings.append("currency column not found")

# 6. Ship country kontrolü - NaN değerleri handle et  
if 'ship-country' in df.columns:
    # NaN değerleri temizle
    valid_countries = df['ship-country'].dropna()
    if len(valid_countries) > 0 and not (valid_countries == 'IN').all():
        invalid_country = valid_countries[valid_countries != 'IN'].unique()
        errors.append(f"Invalid ship countries found: {list(invalid_country)}")
        print(f"ERROR: Invalid ship countries found: {list(invalid_country)}")
    elif len(valid_countries) == 0:
        errors.append("All ship-country values are NaN")
        print("ERROR: All ship-country values are NaN")
    else:
        print("PASS: All ship countries are IN")
else:
    warnings.append("ship-country column not found")

# 7. Status kontrolü
if 'Status' in df.columns:
    allowed_statuses = ['Shipped', 'Cancelled', 'Pending', 'Shipping']
    invalid_status = df[~df['Status'].isin(allowed_statuses)]
    if len(invalid_status) > 0:
        invalid_status_values = invalid_status['Status'].unique()
        errors.append(f"Invalid status values: {list(invalid_status_values)}")
        print(f"ERROR: Invalid status values found: {list(invalid_status_values)}")
    else:
        print("PASS: All status values are valid")
else:
    warnings.append("Status column not found")

# Sonuçlar
print("\n=== VALIDATION RESULTS ===")

if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  ⚠ {w}")

if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  ❌ {e}")
    print("\nFAILED: Validation errors found")
    sys.exit(1)
else:
    print("SUCCESS: All validations passed")
    if warnings:
        print(f"Note: {len(warnings)} warnings present")
    sys.exit(0)
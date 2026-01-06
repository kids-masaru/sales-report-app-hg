

# Read template file directly
with open('templates/confirm.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Checking Template Content Logic...")

if '{% elif key == "次回営業件名" %}' in content:
    print("SUCCESS: Found specific block for '次回営業件名'")
else:
    print("FAILED: Specific block for '次回営業件名' missing")

if '{% for opt in next_sales_options %}' in content:
    print("SUCCESS: Found loop using 'next_sales_options'")
else:
    print("FAILED: Loop using 'next_sales_options' missing")

# Verify App.py content as well
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()
    
if 'next_sales_options=NEXT_SALES_ACTIVITY_OPTIONS' in app_content:
    print("SUCCESS: app.py passes 'next_sales_options'")
else:
    print("FAILED: app.py does NOT pass 'next_sales_options'")


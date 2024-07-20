# -*- coding: utf-8 -*-
from PIL import Image
import pytesseract
import numpy as np
import re
import sqlite3 
import os
import sys

filename = 'south.png'
#filename = sys.argv[1]
#print(sys.argv[1])
img1 = np.array(Image.open(filename))
text = pytesseract.image_to_string(img1)
#print(text)
text = re.sub(r'[:,-]', '', text)
#print(text)
current_path = os.path.dirname(os.path.realpath(__file__))

name= ', '.join({current_path})+'\\' + ', '.join({filename})
print(name)

# Split the OCR text into lines
lines = text.split('\n')
# Assuming the second line contains the supplier name
supplier_name_line = lines[1].strip() if len(lines) > 1 else "Not found"

# Define regex patterns
patterns = {
    #"invoice_number": r"(?i)\b[A-Z0-9/]+\b",  # Alphanumeric pattern for invoice number
    "invoice_number": r"CAS\\[0-9A-Za-z\\-]+",
    "invoice_date": r"\b\d{2}/\d{2}/\d{4}\b",  # Date pattern (dd/mm/yyyy)
    "subtotal": r"(?i)sub\s*total\s*[:\-]?\s*([\d,]+\.\d{2})",
    "cgst": r"(?i)c\s*gst\s*[:\-]?\s*([\d,]+\.\d{2})",
    "sgst": r"(?i)s\s*gst\s*[:\-]?\s*([\d,]+\.\d{2})",
    "total": r"(?i)total\s*[:\-]?\s*([\d,]+\.\d{2})",
    "gstin": r"G\s*S\s*([A-Z0-9]{3})"
}

# Function to extract data using regex
def extract_data(text, patterns):
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[key] = match.group(0).strip()
        else:
            data[key] = "Not found"
    return data

# Extract data
extracted_data = extract_data(text, patterns)
extracted_data['supplier_name'] = supplier_name_line

# Prepare the output string
output_str = f"""Extracted Information:
Invoice Number: {extracted_data.get('invoice_number')}
Invoice Date: {extracted_data.get('invoice_date')}
Subtotal: {extracted_data.get('subtotal')}
Cgst: {extracted_data.get('cgst')}
Sgst: {extracted_data.get('sgst')}
Total: {extracted_data.get('total')}
Supplier Name: {extracted_data.get('supplier_name')}
GSTIN: {extracted_data.get('gstin')}
"""



# Print extracted data

#print(output_str)

# Write the output to a text file
with open("writehere.txt", "w") as file:
    file.write(output_str)
    
inv_num=', '.join({extracted_data.get('invoice_number')})
inv_date=', '.join({extracted_data.get('invoice_date')})
sub_tot=', '.join({extracted_data.get('subtotal')})[10:]
cgst=', '.join({extracted_data.get('cgst')})[5:]
sgst=', '.join({extracted_data.get('sgst')})[5:]
tot=', '.join({extracted_data.get('total')})[6:]
supp_name=', '.join({extracted_data.get('supplier_name')})
gstin=', '.join({extracted_data.get('gstin')})

conn = sqlite3.connect('pythonprojdb.db') 
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM ocroutputtbl")
row_count = cursor.fetchone()[0]
if row_count == 0:
    cursor.execute("insert into ocroutputtbl(id) values(0)")

cursor.execute("SELECT MAX(id) FROM ocroutputtbl")
max_id = cursor.fetchone()[0] + 1  # Fetch the first column of the first row
ins_stmt='INSERT INTO ocroutputtbl VALUES (?,?,?,?,?,?,?,?,?,?,?)'
cursor.execute(ins_stmt,(max_id,name,output_str,inv_num,inv_date,supp_name,gstin,sub_tot,cgst,sgst,tot) )
# Commit your changes in the database	 
conn.commit() 

# Display data inserted 
print("Data Inserted in the table:") 
data=cursor.execute('''SELECT id,inv_num,inv_date,sub_total,cgst,sgst,total, supplier_name FROM ocroutputtbl''') 

for row in data: 
	print(row) 
     
    



# Closing the connection 
conn.close()

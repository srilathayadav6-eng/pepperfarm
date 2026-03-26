import base64
import os

os.makedirs('assets', exist_ok=True)

# A tiny valid 1x1 jpeg
jpeg_b64 = "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
with open('assets/qr_code.jpg', 'wb') as f:
    f.write(base64.b64decode(jpeg_b64))

# Tiny valid PDF 
pdf_code = b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF\n"
with open('assets/company_profile.pdf', 'wb') as f:
    f.write(pdf_code)

print("Assets created successfully in the assets/ folder.")

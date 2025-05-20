import requests
import base64
import sys
import os
from PIL import Image
from io import BytesIO
from pdf2image import convert_from_path
import argparse

API_URL = 'http://localhost:5050/extract-total'
SUPPORTED_EXTS = {'.pdf', '.png', '.jpg', '.jpeg'}

CLAIMS_DIR = 'claims'
DEFAULT_NUM_FILES = 5

def file_to_display_base64(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        images = convert_from_path(filepath, first_page=1, last_page=1)
        img = images[0]
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        mime = 'image/jpeg'
    else:
        img = Image.open(filepath)
        buffered = BytesIO()
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        mime = 'image/jpeg'
    b64 = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:{mime};base64,{b64}"

import random

def get_claim_files(claims_dir, num_files):
    files = [f for f in os.listdir(claims_dir)
             if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS]
    if not files:
        return []
    selected = random.sample(files, min(num_files, len(files)))
    return [os.path.join(claims_dir, f) for f in selected]

def main():
    parser = argparse.ArgumentParser(description="Batch test invoice extraction and generate HTML report.")
    parser.add_argument('--claims-dir', type=str, default=CLAIMS_DIR, help='Directory with claim images (default: claims)')
    parser.add_argument('--num', type=int, default=DEFAULT_NUM_FILES, help='Number of images to test (default: 5)')
    args = parser.parse_args()

    claim_files = get_claim_files(args.claims_dir, args.num)
    if not claim_files:
        print(f"No supported files found in {args.claims_dir}")
        sys.exit(1)

    results = []
    import time
    for idx, filepath in enumerate(claim_files, 1):
        print(f"[{idx}/{len(claim_files)}] Processing {filepath} ...", end=' ')
        start_time = time.time()
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f)}
            try:
                response = requests.post(API_URL, files=files, timeout=60)
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"Error: {e} (Time: {elapsed:.2f}s)")
                results.append({'filename': os.path.basename(filepath), 'total_amount': 'API ERROR', 'img_data_url': '', 'error': str(e), 'time_taken': elapsed})
                continue
        elapsed = time.time() - start_time
        if response.status_code != 200:
            print(f"API Error: {response.status_code} (Time: {elapsed:.2f}s)")
            results.append({'filename': os.path.basename(filepath), 'total_amount': 'API ERROR', 'img_data_url': '', 'error': response.text, 'time_taken': elapsed})
            continue
        result = response.json()
        total_amount = result.get('total_amount', 'N/A')
        handwriting = result.get('handwriting', None)
        img_data_url = file_to_display_base64(filepath)
        results.append({'filename': os.path.basename(filepath), 'total_amount': total_amount, 'handwriting': handwriting, 'img_data_url': img_data_url, 'error': None, 'time_taken': elapsed})
        handwriting_str = f", Handwritten: {handwriting}" if handwriting is not None else ""
        print(f"OK (Time: {elapsed:.2f}s){handwriting_str}")

    # Generate HTML report
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invoice Extraction Batch Report</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f7f7f9; margin: 0; padding: 0; }
            .container { max-width: 1200px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 32px; }
            h1 { color: #333; margin-bottom: 24px; }
            .grid { display: flex; flex-wrap: wrap; gap: 32px; }
            .card { flex: 1 1 320px; min-width: 320px; max-width: 350px; background: #fafbfc; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); padding: 18px 18px 24px 18px; margin-bottom: 24px; display: flex; flex-direction: column; align-items: center; }
            .filename { color: #555; font-size: 1em; margin-bottom: 8px; word-break: break-all; }
            .value { font-size: 1.5em; font-weight: bold; color: #2b9348; margin-bottom: 18px; }
            .img-preview { border: 1px solid #eee; border-radius: 8px; max-width: 100%; max-height: 400px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); margin-bottom: 8px; }
            .error { color: #b30000; font-size: 0.95em; margin-bottom: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Invoice Extraction Batch Report</h1>
            <div class="grid">
    '''
    for r in results:
        handwriting_html = ''
        if r.get('handwriting') is not None:
            handwriting_html = f'<div class="value" style="font-size:1em;color:#555;">Handwritten: {r["handwriting"]}</div>'
        html += f'''<div class="card">
            <div class="filename">{r['filename']}</div>
            <div class="value">{r['total_amount']}</div>
            {handwriting_html}
            <div class="value" style="font-size:1em;color:#555;">Time: {r['time_taken']:.2f}s</div>
            {'<div class="error">'+r['error']+'</div>' if r['error'] else ''}
            {f'<img src="{r["img_data_url"]}" class="img-preview" alt="Invoice Preview" />' if r['img_data_url'] else ''}
        </div>\n'''

    html += '''
            </div>
        </div>
    </body>
    </html>
    '''
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Report generated: report.html")

if __name__ == '__main__':
    main()

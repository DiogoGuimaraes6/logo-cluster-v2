from flask import Flask, render_template, jsonify, send_from_directory, request, send_file
from ssim_storage import SSIMStorage
import os
from pathlib import Path
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
storage = SSIMStorage()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logos')
def get_logos():
    set_type = request.args.get('set', 'A')  # Default to set A
    method = request.args.get('method', 'block4')
    dir_prefix = f'pngs_ALL_inkscape_512/pngs_{set_type}_inkscape_512/'
    if method == 'block4':
        similarities = storage.load_block4_similarities_for_set(set_type)
        logos = set()
        for f1, f2 in similarities.keys():
            logos.add(f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1])
            logos.add(f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1])
        return jsonify(sorted(list(logos)))
    else:
        # Get all unique logo paths from the SSIM scores
        ssim_scores, metadata = storage.load_ssim_scores(name=f'ssim_scores_{set_type}')
        logos = set()
        for (f1, f2) in ssim_scores.keys():
            logos.add(f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1])
            logos.add(f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1])
        return jsonify(sorted(list(logos)))

@app.route('/api/similar/<path:logo_path>')
def get_similar(logo_path):
    set_type = request.args.get('set', 'A')  # Default to set A
    method = request.args.get('method', 'block4')
    dir_prefix = f'pngs_ALL_inkscape_512/pngs_{set_type}_inkscape_512/'
    print(f"[DEBUG] Requested similar logos for: {logo_path} (method={method})")
    if method == 'block4':
        similarities = storage.load_block4_similarities_for_set(set_type)
        similar_pairs = []
        for (f1, f2), score in similarities.items():
            f1_full = f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1]
            f2_full = f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1]
            if f1_full == logo_path:
                similar_pairs.append((f2_full, score))
            elif f2_full == logo_path:
                similar_pairs.append((f1_full, score))
        print(f"[DEBUG] Found {len(similar_pairs)} block4 similar pairs for {logo_path}")
        similar_pairs.sort(key=lambda x: x[1], reverse=True)
        return jsonify(similar_pairs)
    else:
        ssim_scores, metadata = storage.load_ssim_scores(name=f'ssim_scores_{set_type}')
        similar_pairs = []
        for (f1, f2), score in ssim_scores.items():
            f1_full = f1 if f1.startswith(dir_prefix) else dir_prefix + f1.split('/')[-1]
            f2_full = f2 if f2.startswith(dir_prefix) else dir_prefix + f2.split('/')[-1]
            if f1_full == logo_path:
                similar_pairs.append((f2_full, score))
            elif f2_full == logo_path:
                similar_pairs.append((f1_full, score))
        print(f"[DEBUG] Found {len(similar_pairs)} similar pairs for {logo_path}")
        similar_pairs.sort(key=lambda x: x[1], reverse=True)
        return jsonify(similar_pairs)

@app.route('/logos/<path:filename>')
def serve_logo(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # If the filename starts with the new ALL path, serve from there
    if filename.startswith('pngs_ALL_inkscape_512/'):
        rel_path = filename[len('pngs_ALL_inkscape_512/'):]
        directory = os.path.join(base_dir, 'pngs_ALL_inkscape_512')
    else:
        # Fallback to old logic for other cases
        logo_path = os.path.join(base_dir, 'logos', filename)
        directory = os.path.dirname(logo_path)
        rel_path = os.path.basename(logo_path)
    
    if not os.path.exists(os.path.join(directory, rel_path)):
        print(f"File not found: {os.path.join(directory, rel_path)}")
        return f"File not found: {filename}", 404
    return send_from_directory(directory, rel_path, as_attachment=False)

@app.route('/api/export_png', methods=['POST'])
def export_png():
    data = request.json
    main_logo = data.get('main_logo')
    similar_logos = data.get('similar_logos', [])  # List of {filename, label, score}
    # Settings
    bg_color = (17, 17, 17)  # #111
    label_color = (255, 255, 255)
    sim_label_color = (255, 92, 26)  # #ff5c1a
    score_color = (255, 92, 26)
    font_path_custom = os.path.join('static', 'fonts', 'NB-Architekt-R-Regular.otf')
    font_path_fallback = '/Library/Fonts/Arial.ttf'  # Use Arial as fallback
    font_size_label = 32
    font_size_score = 40
    thumb_size = 256
    padding = 48
    # Load fonts
    try:
        font_label = ImageFont.truetype(font_path_custom, font_size_label)
        font_score = ImageFont.truetype(font_path_custom, font_size_score)
        print(f"[DEBUG] Loaded custom font: {font_path_custom}")
    except Exception as e:
        print(f"[WARN] Could not load custom font: {e}. Falling back to Arial.")
        try:
            font_label = ImageFont.truetype(font_path_fallback, font_size_label)
            font_score = ImageFont.truetype(font_path_fallback, font_size_score)
        except Exception as e2:
            print(f"[ERROR] Could not load fallback font: {e2}. Using default font.")
            font_label = font_score = None
    # Compose image list
    all_logos = [{'filename': main_logo, 'label': 'Original Logo', 'score': None}]
    for item in similar_logos:
        all_logos.append({
            'filename': item['filename'],
            'label': 'Similarity',
            'score': item['score']
        })
    # Load images
    images = []
    for logo in all_logos:
        img_path = logo['filename']
        resolved_path = None
        if os.path.exists(img_path):
            resolved_path = img_path
        else:
            img_path2 = os.path.join('pngs_A_inkscape_512', logo['filename'])
            if os.path.exists(img_path2):
                resolved_path = img_path2
            else:
                img_path3 = os.path.join('logos', logo['filename'])
                if os.path.exists(img_path3):
                    resolved_path = img_path3
        print(f"[DEBUG] Logo: {logo['filename']} | Resolved path: {resolved_path}")
        if resolved_path:
            try:
                img = Image.open(resolved_path).convert('RGBA')
                img = img.resize((thumb_size, thumb_size), Image.LANCZOS)
            except Exception as e:
                print(f"[ERROR] Failed to load image {resolved_path}: {e}")
                img = Image.new('RGBA', (thumb_size, thumb_size), (0, 0, 0, 0))
        else:
            print(f"[ERROR] Logo file not found: {logo['filename']}")
            img = Image.new('RGBA', (thumb_size, thumb_size), (0, 0, 0, 0))
        images.append(img)
    # Calculate output size
    n = len(images)
    width = n * thumb_size + (n + 1) * padding
    height = thumb_size + 3 * padding + font_size_label + font_size_score + 20
    out_img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(out_img)
    # Draw each logo and its labels
    for i, (img, logo) in enumerate(zip(images, all_logos)):
        x = padding + i * (thumb_size + padding)
        y = padding
        # Draw white rounded rectangle for each logo
        rect_radius = 32
        logo_margin = 16
        draw.rounded_rectangle([x, y, x + thumb_size, y + thumb_size], radius=rect_radius, fill=(255, 255, 255))
        # Resize logo to fit inside the margin
        logo_box = thumb_size - 2 * logo_margin
        img_resized = img.resize((logo_box, logo_box), Image.LANCZOS)
        out_img.paste(img_resized, (x + logo_margin, y + logo_margin), img_resized)
        # Draw label
        label = logo['label']
        if font_label:
            bbox = font_label.getbbox(label)
            lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            lx = x + (thumb_size - lw) // 2
            ly = y + thumb_size + 8
            draw.text((lx, ly), label, font=font_label, fill=sim_label_color if label != 'Original Logo' else label_color)
        # Draw score
        if logo['score'] is not None and font_score:
            score_text = f"SSIM: {logo['score']:.3f}"
            bbox = font_score.getbbox(score_text)
            sw, sh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            sx = x + (thumb_size - sw) // 2
            sy = y + thumb_size + font_size_label + 18
            draw.text((sx, sy), score_text, font=font_score, fill=score_color)
    # Output to bytes
    buf = io.BytesIO()
    out_img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='logos_compare.png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug) 
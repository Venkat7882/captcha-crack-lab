import os
import random
import string
import pytesseract
from captcha.image import ImageCaptcha
from PIL import Image, ImageDraw, ImageFilter

# === Configuration ===
OUTPUT_DIR = r'<<your folder path here>>'
NUM_CAPTCHAS = 10
CAPTCHA_LENGTH = 5

# Path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\VenkatReddy\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Create output directory if needed
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_random_text(length=CAPTCHA_LENGTH):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_noise_and_lines(img):
    draw = ImageDraw.Draw(img)

    # Random lines
    for _ in range(10):
        draw.line(
            [(random.randint(0, img.width), random.randint(0, img.height)),
             (random.randint(0, img.width), random.randint(0, img.height))],
            fill=(0, 0, 0), width=1
        )

    # Random dots
    for _ in range(100):
        draw.point(
            (random.randint(0, img.width), random.randint(0, img.height)),
            fill=(random.randint(0, 180), random.randint(0, 180), random.randint(0, 180))
        )

    return img

def generate_and_save_captcha(text):
    captcha = ImageCaptcha(width=280, height=90)
    img = captcha.generate_image(text)
    #img = add_noise_and_lines(img)
    #img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    path = os.path.join(OUTPUT_DIR, f"{text}.png")
    img.save(path)
    return path

def read_captcha_with_tesseract(image_path):
    try:
        img = Image.open(image_path).convert('L')  # Convert to grayscale
        extracted_text = pytesseract.image_to_string(img)
        return extracted_text.strip().upper()
    except Exception as e:
        print(f"❌ Error reading {image_path}: {e}")
        return None

def main():
    correct = 0
    total = 0

    print(f"\n🔧 Generating {NUM_CAPTCHAS} captchas and testing with Tesseract...\n")

    for i in range(NUM_CAPTCHAS):
        captcha_text = generate_random_text()
        img_path = generate_and_save_captcha(captcha_text)

        tesseract_output = read_captcha_with_tesseract(img_path)
        ground_truth = captcha_text.upper()

        if tesseract_output:
            normalized = ''.join(filter(str.isalnum, tesseract_output))
            is_correct = normalized == ground_truth
            result = '✅' if is_correct else '❌'
            print(f"[{i+1}/{NUM_CAPTCHAS}] {result} Expected: {ground_truth}, Tesseract: {normalized}")
            if is_correct:
                correct += 1
        else:
            print(f"[{i+1}/{NUM_CAPTCHAS}] ❌ No output for {captcha_text}")

        total += 1

    accuracy = (correct / total) * 100
    print(f"\n📊 Tesseract Accuracy: {accuracy:.2f}% ({correct}/{total})\n")

if __name__ == '__main__':
    main()

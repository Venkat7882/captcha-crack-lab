import os
import random
import string
import boto3
from captcha.image import ImageCaptcha
from PIL import Image, ImageDraw, ImageFilter
import time

# ==== Configuration ====
OUTPUT_DIR = r'<<your folder path>>'
NUM_CAPTCHAS = 10
CAPTCHA_LENGTH = 5
AWS_REGION = 'us-east-1'  # Change if needed

# Create output directory if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Textract client
textract = boto3.client('textract', region_name=AWS_REGION)

def generate_random_text(length=CAPTCHA_LENGTH):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def add_noise_and_lines(img):
    draw = ImageDraw.Draw(img)

    for _ in range(10):
        x1, y1 = random.randint(0, img.width), random.randint(0, img.height)
        x2, y2 = random.randint(0, img.width), random.randint(0, img.height)
        draw.line(((x1, y1), (x2, y2)), fill=(0, 0, 0), width=1)

    for _ in range(100):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        draw.point((x, y), fill=(random.randint(0, 180), random.randint(0, 180), random.randint(0, 180)))

    return img

def generate_and_save_captcha(text):
    captcha = ImageCaptcha(width=280, height=90)

    #img = captcha.generate_image(text)
    #img = add_noise_and_lines(img)
    #img = img.filter(ImageFilter.GaussianBlur(radius=0.6))

    file_path = os.path.join(OUTPUT_DIR, f'{text}.png')
    captcha.write(text, file_path)
    #img.save(file_path)
    return file_path

def read_captcha_with_textract(image_path):
    with open(image_path, 'rb') as img_file:
        bytes_data = img_file.read()

    try:
        response = textract.detect_document_text(Document={'Bytes': bytes_data})
        detected = ''
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                detected += block['Text'].strip().upper()
        return detected
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return None

def main():
    correct = 0
    total = 0

    print(f"\n🔧 Generating {NUM_CAPTCHAS} captchas and testing with Amazon Textract...\n")

    for i in range(NUM_CAPTCHAS):
        captcha_text = generate_random_text()
        img_path = generate_and_save_captcha(captcha_text)
        
        time.sleep(0.2)  # Optional throttle to avoid hitting API too fast
        textract_output = read_captcha_with_textract(img_path)

        # Compare only alphanumeric uppercase
        ground_truth = captcha_text.upper()
        if textract_output:
            normalized_output = ''.join(filter(str.isalnum, textract_output)).upper()
            is_correct = normalized_output == ground_truth
            result = '✅' if is_correct else '❌'
            print(f"[{i+1}/{NUM_CAPTCHAS}] {result} Expected: {ground_truth}, Textract: {normalized_output}")
            if is_correct:
                correct += 1
        else:
            print(f"[{i+1}/{NUM_CAPTCHAS}] ❌ No Textract output for {captcha_text}")

        total += 1

    accuracy = (correct / total) * 100
    print(f"\n📊 Textract Accuracy: {accuracy:.2f}% ({correct}/{total})\n")

if __name__ == '__main__':
    main()

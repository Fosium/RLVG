import json
import os
from time import sleep
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print("Everything is imported")

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)
xpath = '//*[self::a or self::button or @onclick or @role="button" or @role="search" or @role="presentation"]'

# takes a website from the list and makes a directory named the url with the screenshot, images, and dataset

urls = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "chatgpt.com",
    "wikipedia.org",
    "reddit.com",
    "x.com",
    "whatsapp.com",
    "bing.com",
    "amazon.com",
    "duckduckgo.com",
    "yahoo.co.jp",
    "tiktok.com",
    "yandex.ru",
    "msn.com",
    "weather.com",
    "netflix.com",
    "temu.com"
]


# urls
for url in urls:
    print(f"Working on {url}")
    os.makedirs(url, exist_ok = True)
    driver.get("https://"+url)
    sleep(3)  # wait for load

    # find clickable elements
    elements = driver.find_elements(By.XPATH, xpath)

    # screenshot
    screenshot_path = url + "/fullscreen.png"
    driver.save_screenshot(screenshot_path)

    # load image for cropping
    image = Image.open(screenshot_path)

    dataset = []
    output_folder = url + "/element_images"
    os.makedirs(output_folder, exist_ok=True)

    def is_in_viewport(driver, element):
        return driver.execute_script("""
            const elem = arguments[0];
            const rect = elem.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        """, element)

    # process every element
    for idx, elem in enumerate(elements):
        try:
            if not is_in_viewport(driver, elem):
                print(idx, "not in view")
                continue

            text = elem.text.strip()
            if not text:
                text = elem.get_attribute("aria-label") or "no-label"

            loc = elem.location
            size = elem.size

            if size['width'] < 5 or size['height'] < 5:
                continue  # tiny/invisible

            if text == "no-label":
                continue

            x, y = int(loc['x']), int(loc['y'])
            w, h = int(size['width']), int(size['height'])

            # crop element
            cropped_img = image.crop((x, y, x + w, y + h))
            img_name = f"{output_folder}/element_{idx}.png"
            cropped_img.save(img_name)

            dataset.append({
                "text": text,
                "coordinates": {"x": x, "y": y, "width": w, "height": h},
                "image_path": img_name
            })

        except Exception as e:
            print(f"Error processing element {idx}: {e}")
            continue

    # save to json
    with open(url+"/elements_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)

    print(f"Done!!! {len(dataset)} clickable elements saved.")
    
driver.quit()

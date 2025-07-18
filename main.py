# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, ValidationError
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import json
import os

from fastapi.middleware.cors import CORSMiddleware

from models import WebsiteURL, BrandContext, Product, FAQItem, SocialHandle
from llm_utils import load_llm_model, call_llm

app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "null",
    "file://",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        load_llm_model()
    except Exception as e:
        print(f"Error during LLM model startup: {e}")

async def _fetch_html_content(url: str) -> BeautifulSoup:
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.MissingSchema:
        raise HTTPException(status_code=400, detail="Invalid URL: Missing http:// or https:// schema.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=401, detail="Website not found or unable to connect.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request to website timed out.")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error fetching {url}: {e.response.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error fetching {url}: {e}")

async def _fetch_product_catalog(base_url: str) -> List[Product]:
    products_url = f"{base_url.rstrip('/')}/products.json"
    product_catalog = []

    try:
        response = requests.get(products_url, timeout=10)
        response.raise_for_status()
        products_data = response.json()
        if not products_data or 'products' not in products_data:
            return []

        for product_json in products_data['products']:
            title = product_json.get('title', "Untitled Product")
            description = BeautifulSoup(product_json.get('body_html', ''), 'html.parser').get_text(separator=' ', strip=True)
            price = product_json.get('variants', [{}])[0].get('price')
            image_src = None
            if product_json.get('images'):
                try:
                    image_src = HttpUrl(product_json['images'][0]['src'])
                except ValidationError:
                    pass

            product_catalog.append(Product(
                title=title,
                price=price,
                image_src=image_src,
                description=description
            ))
        return product_catalog
    except requests.exceptions.RequestException as e:
        print(f"Error fetching products.json from {products_url}: {e}")
        return []
    except (ValueError, ValidationError, Exception) as e:
        print(f"Error processing product catalog from {products_url}: {e}")
        return []

async def _extract_hero_products(soup: BeautifulSoup) -> List[Product]:
    hero_products = []
    product_card_elements = soup.find_all(class_=re.compile(r'(product-card|grid__item|product-item)'))

    for card in product_card_elements[:3]:
        title = card.find(class_=re.compile(r'(product-card__title|product-item-title|product-title)'))
        price = card.find(class_=re.compile(r'(price-item|product-card__price|product-price)'))
        img_tag = card.find('img')

        title_text = title.get_text(strip=True) if title else None
        price_text = price.get_text(strip=True) if price else None
        img_src = img_tag['src'] if img_tag and 'src' in img_tag else None

        if title_text:
            try:
                hero_products.append(Product(
                    title=title_text,
                    price=price_text,
                    image_src=HttpUrl(img_src) if img_src else None
                ))
            except ValidationError:
                pass
    return hero_products

async def _extract_policies_and_links(soup: BeautifulSoup, base_url: str) -> Dict[str, str | HttpUrl]:
    policies_and_links = {
        "privacy_policy": None,
        "return_refund_policies": None,
        "important_links": {}
    }

    footer = soup.find('footer') or soup
    links = footer.find_all('a', href=True)

    for link in links:
        href = link['href']
        text = link.get_text(strip=True).lower()
        full_url = requests.compat.urljoin(base_url, href)

        if 'privacy' in text or 'privacy-policy' in href:
            policies_and_links["privacy_policy"] = full_url
            try: policies_and_links["important_links"]["Privacy Policy"] = HttpUrl(full_url)
            except ValidationError: pass
        elif 'return' in text or 'refund' in text or 'return-policy' in href or 'refund-policy' in href:
            policies_and_links["return_refund_policies"] = full_url
            try: policies_and_links["important_links"]["Return/Refund Policy"] = HttpUrl(full_url)
            except ValidationError: pass
        elif 'contact' in text or 'contact-us' in href:
            try: policies_and_links["important_links"]["Contact Us"] = HttpUrl(full_url)
            except ValidationError: pass
        elif 'track' in text or 'order-tracking' in href:
            try: policies_and_links["important_links"]["Order Tracking"] = HttpUrl(full_url)
            except ValidationError: pass
        elif 'blog' in text or 'news' in text and '/blogs/' in href:
            try: policies_and_links["important_links"]["Blog"] = HttpUrl(full_url)
            except ValidationError: pass

    return {
        "privacy_policy_url": HttpUrl(policies_and_links["privacy_policy"]) if policies_and_links["privacy_policy"] else None,
        "return_refund_policies_url": HttpUrl(policies_and_links["return_refund_policies"]) if policies_and_links["return_refund_policies"] else None,
        "important_links": {k: v for k, v in policies_and_links["important_links"].items() if v is not None}
    }

async def _extract_brand_text_and_faqs_with_llm(soup: BeautifulSoup) -> Dict:
    main_content_div = soup.find('main') or soup.find('body')
    if not main_content_div:
        return {"brand_text_context": None, "brand_faqs": []}

    text_for_llm = main_content_div.get_text(separator=' ', strip=True)[:4000]

    system_prompt = (
        "Extract brand's 'About Us' text and any FAQs with answers. "
        "Output JSON with 'brand_text_context' (string) and 'brand_faqs' (array of {question, answer}). "
        "Use null for text context and empty array for FAQs if not found. Ensure JSON is perfect."
    )
    user_prompt = f"Extract brand context and FAQs from:\n\n{text_for_llm}"

    llm_output = call_llm(system_prompt=system_prompt, user_prompt=user_prompt)

    brand_text_context = None
    brand_faqs = []

    if llm_output:
        if 'brand_text_context' in llm_output and llm_output['brand_text_context'] not in ["", "null", None]:
            brand_text_context = llm_output['brand_text_context']
        if 'brand_faqs' in llm_output and isinstance(llm_output['brand_faqs'], list):
            for item in llm_output['brand_faqs']:
                if isinstance(item, dict) and 'question' in item and 'answer' in item:
                    try:
                        brand_faqs.append(FAQItem(question=item['question'], answer=item['answer']))
                    except ValidationError:
                        pass
    
    return {
        "brand_text_context": brand_text_context,
        "brand_faqs": brand_faqs
    }

async def _extract_social_and_contact_details(soup: BeautifulSoup) -> Dict:
    social_handles = []
    contact_emails = []
    contact_phones = []

    social_platforms = {
        'instagram': r'instagram\.com', 'facebook': r'facebook\.com', 'tiktok': r'tiktok\.com',
        'twitter|x': r'(twitter\.com|x\.com)', 'youtube': r'youtube\.com', 'linkedin': r'linkedin\.com'
    }

    for tag in soup.find_all('a', href=True):
        href = tag['href']
        for platform, pattern in social_platforms.items():
            if re.search(pattern, href, re.IGNORECASE):
                try: social_handles.append(SocialHandle(platform=platform.replace('|x',''), url=HttpUrl(href)))
                except ValidationError: pass
                break

    page_text = soup.get_text(separator=' ', strip=True)

    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
    contact_emails.extend(set(emails))

    phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})', page_text)
    contact_phones.extend(list(set("".join(m).strip() for m in phones if "".join(m).strip())))

    return {
        "social_handles": social_handles,
        "contact_details": {
            "emails": contact_emails,
            "phone_numbers": contact_phones
        }
    }

@app.post("/shopify-insights", response_model=BrandContext)
async def get_shopify_insights(url: WebsiteURL):
    website_url = str(url.website_url)
    brand_context_data = BrandContext()

    soup = await _fetch_html_content(website_url)

    brand_context_data.product_catalog = await _fetch_product_catalog(website_url)
    brand_context_data.hero_products = await _extract_hero_products(soup)

    extracted_policy_links = await _extract_policies_and_links(soup, website_url)
    brand_context_data.important_links.update(extracted_policy_links.get("important_links", {}))

    policy_text_for_llm = soup.get_text(separator=' ', strip=True)[:4000]
    policy_system_prompt = (
        "Extract 'Privacy Policy' and 'Return/Refund Policy' content. "
        "Output JSON with 'privacy_policy_content' and 'return_refund_policies_content'. "
        "Use null if not found. Ensure JSON is perfect."
    )
    policy_user_prompt = f"Extract policy content from:\n\n{policy_text_for_llm}"
    llm_policy_output = call_llm(system_prompt=policy_system_prompt, user_prompt=policy_user_prompt)

    if llm_policy_output:
        brand_context_data.privacy_policy = llm_policy_output.get('privacy_policy_content')
        brand_context_data.return_refund_policies = llm_policy_output.get('return_refund_policies_content')

    llm_brand_faqs_context = await _extract_brand_text_and_faqs_with_llm(soup)
    brand_context_data.brand_faqs = llm_brand_faqs_context.get("brand_faqs", [])
    brand_context_data.brand_text_context = llm_brand_faqs_context.get("brand_text_context")

    contact_social_details = await _extract_social_and_contact_details(soup)
    brand_context_data.social_handles = contact_social_details.get("social_handles", [])
    brand_context_data.contact_details = contact_social_details.get("contact_details", {})

    output_folder = "shopify_insights_output"
    os.makedirs(output_folder, exist_ok=True)

    sanitized_url = re.sub(r'[^a-zA-Z0-9]', '_', website_url).strip('_')
    if len(sanitized_url) > 100:
        sanitized_url = sanitized_url[:100]

    output_filename = os.path.join(output_folder, f"{sanitized_url}_insights.json")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(brand_context_data.model_dump_json(indent=4))
        print(f"Insights saved to {output_filename}")
    except Exception as e:
        print(f"Error saving insights to file: {e}")

    return brand_context_data
# models.py
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional

class WebsiteURL(BaseModel):
    website_url: HttpUrl

class Product(BaseModel):
    title: str
    price: Optional[str] = None
    image_src: Optional[HttpUrl] = None
    description: Optional[str] = None

class FAQItem(BaseModel):
    question: str
    answer: str

class SocialHandle(BaseModel):
    platform: str
    url: HttpUrl

class BrandContext(BaseModel):
    product_catalog: List[Product] = []
    hero_products: List[Product] = []
    privacy_policy: Optional[str] = None
    return_refund_policies: Optional[str] = None
    brand_faqs: List[FAQItem] = []
    social_handles: List[SocialHandle] = []
    contact_details: Dict[str, List[str]] = {}
    brand_text_context: Optional[str] = None
    important_links: Dict[str, HttpUrl] = {}
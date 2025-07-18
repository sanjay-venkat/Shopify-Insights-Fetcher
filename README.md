Got it. I will ensure the project name is correctly used and `gitignore` is not included in the main `README.md` content, but rather mentioned in the Project Structure for clarity.

Here's the refined README.md.

-----

````markdown
# Shopify Insights Fetcher

## Project Overview

This project implements a Python application using the FastAPI framework to extract comprehensive insights from any given Shopify e-commerce store URL. Developed as part of a GenAI Developer Intern Assignment, it focuses on building a robust, maintainable, and scalable backend system capable of fetching various data points, including product catalogs, brand policies, social media presence, and general brand context.

A key aspect of this solution is the integration of a local Large Language Model (LLM) – specifically, TinyLlama – to intelligently structure and extract information from less organized web content, such as FAQs and descriptive brand text.

## Features

The application successfully fetches and processes the following mandatory insights/datapoints from Shopify stores:

1.  **Whole Product Catalog:** Retrieves a comprehensive list of products available in the store by leveraging the `/products.json` endpoint. Each product includes details like title, price, image, and description.
2.  **Hero Products:** Identifies and extracts information about prominent or featured products displayed directly on the store's homepage.
3.  **Privacy Policy:** Extracts the full text content of the store's Privacy Policy.
4.  **Return & Refund Policies:** Extracts the full text content of the store's Return and Refund Policies.
5.  **Brand FAQs:** Uses an LLM to identify and list Frequently Asked Questions (FAQs) along with their corresponding answers, even from unstructured text.
6.  **Social Handles:** Scans the website for links to various social media platforms (e.g., Instagram, Facebook, TikTok, Twitter/X, YouTube, LinkedIn), providing their URLs.
7.  **Contact Details:** Extracts available contact information such as email address(es) and phone number(s) found on the website.
8.  **Brand Text Context:** Leverages an LLM to extract "About Us" or general descriptive text about the brand from the website.
9.  **Important Links:** Identifies and provides URLs for key pages like Order Tracking, Contact Us, and Blog sections.

### Project Adherence to Guidelines

* **Language & Framework:** Python with FastAPI.
* **Demoable APIs:** Provided with a simple `index.html` UI for easy demonstration.
* **Backend Focus:** Designed with an emphasis on backend logic, data extraction, and LLM integration.
* **Best Practices:** Adheres to principles of clean code, modular structure (using Pydantic models), and RESTful API design. Edge-case handling for network errors and invalid URLs is implemented.
* **Pydantic Models:** Extensively uses Pydantic for robust data validation and clear API response structuring.
* **Code Readability & Structure:** Code is organized into `main.py`, `models.py`, and `llm_utils.py` for logical separation.

## How It Works

1.  **URL Input:** The user provides a Shopify store URL via a simple HTML interface.
2.  **HTML Fetching:** The backend uses `requests` and `BeautifulSoup` to fetch and parse the store's HTML content.
3.  **Product Catalog:** It makes a direct API call to the store's `/products.json` endpoint to get the comprehensive product list.
4.  **Static Data Extraction:** Common elements like hero products, social links, and contact details are extracted using `BeautifulSoup` and regular expressions.
5.  **LLM-Powered Extraction:** For unstructured or semi-structured data (like policies, FAQs, and general brand context), a locally hosted TinyLlama model (via `llama-cpp-python`) is employed. The model is prompted to extract and format this information into a structured JSON.
    * **Automatic Model Download:** The TinyLlama model (`tinyllama-1.1b-chat-v0.3.Q4_K_M.gguf`) is automatically downloaded from Hugging Face Hub (`TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF`) into the `models/` directory upon the first run if not already present.
6.  **JSON Output & Persistence:** All extracted insights are compiled into a `BrandContext` Pydantic model. This JSON response is sent back to the frontend and also saved as a `.json` file within the `shopify_insights_output/` directory in the project root for local persistence.

## Getting Started

Follow these steps to set up and run the Shopify Insights Fetcher locally.

### Prerequisites

* Python 3.9+ (or newer)
* `pip` (Python package installer)

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/Shopify-Insights-Fetcher.git](https://github.com/your-username/Shopify-Insights-Fetcher.git)
    cd Shopify-Insights-Fetcher
    ```
    *(Remember to replace `your-username` with your actual GitHub username)*

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.

    * **On Windows:**
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install Dependencies:**
    Install all required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: This step will also install `llama-cpp-python`, which is crucial for running the local LLM.)*

4.  **Initial LLM Model Download:**
    The first time you run the application, the `tinyllama-1.1b-chat-v0.3.Q4_K_M.gguf` model (approx. 600MB) will automatically download into the `models/` folder. This might take a few minutes depending on your internet connection.

### Running the Application

1.  **Start the FastAPI Server:**
    Ensure your virtual environment is activated, then run:
    ```bash
    uvicorn main:app --reload
    ```
    The server will typically run on `http://127.0.0.1:8000`.

2.  **Access the Web UI:**
    Open the `index.html` file located in your project directory in your web browser. You can usually do this by navigating to the file path (e.g., `file:///C:/Path/To/Your/Project/index.html`) or by dragging the file into your browser.

    Enter a Shopify store URL (e.g., `https://hairoriginals.com`) into the input field and click "Get Insights". The extracted JSON data will be displayed on the page.

## API Endpoint Reference

The core functionality is exposed via a single POST endpoint.

### `POST /shopify-insights`

Fetches comprehensive brand insights from a given Shopify website URL.

* **URL:** `http://127.0.0.1:8000/shopify-insights`
* **Method:** `POST`
* **Content-Type:** `application/json`

#### Request Body

The request body should be a JSON object with a `website_url` field.

```json
{
  "website_url": "[https://example.myshopify.com](https://example.myshopify.com)"
}
````

#### Example `curl` Request

```bash
curl -X POST "[http://127.0.0.1:8000/shopify-insights](http://127.0.0.1:8000/shopify-insights)" \
     -H "Content-Type: application/json" \
     -d '{"website_url": "[https://hairoriginals.com](https://hairoriginals.com)"}'
```

#### Success Response (Status: 200 OK)

Returns a JSON object structured according to the `BrandContext` Pydantic model.

```json
{
  "product_catalog": [
    {
      "title": "Clip-In Hair Streaks | Pack of 4 | 100% Human Hair Extensions",
      "price": "1350.00",
      "image_src": "[https://cdn.shopify.com/s/files/](https://cdn.shopify.com/s/files/)...",
      "description": "Ready to elevate your look without any damage to your natural hair?..."
    }
    // ... truncated for brevity, full structure defined by models.py
  ],
  "hero_products": [
    // ... products from homepage
  ],
  "privacy_policy": "...",
  "return_refund_policies": "...",
  "brand_faqs": [
    {
      "question": "Q) Do you have COD as a payment option?",
      "answer": "A) Yes, we do have"
    }
    // ... more FAQs
  ],
  "social_handles": [
    {
      "platform": "instagram",
      "url": "[https://www.instagram.com/hairoriginals_official/](https://www.instagram.com/hairoriginals_official/)"
    }
    // ... more social handles
  ],
  "contact_details": {
    "emails": ["support@hairoriginals.com"],
    "phone_numbers": ["+91 99990 00000"]
  },
  "brand_text_context": "...",
  "important_links": {
    "Contact Us": "[https://hairoriginals.com/pages/contact-us](https://hairoriginals.com/pages/contact-us)",
    "Blog": "[https://hairoriginals.com/blogs/news](https://hairoriginals.com/blogs/news)"
  }
}
```

#### Error Responses

  * **400 Bad Request:**
    ```json
    {
      "detail": "Invalid URL: Missing http:// or https:// schema."
    }
    ```
  * **401 Unauthorized/Website Not Found:**
    ```json
    {
      "detail": "Website not found or unable to connect."
    }
    ```
  * **500 Internal Server Error:**
    ```json
    {
      "detail": "Internal server error while fetching content from [URL]: [error_message]"
    }
    ```
  * **504 Gateway Timeout:**
    ```json
    {
      "detail": "Request to website timed out."
    }
    ```

## Project Structure

```
.
├── main.py                    # Main FastAPI application, API routes, and orchestration of data extraction.
├── models.py                  # Pydantic models for request body, response structure, and data validation.
├── llm_utils.py               # Utility functions for LLM interaction, model loading, and JSON parsing from LLM output.
├── index.html                 # Simple HTML UI for demonstrating the API.
├── requirements.txt           # Python package dependencies.
├── .gitignore                 # Specifies intentionally untracked files to ignore from Git (e.g., .venv/, models/, output files).
├── models/                    # Directory where the LLM model will be downloaded.
└── shopify_insights_output/   # Directory where generated JSON insight files are saved.
```

## Future Enhancements (Bonus Section Reflections)

The assignment outlines two bonus requirements that could be implemented to further enhance the application:

1.  **Competitor Analysis:** Extending the application to identify and fetch insights for competitors of a given brand would add significant value. This could involve integrating with web search APIs or more sophisticated scraping techniques.
2.  **Persist data in a SQL DB:** Currently, insights are saved to local JSON files. Integrating a SQL database (e.g., MySQL, as preferred in the guidelines) would enable more robust data management, querying, and scalability for storing extracted insights.

## Technologies Used

  * **Python 3.9+**
  * **FastAPI:** Web framework for building the API.
  * **Pydantic:** Data validation and settings management.
  * **Requests:** HTTP library for making web requests.
  * **BeautifulSoup4:** HTML parsing library.
  * **llama-cpp-python:** Python bindings for `llama.cpp`, enabling local LLM inference.
  * **Hugging Face Hub:** For programmatically downloading the TinyLlama model.

## Author

Sanjay Venkat S

## License

This project is open-sourced under the MIT License. See the `LICENSE` file for more details.

```
```

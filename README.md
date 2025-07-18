### **Shopify Insights Fetcher**

markdown

## Project Overview

This project implements a Python application using the FastAPI framework to extract comprehensive insights from any given Shopify e-commerce store URL. [cite_start]Developed as part of a GenAI Developer Intern Assignment[cite: 1], it focuses on building a robust, maintainable, and scalable backend system capable of fetching various data points, including product catalogs, brand policies, social media presence, and general brand context.

[cite_start]A key aspect of this solution is the integration of a local Large Language Model (LLM) – specifically, TinyLlama – to intelligently structure and extract information from less organized web content, such as FAQs and descriptive brand text[cite: 43].

## Features

[cite_start]The application successfully fetches and processes the following mandatory insights/datapoints from Shopify stores[cite: 21]:

1.  [cite_start]**Whole Product Catalog:** Retrieves a comprehensive list of products available in the store by leveraging the `/products.json` endpoint[cite: 22, 40]. Each product includes details like title, price, image, and description.
2.  [cite_start]**Hero Products:** Identifies and extracts information about prominent or featured products displayed directly on the store's homepage[cite: 23].
3.  [cite_start]**Privacy Policy:** Extracts the full text content of the store's Privacy Policy[cite: 24].
4.  [cite_start]**Return & Refund Policies:** Extracts the full text content of the store's Return and Refund Policies[cite: 25].
5.  [cite_start]**Brand FAQs:** Uses an LLM to identify and list Frequently Asked Questions (FAQs) along with their corresponding answers, even from unstructured text[cite: 26, 43].
6.  [cite_start]**Social Handles:** Scans the website for links to various social media platforms (e.g., Instagram, Facebook, Tiktok (Outside India brands), Twitter/X, YouTube, LinkedIn), providing their URLs[cite: 28].
7.  [cite_start]**Contact Details:** Extracts available contact information such as email address(es) and phone number(s) found on the website[cite: 29].
8.  [cite_start]**Brand Text Context:** Leverages an LLM to extract "About Us" or general descriptive text about the brand from the website[cite: 30, 43].
9.  [cite_start]**Important Links:** Identifies and provides URLs for key pages like Order Tracking, Contact Us, and Blog sections[cite: 31].

### Project Adherence to Guidelines

* [cite_start]**Language & Framework:** Python with FastAPI[cite: 4].
* [cite_start]**Demoable APIs:** Provided with a simple `index.html` UI for easy demonstration[cite: 6].
* [cite_start]**Backend Focus:** Designed with an emphasis on backend logic, data extraction, and LLM integration[cite: 7].
* **Best Practices:** Adheres to principles of clean code, modular structure (using Pydantic models), and RESTful API design. [cite_start]Edge-case handling for network errors and invalid URLs is implemented[cite: 8, 9].
* [cite_start]**Pydantic Models:** Extensively uses Pydantic for robust data validation and clear API response structuring[cite: 9].
* [cite_start]**Code Readability & Structure:** Code is organized into `main.py`, `models.py`, and `llm_utils.py` for logical separation[cite: 9].

## How It Works

1.  **URL Input:** The user provides a Shopify store URL via a simple HTML interface.
2.  **HTML Fetching:** The backend uses `requests` and `BeautifulSoup` to fetch and parse the store's HTML content.
3.  [cite_start]**Product Catalog:** It makes a direct API call to the store's `/products.json` endpoint to get the comprehensive product list[cite: 40].
4.  **Static Data Extraction:** Common elements like hero products, social links, and contact details are extracted using `BeautifulSoup` and regular expressions.
5.  [cite_start]**LLM-Powered Extraction:** For unstructured or semi-structured data (like policies, FAQs, and general brand context), a locally hosted TinyLlama model (via `llama-cpp-python`) is employed[cite: 43]. The model is prompted to extract and format this information into a structured JSON.
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
    # Replace 'your-username' with your actual GitHub username
    ```

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
    ```bash
    pip install -r requirements.txt
    # This includes 'llama-cpp-python' for LLM support.
    ```

4.  **Initial LLM Model Download:**
    The TinyLlama model (approx. 600MB) will automatically be downloaded to the `models/` folder during the first API call if not already present. This might take a few minutes depending on your internet connection.

### Running the Application

1.  **Start FastAPI Server:**
    Ensure your virtual environment is activated, then run:
    ```bash
    uvicorn main:app --reload
    ```
    The server will typically run on `http://127.0.0.1:8000`.

2.  **Use the UI:**
    Open the `index.html` file located in your project directory in your web browser. You can usually do this by navigating to the file path (e.g., `file:///C:/Path/To/Your/Project/index.html`) or by dragging the file into your browser.

    Enter a Shopify store URL (e.g., `https://hairoriginals.com`) into the input field and click "Get Insights" to see the JSON output.

## API Endpoint Reference

[cite_start]The core functionality is exposed via a single POST endpoint[cite: 33].

### `POST /shopify-insights`

Fetches comprehensive brand insights from a given Shopify website URL.

* **URL:** `http://127.0.0.1:8000/shopify-insights`
* **Method:** `POST`
* **Content-Type:** `application/json`

#### Request Example

```json
{
  "website_url": "[https://hairoriginals.com](https://hairoriginals.com)"
}
````

#### Example `curl` Command

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
    // ... More products (truncated for brevity, full structure defined by models.py)
  ],
  "hero_products": [
    /* ... */
  ],
  "privacy_policy": "...",
  "return_refund_policies": "...",
  "brand_faqs": [
    {
      "question": "Do you have COD as a payment option?",
      "answer": "Yes, we do have"
    }
  ],
  "social_handles": [
    {
      "platform": "instagram",
      "url": "[https://www.instagram.com/hairoriginals_official/](https://www.instagram.com/hairoriginals_official/)"
    }
  ],
  "contact_details": {
    "emails": [
      "support@hairoriginals.com"
    ],
    "phone_numbers": [
      "+91 99990 00000"
    ]
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
  * **401 Unauthorized:**
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
├── main.py                    # Main FastAPI application with API routes and orchestration logic.
├── models.py                  # Pydantic models for request/response validation and structuring.
├── llm_utils.py               # Utility functions for local LLM (TinyLlama) interaction.
├── index.html                 # Simple HTML-based user interface for demonstration.
├── requirements.txt           # Lists all Python package dependencies.
├── .gitignore                 # Specifies files and directories to be ignored by Git (e.g., .venv/, models/, output files).
├── models/                    # Directory where the TinyLlama LLM model is downloaded upon first run.
└── shopify_insights_output/   # Local folder for storing generated JSON insight responses.
```

## Future Enhancements (Bonus Section Reflections)

[cite\_start]The assignment outlines two bonus requirements that could be implemented to further enhance the application[cite: 44]:

1.  **Competitor Analysis:** Extend the application to identify and fetch insights for competitors of a given brand (brand's website). [cite\_start]This could involve integrating with web search APIs or some other better logic, if applicable, to then get the same insights for its competitors' webstores also[cite: 45, 46].
2.  **SQL Database Integration:** Currently, insights are saved to local JSON files. [cite\_start]Integrating a SQL database (e.g., MySQL, as preferred in the guidelines [cite: 5][cite\_start]) would enable more robust data management, querying, and scalability for storing extracted insights[cite: 47].

## Technologies Used

  * [cite\_start]**Python 3.9+** [cite: 4]
  * [cite\_start]**FastAPI:** Web framework for building the API[cite: 4].
  * [cite\_start]**Pydantic:** Data validation and settings management[cite: 9].
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

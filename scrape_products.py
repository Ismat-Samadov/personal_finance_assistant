import asyncio
import aiohttp
import csv
import json
from typing import List, Dict
from datetime import datetime

API_URL = "https://premium-api-production.up.railway.app/products"
TOTAL_PAGES = 213  # Actual total pages from API
CONCURRENT_REQUESTS = 10  # Limit concurrent requests to avoid overwhelming the server

async def fetch_page(session: aiohttp.ClientSession, page: int, semaphore: asyncio.Semaphore) -> Dict:
    """Fetch a single page of products"""
    payload = {
        "lang": "az",
        "page": page,
        "sort": "",
        "limit": 30,
        "filter_category": 4,
        "param_srsltid": "AfmBOoqYkwwKtgLjHJ8RJc6S5lAOiqf3tQRSuSaQe_fRqarwzprfL8e0"
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.premiumoutlet.az"
    }

    async with semaphore:
        try:
            async with session.post(API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Page {page}/{TOTAL_PAGES} fetched ({len(data.get('data', {}).get('items', []))} items)")
                    return data
                else:
                    print(f"✗ Page {page} failed with status {response.status}")
                    return None
        except Exception as e:
            print(f"✗ Page {page} error: {str(e)}")
            return None

def flatten_product(product: Dict) -> Dict:
    """Flatten product data for CSV export"""
    flattened = {
        'id': product.get('id'),
        'title': product.get('title'),
        'route': product.get('route'),
        'brandName': product.get('brandName'),
        'brand_title': product.get('brand', {}).get('title'),
        'brand_route': product.get('brand', {}).get('route'),
        'price': product.get('price'),
        'priceOld': product.get('priceOld'),
        'discount': product.get('discount'),
        'maxPrice': product.get('maxPrice'),
        'minPrice': product.get('minPrice'),
        'maxPriceOld': product.get('maxPriceOld'),
        'minPriceOld': product.get('minPriceOld'),
        'newIn': product.get('newIn'),
        'monoBrand': product.get('monoBrand'),
        'priceInStore': product.get('priceInStore'),
        'season': product.get('season'),
        'colection': product.get('colection'),
        'line': product.get('line'),
        'item': product.get('item'),
        'model': product.get('model'),
        'article': product.get('article'),
        'warehouse': product.get('warehouse'),
        'image': product.get('image'),
        'mannequins': product.get('mannequins'),
        'outfit': product.get('outfit'),
        'hasVariantPrice': product.get('hasVariantPrice'),
        'beautyDiscount': product.get('beautyDiscount'),
        'discountId': product.get('discountId'),
        # Size table info
        'sizeTable_name': product.get('sizeTable', {}).get('name'),
        'sizeTable_title': product.get('sizeTable', {}).get('title'),
        'sizeTable_show': product.get('sizeTable', {}).get('show'),
        # Variants (join sizes)
        'available_sizes': ', '.join([v.get('siteSize', '') for v in product.get('variants', [])]),
        'variant_count': len(product.get('variants', [])),
        # Images (join image URLs)
        'images': ', '.join([img.get('source', '') for img in product.get('images', [])]),
        'image_count': len(product.get('images', [])),
    }

    return flattened

async def scrape_all_pages() -> List[Dict]:
    """Scrape all pages concurrently"""
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    all_products = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, page, semaphore) for page in range(1, TOTAL_PAGES + 1)]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result and result.get('ok'):
                items = result.get('data', {}).get('items', [])
                all_products.extend(items)

    return all_products

def save_to_csv(products: List[Dict], filename: str):
    """Save products to CSV file"""
    if not products:
        print("No products to save!")
        return

    flattened_products = [flatten_product(p) for p in products]

    # Get all unique keys from all products
    fieldnames = set()
    for product in flattened_products:
        fieldnames.update(product.keys())

    fieldnames = sorted(fieldnames)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_products)

    print(f"\n✓ Saved {len(products)} products to {filename}")

async def main():
    print(f"Starting scrape of {TOTAL_PAGES} pages...")
    print(f"Concurrent requests: {CONCURRENT_REQUESTS}\n")

    start_time = datetime.now()

    products = await scrape_all_pages()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n{'='*60}")
    print(f"Scraping completed in {duration:.2f} seconds")
    print(f"Total products fetched: {len(products)}")
    print(f"{'='*60}\n")

    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"premium_outlet_products_{timestamp}.csv"
    save_to_csv(products, filename)

    # Also save raw JSON for backup
    json_filename = f"premium_outlet_products_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved raw data to {json_filename}")

if __name__ == "__main__":
    asyncio.run(main())

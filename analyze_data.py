import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Load the data
print("Loading data...")
df = pd.read_csv('premium_outlet_products_20251130_224700.csv')

print(f"Total records: {len(df)}")
print(f"Columns: {len(df.columns)}")

# Clean data
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['priceOld'] = pd.to_numeric(df['priceOld'], errors='coerce')
df['discount'] = pd.to_numeric(df['discount'], errors='coerce')

# Create insights dictionary
insights = {}

# 1. PRICE DISTRIBUTION
print("\n1. Creating Price Distribution chart...")
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
df['price'].dropna().hist(bins=50, edgecolor='black', color='#2E86AB')
plt.xlabel('Price (AZN)', fontsize=12, fontweight='bold')
plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
plt.title('Price Distribution of Products', fontsize=14, fontweight='bold', pad=20)
plt.axvline(df['price'].median(), color='red', linestyle='--', linewidth=2, label=f'Median: {df["price"].median():.2f} AZN')
plt.axvline(df['price'].mean(), color='green', linestyle='--', linewidth=2, label=f'Mean: {df["price"].mean():.2f} AZN')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
price_ranges = pd.cut(df['price'].dropna(), bins=[0, 50, 100, 200, 500, 1000, df['price'].max()],
                      labels=['0-50', '50-100', '100-200', '200-500', '500-1000', '1000+'])
price_range_counts = price_ranges.value_counts().sort_index()
colors = sns.color_palette("viridis", len(price_range_counts))
price_range_counts.plot(kind='bar', color=colors, edgecolor='black')
plt.xlabel('Price Range (AZN)', fontsize=12, fontweight='bold')
plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
plt.title('Products by Price Range', fontsize=14, fontweight='bold', pad=20)
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('charts/01_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

insights['price'] = {
    'mean': float(df['price'].mean()),
    'median': float(df['price'].median()),
    'min': float(df['price'].min()),
    'max': float(df['price'].max()),
    'std': float(df['price'].std())
}

# 2. TOP BRANDS
print("2. Creating Top Brands chart...")
plt.figure(figsize=(14, 8))
top_brands = df['brand_title'].value_counts().head(15)
colors = sns.color_palette("husl", len(top_brands))
bars = plt.barh(range(len(top_brands)), top_brands.values, color=colors, edgecolor='black', linewidth=1.5)
plt.yticks(range(len(top_brands)), top_brands.index, fontsize=11)
plt.xlabel('Number of Products', fontsize=12, fontweight='bold')
plt.ylabel('Brand', fontsize=12, fontweight='bold')
plt.title('Top 15 Brands by Product Count', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, (bar, value) in enumerate(zip(bars, top_brands.values)):
    plt.text(value + 5, i, str(value), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_top_brands.png', dpi=300, bbox_inches='tight')
plt.close()

insights['top_brands'] = top_brands.head(10).to_dict()

# 3. DISCOUNT ANALYSIS
print("3. Creating Discount Analysis chart...")
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
discount_dist = df[df['discount'] > 0]['discount'].value_counts().sort_index()
colors = sns.color_palette("rocket", len(discount_dist))
plt.bar(discount_dist.index, discount_dist.values, color=colors, edgecolor='black', linewidth=1.5)
plt.xlabel('Discount Percentage (%)', fontsize=12, fontweight='bold')
plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
plt.title('Distribution of Discount Percentages', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='y')

plt.subplot(1, 2, 2)
discount_categories = pd.cut(df['discount'], bins=[-1, 0, 20, 40, 60, 80, 100],
                              labels=['No Discount', '1-20%', '21-40%', '41-60%', '61-80%', '81-100%'])
discount_cat_counts = discount_categories.value_counts().sort_index()
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#6C5CE7']

# Create pie chart without labels, use legend instead
wedges, texts, autotexts = plt.pie(discount_cat_counts, autopct='%1.1f%%',
                                     colors=colors, startangle=140,
                                     textprops={'fontsize': 11, 'fontweight': 'bold'},
                                     pctdistance=0.75)

# Make percentage text white for better visibility
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

# Add legend
plt.legend(discount_cat_counts.index, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
           fontsize=10, frameon=False)
plt.title('Products by Discount Range', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('charts/03_discount_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

insights['discount'] = {
    'avg_discount': float(df[df['discount'] > 0]['discount'].mean()),
    'products_with_discount': int((df['discount'] > 0).sum()),
    'products_without_discount': int((df['discount'] == 0).sum()),
    'max_discount': float(df['discount'].max())
}

# 4. PRODUCT CATEGORIES (ITEMS)
print("4. Creating Product Categories chart...")
plt.figure(figsize=(14, 8))
top_items = df['item'].value_counts().head(12)
colors = sns.color_palette("Set3", len(top_items))
wedges, texts, autotexts = plt.pie(top_items, labels=top_items.index, autopct='%1.1f%%',
                                     colors=colors, startangle=140,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'})
plt.title('Product Categories Distribution (Top 12)', fontsize=14, fontweight='bold', pad=20)
plt.axis('equal')
plt.tight_layout()
plt.savefig('charts/04_product_categories.png', dpi=300, bbox_inches='tight')
plt.close()

insights['top_categories'] = top_items.head(10).to_dict()

# 5. SEASONAL ANALYSIS
print("5. Creating Seasonal Analysis chart...")
plt.figure(figsize=(14, 6))
season_counts = df['season'].value_counts().head(10)
colors = sns.color_palette("coolwarm", len(season_counts))
plt.bar(range(len(season_counts)), season_counts.values, color=colors, edgecolor='black', linewidth=1.5)
plt.xticks(range(len(season_counts)), season_counts.index, rotation=45, ha='right')
plt.xlabel('Season', fontsize=12, fontweight='bold')
plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
plt.title('Products by Season', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, value in enumerate(season_counts.values):
    plt.text(i, value + 10, str(value), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/05_seasonal_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

insights['top_seasons'] = season_counts.head(5).to_dict()

# 6. PRICE VS DISCOUNT CORRELATION
print("6. Creating Price vs Discount chart...")
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
df_discount = df[df['discount'] > 0].copy()
plt.scatter(df_discount['discount'], df_discount['price'], alpha=0.5, color='#E74C3C', s=30)
plt.xlabel('Discount (%)', fontsize=12, fontweight='bold')
plt.ylabel('Current Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Price vs Discount Percentage', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3)

# Add trend line
z = np.polyfit(df_discount['discount'].dropna(), df_discount['price'].dropna(), 1)
p = np.poly1d(z)
plt.plot(df_discount['discount'].sort_values(), p(df_discount['discount'].sort_values()),
         "r--", linewidth=2, label='Trend')
plt.legend()

plt.subplot(1, 2, 2)
# Average price by discount bracket
discount_brackets = pd.cut(df_discount['discount'], bins=[0, 20, 40, 60, 80, 100])
avg_price_by_discount = df_discount.groupby(discount_brackets)['price'].mean()
colors = sns.color_palette("mako", len(avg_price_by_discount))
avg_price_by_discount.plot(kind='bar', color=colors, edgecolor='black', linewidth=1.5)
plt.xlabel('Discount Range (%)', fontsize=12, fontweight='bold')
plt.ylabel('Average Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Average Price by Discount Range', fontsize=14, fontweight='bold', pad=20)
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('charts/06_price_vs_discount.png', dpi=300, bbox_inches='tight')
plt.close()

# 7. TOP EXPENSIVE PRODUCTS BY BRAND
print("7. Creating Top Expensive Products chart...")
plt.figure(figsize=(14, 8))
top_expensive = df.nlargest(15, 'price')[['title', 'brand_title', 'price']].copy()
colors = sns.color_palette("Spectral", len(top_expensive))
bars = plt.barh(range(len(top_expensive)), top_expensive['price'].values, color=colors,
                edgecolor='black', linewidth=1.5)
labels = [f"{row['brand_title'][:20]}" for _, row in top_expensive.iterrows()]
plt.yticks(range(len(top_expensive)), labels, fontsize=10)
plt.xlabel('Price (AZN)', fontsize=12, fontweight='bold')
plt.ylabel('Brand', fontsize=12, fontweight='bold')
plt.title('Top 15 Most Expensive Products', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, (bar, value) in enumerate(zip(bars, top_expensive['price'].values)):
    plt.text(value + 10, i, f'{value:.0f} AZN', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/07_top_expensive_products.png', dpi=300, bbox_inches='tight')
plt.close()

# 8. NEW ITEMS vs OLD ITEMS
print("8. Creating New vs Old Items chart...")
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
new_items = df['newIn'].value_counts()
colors_new = ['#3498DB', '#E74C3C']
labels_new = ['New Items', 'Older Items']
plt.pie(new_items, labels=labels_new, autopct='%1.1f%%', colors=colors_new,
        startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
plt.title('New Items vs Older Items', fontsize=14, fontweight='bold', pad=20)

plt.subplot(1, 2, 2)
# Average price comparison
avg_prices = df.groupby('newIn')['price'].mean()
colors_bar = ['#E74C3C', '#3498DB']
bars = plt.bar(['Older Items', 'New Items'], avg_prices.values, color=colors_bar,
               edgecolor='black', linewidth=2, width=0.6)
plt.ylabel('Average Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Average Price: New vs Older Items', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='y')

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f} AZN', ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('charts/08_new_vs_old_items.png', dpi=300, bbox_inches='tight')
plt.close()

insights['new_items'] = {
    'new_count': int(df['newIn'].sum()),
    'old_count': int((~df['newIn']).sum()),
    'new_percentage': float(df['newIn'].sum() / len(df) * 100)
}

# 9. AVERAGE PRICE BY TOP BRANDS
print("9. Creating Average Price by Brand chart...")
plt.figure(figsize=(14, 8))
top_brands_list = df['brand_title'].value_counts().head(15).index
brand_avg_prices = df[df['brand_title'].isin(top_brands_list)].groupby('brand_title')['price'].mean().sort_values(ascending=True)
colors = sns.color_palette("viridis", len(brand_avg_prices))
bars = plt.barh(range(len(brand_avg_prices)), brand_avg_prices.values, color=colors,
                edgecolor='black', linewidth=1.5)
plt.yticks(range(len(brand_avg_prices)), brand_avg_prices.index, fontsize=11)
plt.xlabel('Average Price (AZN)', fontsize=12, fontweight='bold')
plt.ylabel('Brand', fontsize=12, fontweight='bold')
plt.title('Average Price by Top 15 Brands', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='x')

# Add value labels
for i, (bar, value) in enumerate(zip(bars, brand_avg_prices.values)):
    plt.text(value + 5, i, f'{value:.0f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/09_avg_price_by_brand.png', dpi=300, bbox_inches='tight')
plt.close()

# 10. PRODUCT VARIANTS DISTRIBUTION
print("10. Creating Product Variants chart...")
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
variant_counts = df['variant_count'].value_counts().sort_index().head(10)
colors = sns.color_palette("magma", len(variant_counts))
plt.bar(variant_counts.index, variant_counts.values, color=colors, edgecolor='black', linewidth=1.5)
plt.xlabel('Number of Variants', fontsize=12, fontweight='bold')
plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
plt.title('Products by Number of Variants', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='y')

plt.subplot(1, 2, 2)
max_variants = int(df['variant_count'].max())
if max_variants > 10:
    variant_categories = pd.cut(df['variant_count'], bins=[0, 1, 3, 5, 10, max_variants],
                                labels=['1 variant', '2-3 variants', '4-5 variants', '6-10 variants', '10+ variants'])
else:
    variant_categories = pd.cut(df['variant_count'], bins=[0, 1, 3, 5, max_variants],
                                labels=['1 variant', '2-3 variants', '4-5 variants', f'6-{max_variants} variants'])
variant_cat_counts = variant_categories.value_counts().sort_index()
colors_pie = sns.color_palette("Set2", len(variant_cat_counts))

# Create pie chart with legend instead of labels
wedges, texts, autotexts = plt.pie(variant_cat_counts, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=140,
                                     textprops={'fontsize': 11, 'fontweight': 'bold'},
                                     pctdistance=0.75)

# Make percentage text white for better visibility
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

# Add legend
plt.legend(variant_cat_counts.index, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
           fontsize=10, frameon=False)
plt.title('Variant Range Distribution', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('charts/10_product_variants.png', dpi=300, bbox_inches='tight')
plt.close()

insights['variants'] = {
    'avg_variants': float(df['variant_count'].mean()),
    'max_variants': int(df['variant_count'].max()),
    'products_with_multiple_variants': int((df['variant_count'] > 1).sum())
}

# 11. SAVINGS ANALYSIS
print("11. Creating Savings Analysis chart...")
df['savings'] = df['priceOld'] - df['price']
df['savings_pct'] = (df['savings'] / df['priceOld'] * 100).fillna(0)

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
savings_data = df[df['savings'] > 0]['savings']
plt.hist(savings_data, bins=50, color='#27AE60', edgecolor='black', alpha=0.7)
plt.xlabel('Savings Amount (AZN)', fontsize=12, fontweight='bold')
plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
plt.title('Distribution of Savings', fontsize=14, fontweight='bold', pad=20)
plt.axvline(savings_data.median(), color='red', linestyle='--', linewidth=2,
            label=f'Median: {savings_data.median():.2f} AZN')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
# Top brands by average savings
top_savings_brands = df[df['savings'] > 0].groupby('brand_title')['savings'].agg(['mean', 'count'])
top_savings_brands = top_savings_brands[top_savings_brands['count'] >= 10].nlargest(10, 'mean')
colors = sns.color_palette("summer", len(top_savings_brands))
bars = plt.barh(range(len(top_savings_brands)), top_savings_brands['mean'].values,
                color=colors, edgecolor='black', linewidth=1.5)
plt.yticks(range(len(top_savings_brands)), top_savings_brands.index, fontsize=10)
plt.xlabel('Average Savings (AZN)', fontsize=12, fontweight='bold')
plt.ylabel('Brand', fontsize=12, fontweight='bold')
plt.title('Top 10 Brands by Average Savings', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='x')

for i, (bar, value) in enumerate(zip(bars, top_savings_brands['mean'].values)):
    plt.text(value + 2, i, f'{value:.0f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/11_savings_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

insights['savings'] = {
    'total_potential_savings': float(df['savings'].sum()),
    'avg_savings': float(df[df['savings'] > 0]['savings'].mean()),
    'products_with_savings': int((df['savings'] > 0).sum())
}

# 12. COLLECTION ANALYSIS
print("12. Creating Collection Analysis chart...")
plt.figure(figsize=(14, 6))
collection_counts = df['colection'].value_counts().head(8)
colors = sns.color_palette("pastel", len(collection_counts))
bars = plt.bar(range(len(collection_counts)), collection_counts.values, color=colors,
               edgecolor='black', linewidth=1.5)
plt.xticks(range(len(collection_counts)), collection_counts.index, rotation=45, ha='right')
plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
plt.xlabel('Collection Type', fontsize=12, fontweight='bold')
plt.title('Products by Collection', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, (bar, value) in enumerate(zip(bars, collection_counts.values)):
    plt.text(i, value + 20, str(value), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/12_collection_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# Save insights to JSON
print("\nSaving insights to insights.json...")
with open('insights.json', 'w', encoding='utf-8') as f:
    json.dump(insights, f, indent=2, ensure_ascii=False)

print("\n" + "="*60)
print("ANALYSIS COMPLETE!")
print("="*60)
print(f"\nGenerated 12 charts in the 'charts/' folder")
print(f"Insights saved to 'insights.json'")
print(f"\nKey Statistics:")
print(f"  - Total Products: {len(df):,}")
print(f"  - Unique Brands: {df['brand_title'].nunique()}")
print(f"  - Average Price: {df['price'].mean():.2f} AZN")
print(f"  - Products on Discount: {(df['discount'] > 0).sum():,} ({(df['discount'] > 0).sum()/len(df)*100:.1f}%)")
print(f"  - New Items: {df['newIn'].sum():,} ({df['newIn'].sum()/len(df)*100:.1f}%)")
print(f"  - Total Potential Savings: {df['savings'].sum():,.2f} AZN")
print("="*60)

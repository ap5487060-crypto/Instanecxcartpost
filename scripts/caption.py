"""
caption.py
Generates engaging Hindi+English captions for Instagram/Facebook posts.
Rotates between templates to avoid looking spammy.
"""

import random
from datetime import datetime

HASHTAG_POOLS = {
    "Electronics": "#electronics #gadgets #tech #techdeals #smartphone #earbuds #laptop #indiatech #deals #offer",
    "Fashion": "#fashion #style #ootd #clothing #ethnic #trendy #fashionIndia #deals #offer #shopping",
    "Home & Kitchen": "#home #kitchen #homedecor #kitchentools #homeshopping #interiors #deals #offer #Amazon",
    "Beauty": "#beauty #skincare #makeup #haircare #beautytips #glowup #deals #offer #selfcare",
    "Mobiles & Accessories": "#mobile #smartphone #accessories #phonecase #charging #tech #deals #offer",
    "Toys & Baby": "#toys #baby #kids #babyproducts #parenting #kidstoys #deals #offer",
    "Sports & Fitness": "#fitness #sports #workout #gym #yoga #healthylife #deals #offer",
    "Books": "#books #reading #bookstagram #knowledge #education #deals #offer",
}

COMMON_HASHTAGS = "#onlineshopping #amazonsale #flipkart #discount #bestprice #trending #viral #buyonline #linkInBio"

IG_TEMPLATES = [
    "🔥 {title}\n\n💰 Price: Rs {price} only!\n🛒 Bahut kam keemat mein ek daam ka product!\n\n✅ Order karne ke liye LINK IN BIO click karo 👆\n#AffiliateLink\n{hashtags}\n{common}",
    "🛍️ Aaj ka BEST DEAL!\n\n{title}\n\n💸 Sirf Rs {price}\n⚡ Stock limited hai - jaldi karo!\n\n🔗 LINK IN BIO se order karo 👆\n#AffiliateLink\n{hashtags}\n{common}",
    "✨ {category} mein zabardast deal!\n\n🏷️ {title}\n💰 Price: Rs {price}\n\n👇 Buy karne ke liye bio mein link hai\n#AffiliateLink\n{hashtags}\n{common}",
    "😍 Trending product alert!\n\n{title}\n\n🔥 Rs {price} mein le jao!\n📦 Fast delivery available\n\n👆 LINK IN BIO se order karo\n#AffiliateLink\n{hashtags}\n{common}",
    "💎 {category} ka top product!\n\n{title}\n\n🏷️ Rs {price} only\n⭐ Bestseller hai ye!\n\n🔗 Buy now - LINK IN BIO 👆\n#AffiliateLink\n{hashtags}\n{common}",
]

FB_TEMPLATES = [
    "🔥 {title}\n\n💰 Price: Rs {price} only!\n🛒 Bahut kam keemat mein!\n\n✅ Abhi order karo: {link}\n\n#AffiliateLink {hashtags} {common}",
    "🛍️ Aaj ka BEST DEAL!\n\n{title}\n\n💸 Sirf Rs {price}\n⚡ Stock limited hai!\n\n👉 Direct link se order karo: {link}\n\n#AffiliateLink {hashtags} {common}",
    "😍 {category} mein zabardast offer!\n\n{title}\n💰 Rs {price}\n\n🛒 Yahan se kharido: {link}\n\n#AffiliateLink {hashtags} {common}",
]


def get_instagram_caption(product: dict) -> str:
    template = random.choice(IG_TEMPLATES)
    hashtags = HASHTAG_POOLS.get(product.get("category", ""), "#deals #offer #shopping")
    discount_line = f"💥 {product['discount_pct']}% OFF!" if product.get("discount_pct") else ""

    caption = template.format(
        title=product.get("title", "Amazing Product"),
        price=f'{product["price"]:,}' if product.get("price") else "Best Price",
        category=product.get("category", "Trending"),
        hashtags=hashtags,
        common=COMMON_HASHTAGS,
    )
    if discount_line:
        caption = caption.replace("💰 Price:", f"{discount_line}\n💰 Price:")
    return caption


def get_facebook_caption(product: dict) -> str:
    template = random.choice(FB_TEMPLATES)
    hashtags = HASHTAG_POOLS.get(product.get("category", ""), "#deals #offer #shopping")
    discount_line = f"💥 {product['discount_pct']}% OFF!\n" if product.get("discount_pct") else ""

    caption = template.format(
        title=product.get("title", "Amazing Product"),
        price=f'{product["price"]:,}' if product.get("price") else "Best Price",
        category=product.get("category", "Trending"),
        link=product.get("affiliate_link", "#"),
        hashtags=hashtags,
        common=COMMON_HASHTAGS,
    )
    if discount_line:
        caption = discount_line + caption
    return caption

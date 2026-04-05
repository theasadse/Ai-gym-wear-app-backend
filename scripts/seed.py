import asyncio
import random
from decimal import Decimal
from typing import List

from prisma import Prisma


random.seed(42)

CATEGORIES = ["Tops", "Bottoms", "Outerwear", "Footwear", "Accessories", "Sets"]
ITEMS = {
    "Tops": ["Tee", "Long Sleeve", "Tank", "Crop", "Bra"],
    "Bottoms": ["Leggings", "Shorts", "Joggers"],
    "Outerwear": ["Jacket", "Hoodie", "Shell"],
    "Footwear": ["Trainers", "Runners"],
    "Accessories": ["Gloves", "Strap", "Socks", "Cap"],
    "Sets": ["Set"],
}
ADJECTIVES = [
    "AeroFlex",
    "Pulse",
    "Tempo",
    "Momentum",
    "SprintLite",
    "Studio",
    "Recover",
    "Core",
    "Flow",
    "Prime",
    "Form",
    "Balance",
    "Edge",
]
DESCRIPTORS = [
    "breathable mesh",
    "seamless knit",
    "compression fit",
    "high-stretch",
    "brushed fleece",
    "wind-resistant shell",
    "quick-dry",
    "no-slip waistband",
    "pocketed",
    "reflective trim",
]
COLORS = ["Black", "Charcoal", "Navy", "Sage", "Cobalt", "Berry", "Sand", "Olive", "Forest", "Mars", "Stone"]
TAGS = ["running", "hiit", "yoga", "studio", "compression", "recovery", "warmup", "commute", "training", "lightweight", "support"]
IMAGES = [
    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
    "https://images.unsplash.com/photo-1514986888952-8cd320577b68",
    "https://images.unsplash.com/photo-1521572267360-ee0c2909d518",
    "https://images.unsplash.com/photo-1542293787938-4d273c37c1d1",
    "https://images.unsplash.com/photo-1528701800489-20be9bb2f7af",
]


def pick_sizes(category: str) -> str:
    if category == "Footwear":
        return "7,8,9,10,11,12"
    if category == "Accessories":
        return "One Size"
    return "XS,S,M,L,XL"


def generate_products(count: int) -> List[dict]:
    products: List[dict] = []
    for i in range(count):
        category = random.choice(CATEGORIES)
        base_name = random.choice(ADJECTIVES)
        item = random.choice(ITEMS[category])
        name = f"{base_name} {item} {i+1}"
        description = f"{random.choice(ADJECTIVES)} {item.lower()} with {random.choice(DESCRIPTORS)}."
        price = round(random.uniform(18, 120), 2)
        colors = random.sample(COLORS, k=random.randint(1, 3))
        tags = random.sample(TAGS, k=random.randint(2, 4))
        rating = round(random.uniform(4.0, 4.9), 1)
        stock = random.randint(5, 40)
        featured = random.random() < 0.35
        new_arrival = random.random() < 0.25
        image = random.choice(IMAGES) + f"?sig={i}"

        products.append(
            {
                "name": name,
                "description": description,
                "price": Decimal(str(price)),
                "category": category,
                "image": image,
                "colors": colors,
                "tags": tags,
                "rating": rating,
                "stock": stock,
                "featured": featured,
                "newArrival": new_arrival,
                "sizes": pick_sizes(category),
            }
        )
    return products


async def main():
    db = Prisma()
    await db.connect()
    try:
        existing = await db.product.count()
        target = 200
        if existing >= target:
            print(f"Database already has {existing} products; skipping seed.")
            return

        to_create = target - existing
        products = generate_products(to_create)
        for item in products:
            await db.product.create(data=item)
        print(f"Seeded {to_create} products (total now {target}).")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

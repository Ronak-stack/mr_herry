from models import User, Product,Order, OrderItem
from database import SessionLocal
def seed_data():
    session = SessionLocal()
    # 👤 Users
    users = [
        User(name="Ronak", email="ronak@test.com"),
        User(name="Amit", email="amit@test.com"),
        User(name="Neha", email="neha@test.com"),
    ]

    session.add_all(users)
    session.commit()

    # 📦 Products
    products = [
        Product(name="Laptop", price=50000),
        Product(name="Phone", price=20000),
        Product(name="Headphones", price=2000),
    ]

    session.add_all(products)
    session.commit()

    # 🧾 Orders
    orders = [
        Order(user_id=users[0].id),
        Order(user_id=users[1].id),
        Order(user_id=users[0].id),
    ]

    session.add_all(orders)
    session.commit()

    # 🧩 Order Items
    items = [OrderItem(order_id=orders[0].id, product_id=products[0].id, quantity=1)]

    session.add_all(items)
    session.commit()

    print("✅ Seed data inserted")

if __name__ == "__main__":
    seed_data()
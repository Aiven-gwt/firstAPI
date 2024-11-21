import asyncio

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from core.models import (
    db_helper,
    User,
    Profile,
    Post,
    Order,
    Product,
    OrderProductAssociation,
)


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print("user", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    # result: Result = await session.execute(stmt)
    user: User | None = await session.scalar(stmt)
    print("Found user", username, user)
    return user


async def create_user_profile(
        session: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(profile)
    await session.commit()
    return profile


async def show_users_with_profiles(session: AsyncSession):
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    # result: Result = await session.execute(stmt)
    # user = result.scalars(stmt)
    users = await session.scalars(stmt)
    for user in users:
        print(user)
        print(user.profile.first_name)


async def create_posts(
        session: AsyncSession,
        user_id: int,
        *posts_titles: str,
) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in posts_titles]
    session.add_all(posts)
    await session.commit()
    print(posts)
    return posts


async def get_users_wih_posts(
        session: AsyncSession,
):
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars()

    for user in users:
        print("**" * 10)
        print(user)
        for post in user.posts:
            print("-", post)


async def get_posts_with_authors(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)

    for post in posts:
        print("post", post)
        print("author", post.user)


async def get_profiles_with_users_and_users_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
            .join(Profile.user)
            .options(joinedload(Profile.user).selectinload(User.posts))
            .where(User.username == "jhon")
            .order_by(Profile.id)
    )

    profiles = await session.scalars(stmt)

    for profile in profiles:
        print(profile.first_name, profile.user)
        print(profile.user.posts)


async def main_relations(session: AsyncSession):
    # await create_user(session=session, username="jhon")
    # await create_user(session=session, username="alise")
    # await create_user(session=session, username="sam")
    # user_sam = await get_user_by_username(session=session, username="sam")
    # user_jhon = await get_user_by_username(session=session, username="jhon")
    # await create_user_profile(
    #     session=session,
    #     user_id=user_jhon.id,
    #     first_name="John"
    # )
    # await create_user_profile(
    #     session=session,
    #     user_id=user_sam.id,
    #     first_name="Sam",
    #     last_name="White"
    # )
    # await show_users_with_profiles(session=session)
    # await create_posts(
    #     session,
    #     user_jhon.id,
    #     "sdfsdf",
    #     "klsdjflskdjf",
    # )
    # await create_posts(
    #     session,
    #     user_sam.id,
    #     "NONONO",
    #     "bimbimbambam",
    # )
    # await get_users_wih_posts(session=session)
    # await get_posts_with_authors(session=session)
    await get_profiles_with_users_and_users_with_posts(session=session)


async def create_order(
        session: AsyncSession,
        promocode: str | None = None,
) -> Order:
    order = Order(promocode=promocode)

    session.add(order)
    await session.commit()

    return order


async def get_orders_with_products(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)

    return list(orders)


async def create_orders_and_products(session: AsyncSession):
    order_one = await create_order(session)
    order_promo = await create_order(session, promocode="promo")

    mouse = await create_product(
        session,
        "Mouse",
        "Great mouse pokupai",
        price=1200,
    )
    keyboard = await create_product(
        session,
        "Keyboard",
        "Great keyboard pokupai faster",
        price=2000,
    )
    display = await create_product(
        session,
        "Display",
        "Great display",
        price=4900,
    )
    order_one = await session.scalar(
        select(Order)
            .where(Order.id == order_one.id)
            .options(
            selectinload(Order.products),
        ),
    )

    order_promo = await session.scalar(
        select(Order)
            .where(Order.id == order_promo.id)
            .options(
            selectinload(Order.products),
        ),
    )

    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    # order_promo.products.append(keyboard)
    # order_promo.products.append(display)

    order_promo.products = [keyboard, display]

    await session.commit()


async def create_product(
        session: AsyncSession,
        name: str,
        description: str,
        price: int,
) -> Product:
    product = Product(
        name=name,
        description=description,
        price=price,
    )

    session.add(product)
    await session.commit()

    return product


async def demo_get_orders_with_products_through_secondary(session: AsyncSession):
    orders = await get_orders_with_products(session)
    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for product in order.products:  # type: Product
            print("-", product.id, product.name, product.price)


async def get_order_with_products_assoc(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(
                OrderProductAssociation.product
            ),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_products_with_assoc(session: AsyncSession):
    orders = await get_order_with_products_assoc(session)

    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for (
                order_product_details
        ) in order.products_details:  # type OrderProductAssociation
            print(
                "-",
                order_product_details.product.id,
                order_product_details.product.name,
                order_product_details.product.price,
                "qty:",
                order_product_details.count,
            )


async def create_gift_product_for_existing_orders(session: AsyncSession):
    orders = await get_order_with_products_assoc(session)
    gift_product = await create_product(
        session,
        name="Gift",
        description="Gift for you",
        price=0,
    )
    for order in orders:
        order.products_details.append(
            OrderProductAssociation(
                count=1,
                unit_price=0,
                product=gift_product,
            )
        )

    await session.commit()


async def demo_m2m(session: AsyncSession):
    # await create_orders_and_products(session)
    # await demo_get_orders_with_products_through_secondary()
    await demo_get_orders_with_products_with_assoc(session)
    # await create_gift_product_for_existing_orders(session)


async def main():
    async with db_helper.session_factory() as session:
        # await main_relations(session)
        await demo_m2m(session)


if __name__ == "__main__":
    asyncio.run(main())

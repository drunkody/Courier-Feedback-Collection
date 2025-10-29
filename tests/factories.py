"""Factory classes for test data generation."""
import factory
from factory import fuzzy
from faker import Faker
import json

from app.database import Courier, Feedback, AdminUser, hash_password

fake = Faker()


class CourierFactory(factory.Factory):
    """Factory for Courier model."""

    class Meta:
        model = Courier

    id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')
    phone = factory.Faker('phone_number')
    contact_link = factory.Faker('url')


class FeedbackFactory(factory.Factory):
    """Factory for Feedback model."""

    class Meta:
        model = Feedback

    id = factory.Sequence(lambda n: n)
    order_id = factory.Sequence(lambda n: f"ORD{n:05d}")
    courier_id = 1
    rating = fuzzy.FuzzyInteger(1, 5)
    comment = factory.Faker('text', max_nb_chars=200)
    reasons = factory.LazyFunction(
        lambda: json.dumps(
            fake.random_choices(
                elements=["Punctuality", "Politeness", "Item Condition", "Packaging", "Other"],
                length=fake.random_int(1, 3)
            )
        )
    )
    publish_consent = factory.Faker('boolean')
    needs_follow_up = factory.LazyAttribute(lambda obj: obj.rating <= 4)


class AdminUserFactory(factory.Factory):
    """Factory for AdminUser model."""

    class Meta:
        model = AdminUser

    id = factory.Sequence(lambda n: n)
    username = factory.Faker('user_name')
    password_hash = factory.LazyFunction(lambda: hash_password("testpass123"))


def create_feedback_batch(count: int = 10, **kwargs):
    """Create multiple feedback entries."""
    return [FeedbackFactory.build(**kwargs) for _ in range(count)]


def create_courier_batch(count: int = 5, **kwargs):
    """Create multiple couriers."""
    return [CourierFactory.build(**kwargs) for _ in range(count)]

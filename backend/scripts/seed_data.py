"""
Seed script — populates the database with realistic demo data
for a grocery shop business.

Run: python -m scripts.seed_data
"""
import asyncio
import random
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import Base
from app.models.business import Business, IndustryType
from app.models.customer import Customer
from app.models.expense import Expense, ExpenseCategory
from app.models.income import Income, IncomeCategory, PaymentMethod
from app.models.invoice import Invoice, InvoiceStatus
from app.models.user import User, UserRole


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        # ── Admin User ───────────────────────────────────────────────────────
        admin = User(
            email="admin@smartcash.ai",
            hashed_password=get_password_hash("Admin@123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_email_verified=True,
            is_active=True,
        )
        db.add(admin)

        # ── Business Owner ───────────────────────────────────────────────────
        owner = User(
            email="demo@smartcash.ai",
            hashed_password=get_password_hash("Demo@123"),
            full_name="Ravi Kumar",
            role=UserRole.BUSINESS_OWNER,
            is_email_verified=True,
            is_active=True,
        )
        db.add(owner)
        await db.flush()

        # ── Business ─────────────────────────────────────────────────────────
        business = Business(
            owner_id=owner.id,
            name="Ravi Grocery & General Store",
            gst_number="33AACFR1234F1Z5",
            industry=IndustryType.GROCERY,
            currency="INR",
            opening_balance=50_000.0,
            city="Chennai",
            state="Tamil Nadu",
        )
        db.add(business)
        await db.flush()

        # ── Customers ────────────────────────────────────────────────────────
        customers_data = [
            ("Anbu Selvam", "9876543210", "anbu@gmail.com", 15_000, 30),
            ("Priya Devi", "9865432109", "priya@gmail.com", 8_500, 15),
            ("Mohan Das", "9754321098", None, 22_000, -5),   # overdue
            ("Kavitha", "9643210987", "kavitha@gmail.com", 3_200, 45),
            ("Suresh Kumar", "9532109876", None, 45_000, -10),  # overdue
        ]
        customer_objs = []
        for name, phone, email, outstanding, due_offset in customers_data:
            c = Customer(
                business_id=business.id,
                name=name,
                phone=phone,
                email=email,
                outstanding_amount=outstanding,
                due_date=date.today() + timedelta(days=due_offset),
                total_invoiced=outstanding * 2.5,
                total_paid=outstanding * 1.5,
            )
            db.add(c)
            customer_objs.append(c)
        await db.flush()

        # ── Income (last 90 days) ─────────────────────────────────────────────
        income_categories = list(IncomeCategory)
        payment_methods = list(PaymentMethod)
        today = date.today()
        for i in range(90):
            txn_date = today - timedelta(days=i)
            n_transactions = random.randint(2, 6)
            for _ in range(n_transactions):
                income = Income(
                    business_id=business.id,
                    amount=round(random.uniform(500, 8_000), 2),
                    category=random.choice([IncomeCategory.SALES, IncomeCategory.CASH, IncomeCategory.ONLINE]),
                    payment_method=random.choice(payment_methods),
                    transaction_date=txn_date,
                    description=f"Daily sales",
                )
                db.add(income)

        # ── Expenses (last 90 days) ───────────────────────────────────────────
        recurring_expenses = [
            (ExpenseCategory.RENT, 15_000, 1),
            (ExpenseCategory.ELECTRICITY, 3_500, 1),
            (ExpenseCategory.SALARY, 25_000, 1),
        ]
        for i in range(90):
            txn_date = today - timedelta(days=i)
            # Recurring monthly
            if txn_date.day == 1:
                for cat, amt, _ in recurring_expenses:
                    db.add(Expense(
                        business_id=business.id,
                        amount=amt,
                        category=cat,
                        transaction_date=txn_date,
                        description=f"Monthly {cat.value}",
                        is_recurring=True,
                    ))
            # Daily variable
            n = random.randint(1, 4)
            for _ in range(n):
                db.add(Expense(
                    business_id=business.id,
                    amount=round(random.uniform(200, 4_000), 2),
                    category=random.choice([
                        ExpenseCategory.INVENTORY, ExpenseCategory.FUEL,
                        ExpenseCategory.MARKETING, ExpenseCategory.MISCELLANEOUS,
                    ]),
                    transaction_date=txn_date,
                ))

        # One anomalous expense
        db.add(Expense(
            business_id=business.id,
            amount=85_000.0,
            category=ExpenseCategory.MISCELLANEOUS,
            transaction_date=today - timedelta(days=5),
            description="Anomalous large payment",
            is_anomaly=True,
            anomaly_score=0.95,
        ))

        await db.commit()

    await engine.dispose()
    print("✅ Seed data loaded successfully!")
    print("   Admin:  admin@smartcash.ai / Admin@123")
    print("   Owner:  demo@smartcash.ai  / Demo@123")


if __name__ == "__main__":
    asyncio.run(seed())

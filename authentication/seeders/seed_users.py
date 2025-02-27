from django.core.management.base import BaseCommand
from authentication.models import User
from django.utils.timezone import now

def seed():
    print("🔹 Menjalankan User Seeder...")

    # Hapus data lama jika ingin reset
    User.objects.all().delete()

    # Data dummy untuk User
    users_data = [
        {
            "user_id": "user001",
            "user_name": "admin",
            "real_name": "Administrator",
            "email": "admin@example.com",
            "phone": "081234567890",
            "password": "admin123",
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "user_id": "user002",
            "user_name": "doctor_john",
            "real_name": "John Doe",
            "email": "john@example.com",
            "phone": "081234567891",
            "password": "doctor123",
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "user_id": "user003",
            "user_name": "patient_jane",
            "real_name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "081234567892",
            "password": "patient123",
            "is_staff": False,
            "is_superuser": False,
        }
    ]

    # Buat User
    for user_data in users_data:
        user = User.objects.create(
            user_id=user_data["user_id"],
            user_name=user_data["user_name"],
            real_name=user_data["real_name"],
            email=user_data["email"],
            phone=user_data["phone"],
            is_staff=user_data["is_staff"],
            is_superuser=user_data["is_superuser"],
            date_joined=now(),
        )
        user.set_password(user_data["password"])  # Hash password
        user.save()

    print('✅ User Seeder selesai!')
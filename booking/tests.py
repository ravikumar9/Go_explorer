from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from datetime import date

from .models import Hotel, RoomType, RoomPlan, Coupon, Booking
from django.core.exceptions import ValidationError


class CouponViewTests(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name="Test Hotel", city="City", address="", rating=3, is_active=True)
        self.rt = RoomType.objects.create(hotel=self.hotel, name="Standard")
        self.plan = RoomPlan.objects.create(room_type=self.rt, plan_type="ROOM_ONLY", price=Decimal('100.00'))
        self.percent_coupon = Coupon.objects.create(code="PERC10", hotel=self.hotel, discount_type="PERCENT", discount_value=10, is_active=True)
        self.flat_coupon = Coupon.objects.create(code="FLAT50", hotel=self.hotel, discount_type="FLAT", discount_value=50, is_active=True)

    def test_validate_percent_coupon(self):
        url = reverse('validate_coupon')
        resp = self.client.get(url, {'code': 'PERC10', 'plan_id': self.plan.id, 'total': '118.00'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertEqual(data.get('code'), 'PERC10')
        self.assertEqual(Decimal(data.get('discount')), Decimal('11.80'))
        self.assertEqual(Decimal(data.get('payable')), Decimal('106.20'))

    def test_validate_flat_coupon(self):
        url = reverse('validate_coupon')
        resp = self.client.get(url, {'code': 'FLAT50', 'plan_id': self.plan.id, 'total': '118.00'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertEqual(data.get('code'), 'FLAT50')
        self.assertEqual(Decimal(data.get('discount')), Decimal('50'))
        self.assertEqual(Decimal(data.get('payable')), Decimal('68.00'))

    def test_validate_not_found(self):
        url = reverse('validate_coupon')
        resp = self.client.get(url, {'code': 'NOPE', 'plan_id': self.plan.id, 'total': '100.00'})
        self.assertEqual(resp.status_code, 404)


class BookingModelTests(TestCase):
    def test_booking_dates_validation(self):
        hotel = Hotel.objects.create(name="H2", city="C2", address="", rating=3, is_active=True)
        rt = RoomType.objects.create(hotel=hotel, name="R2")
        rp = RoomPlan.objects.create(room_type=rt, plan_type="ROOM_ONLY", price=Decimal('100.00'))

        b = Booking(
            room_plan=rp,
            guest_name='G',
            guest_email='e@example.com',
            guest_phone='1234',
            check_in=date(2026, 5, 10),
            check_out=date(2026, 5, 5),
            coupon_code=None,
            discount_amount=Decimal('0'),
            amount=Decimal('100.00'),
        )
        with self.assertRaises(ValidationError):
            b.full_clean()

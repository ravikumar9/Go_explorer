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


class EndToEndBookingFlowTests(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name="E2E Hotel", city="CityE", address="", rating=4, is_active=True)
        self.rt = RoomType.objects.create(hotel=self.hotel, name="Deluxe")
        self.plan = RoomPlan.objects.create(room_type=self.rt, plan_type="ROOM_ONLY", price=Decimal('100.00'))
        self.coupon = Coupon.objects.create(code="PERC10", hotel=self.hotel, discount_type="PERCENT", discount_value=10, is_active=True)

    def test_full_booking_flow_with_coupon(self):
        # Review booking (GET)
        check_in = date(2026, 6, 1)
        check_out = date(2026, 6, 3)  # 2 nights
        url = reverse('review_booking')
        resp = self.client.get(url, {
            'plan_id': self.plan.id,
            'check_in': check_in.isoformat(),
            'check_out': check_out.isoformat(),
        })
        self.assertEqual(resp.status_code, 200)

        # Compute expected totals as view would
        nights = (check_out - check_in).days
        base_fare = Decimal(self.plan.price) * nights
        gst = (base_fare * Decimal('0.18')).quantize(Decimal('0.01'))
        total = base_fare + gst

        # Create booking (POST) with coupon
        post_url = reverse('create_booking')
        data = {
            'plan_id': str(self.plan.id),
            'check_in': check_in.isoformat(),
            'check_out': check_out.isoformat(),
            'total': str(total),
            'coupon_code': self.coupon.code,
            'guest_name': 'Alice',
            'email': 'alice@example.com',
            'phone': '9998887777',
        }
        resp2 = self.client.post(post_url, data)
        self.assertEqual(resp2.status_code, 302)

        # Booking created and redirected to payment page
        booking = Booking.objects.first()
        self.assertIsNotNone(booking)

        # Validate discount and final amount
        expected_discount = (total * Decimal(self.coupon.discount_value) / 100).quantize(Decimal('0.01'))
        expected_payable = (total - expected_discount).quantize(Decimal('0.01'))

        self.assertEqual(booking.discount_amount, expected_discount)
        self.assertEqual(booking.amount, expected_payable)

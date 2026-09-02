# payment_gateway.py
"""
لایه‌ی انتزاعی درگاه پرداخت.

هدف این ماژول اینه که کل بقیه‌ی برنامه (روت‌ها، تمپلیت‌ها) اصلاً ندونن
داریم از درگاه واقعی (زیبال) استفاده می‌کنیم یا از حالت آزمایشی/سندباکس.
برای سوییچ بین این دو حالت فقط کافیه مقدار PAYMENT_MODE در تنظیمات برنامه
(app.config یا متغیر محیطی) رو از 'sandbox' به 'zibal' تغییر بدید — هیچ
تغییری در app.py یا تمپلیت‌ها لازم نیست.

نحوه‌ی اضافه‌کردن یک درگاه جدید در آینده:
    یک کلاس جدید از BasePaymentGateway بسازید، متدهای request_payment و
    verify_payment رو پیاده‌سازی کنید و در تابع get_gateway ثبتش کنید.
"""

import requests

ZIBAL_REQUEST_URL = "https://gateway.zibal.ir/v1/request"
ZIBAL_VERIFY_URL = "https://gateway.zibal.ir/v1/verify"
ZIBAL_STARTPAY_URL = "https://gateway.zibal.ir/start/{track_id}"

# کدهای نتیجه‌ی معروف زیبال (برای پیام‌های خطای خواناتر)
ZIBAL_RESULT_MESSAGES = {
    100: "موفق",
    102: "مرچنت یافت نشد",
    103: "مرچنت غیرفعال",
    104: "مرچنت نامعتبر",
    201: "قبلاً تایید شده",
    202: "سفارش پرداخت نشده یا ناموفق بوده",
    203: "شناسه پرداخت (trackId) نامعتبر است",
}


class PaymentResult:
    """نتیجه‌ی یکسان‌شده‌ی هر عملیات درگاه، صرف‌نظر از اینکه درگاه واقعیه یا آزمایشی."""

    def __init__(self, success, track_id=None, payment_url=None,
                 ref_number=None, message=""):
        self.success = success
        self.track_id = track_id
        self.payment_url = payment_url
        self.ref_number = ref_number
        self.message = message


class BasePaymentGateway:
    name = "base"

    def request_payment(self, amount, description, callback_url, order_id):
        """شروع یک تراکنش. amount به تومان است."""
        raise NotImplementedError

    def verify_payment(self, track_id, amount):
        """تایید نهایی پرداخت بعد از بازگشت کاربر از درگاه."""
        raise NotImplementedError


class SandboxGateway(BasePaymentGateway):
    """
    درگاه آزمایشی داخلی.

    هیچ تماس اینترنتی برقرار نمی‌کند و به هیچ مرچنت واقعی نیاز ندارد؛ فقط
    برای تستِ کاملِ مسیر خرید (ایجاد سفارش → پرداخت → تایید → دانلود) قبل
    از وصل‌شدن به یک درگاه واقعی استفاده می‌شود. کاربر در یک صفحه‌ی داخلی
    بین «پرداخت موفق» و «انصراف» یکی را انتخاب می‌کند.
    """
    name = "sandbox"

    def request_payment(self, amount, description, callback_url, order_id):
        return PaymentResult(
            success=True,
            track_id=f"SANDBOX-{order_id}",
            payment_url=None,
            message="حالت آزمایشی (بدون درگاه واقعی)"
        )

    def verify_payment(self, track_id, amount):
        # در حالت آزمایشی، انتخاب کاربر در صفحه‌ی شبیه‌سازی، خودِ نتیجه است
        return PaymentResult(success=True, ref_number=f"REF-{track_id}")


class ZibalGateway(BasePaymentGateway):
    """اتصال واقعی به درگاه زیبال (zibal.ir)."""
    name = "zibal"

    def __init__(self, merchant):
        # مرچنت آزمایشی رسمی زیبال مقدار "zibal" است (برای تست بدون نیاز به ثبت‌نام)
        self.merchant = merchant

    def request_payment(self, amount, description, callback_url, order_id):
        try:
            resp = requests.post(ZIBAL_REQUEST_URL, json={
                "merchant": self.merchant,
                "amount": int(amount) * 10,  # زیبال مبلغ را بر حسب ریال می‌گیرد
                "callbackUrl": callback_url,
                "description": description,
                "orderId": str(order_id),
            }, timeout=10)
            data = resp.json()
        except Exception as e:
            return PaymentResult(success=False, message=f"خطا در اتصال به درگاه زیبال: {e}")

        if data.get("result") == 100:
            track_id = data.get("trackId")
            return PaymentResult(
                success=True,
                track_id=track_id,
                payment_url=ZIBAL_STARTPAY_URL.format(track_id=track_id)
            )

        code = data.get("result")
        return PaymentResult(
            success=False,
            message=ZIBAL_RESULT_MESSAGES.get(code, data.get("message", "خطای نامشخص از درگاه زیبال"))
        )

    def verify_payment(self, track_id, amount):
        try:
            resp = requests.post(ZIBAL_VERIFY_URL, json={
                "merchant": self.merchant,
                "trackId": track_id,
            }, timeout=10)
            data = resp.json()
        except Exception as e:
            return PaymentResult(success=False, message=f"خطا در اتصال به درگاه زیبال: {e}")

        if data.get("result") == 100:
            paid_amount_toman = int(data.get("amount", 0)) // 10
            if paid_amount_toman != int(amount):
                return PaymentResult(success=False, message="مبلغ پرداختی با مبلغ سفارش مطابقت ندارد")
            return PaymentResult(success=True, ref_number=str(data.get("refNumber", "")))

        code = data.get("result")
        return PaymentResult(
            success=False,
            message=ZIBAL_RESULT_MESSAGES.get(code, data.get("message", "پرداخت تایید نشد"))
        )


def get_gateway(app_config):
    """بر اساس تنظیمات برنامه، نمونه‌ی درگاه مناسب رو برمی‌گردونه."""
    mode = (app_config.get("PAYMENT_MODE") or "sandbox").lower()
    if mode == "zibal":
        return ZibalGateway(merchant=app_config.get("ZIBAL_MERCHANT", "zibal"))
    return SandboxGateway()

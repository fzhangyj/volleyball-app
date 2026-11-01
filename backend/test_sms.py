"""Exercise the real SMS utility with SDK response models and a mocked client.

Run with `py -m unittest test_sms -v`; no SMS requests leave this process.
"""
import os
import unittest
from unittest.mock import Mock, patch

from alibabacloud_dypnsapi20170525 import models

os.environ.setdefault("SECRET_KEY", "sms-unit-test-only-secret-at-least-32-characters")

from app.utils import sms


class SmsProviderTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.enabled = patch.object(sms, "SMS_ENABLED", True)
        self.provider = patch.object(sms.AliyunSmsClient, "get_client", return_value=self.client)
        self.enabled.start()
        self.provider.start()
        self.addCleanup(self.enabled.stop)
        self.addCleanup(self.provider.stop)

    def test_send_accepts_ok_and_reads_sdk_model_biz_id(self):
        self.client.send_sms_verify_code_with_options.return_value = models.SendSmsVerifyCodeResponse(
            status_code=200,
            body=models.SendSmsVerifyCodeResponseBody(
                code="OK", success=True,
                model=models.SendSmsVerifyCodeResponseBodyModel(biz_id="provider-biz-id"),
            ),
        )

        result = sms.send_sms("13800000000", "login")

        self.assertTrue(result["success"])
        self.assertEqual(result["biz_id"], "provider-biz-id")
        self.client.send_sms_verify_code_with_options.assert_called_once()
        request, _ = self.client.send_sms_verify_code_with_options.call_args.args
        self.assertIsInstance(request, models.SendSmsVerifyCodeRequest)
        self.assertEqual(request.phone_number, "13800000000")
        self.assertEqual(request.template_code, sms.SMS_TEMPLATE_REGISTER)
        self.assertEqual(request.sign_name, sms.ALIYUN_SMS_SIGN_NAME)
        self.assertEqual(request.code_length, 6)
        self.assertEqual(request.valid_time, 300)

    def test_send_rejects_http_200_with_unknown_business_code(self):
        self.client.send_sms_verify_code_with_options.return_value = models.SendSmsVerifyCodeResponse(
            status_code=200,
            body=models.SendSmsVerifyCodeResponseBody(code="UNKNOWN", message="provider rejected request", success=False),
        )

        result = sms.send_sms("13800000000", "login")

        self.assertFalse(result["success"])
        self.assertNotIn("biz_id", result)
        self.assertIn("短信服务暂不可用", result["message"])

    def test_send_rejects_non_200_even_with_ok_business_code(self):
        self.client.send_sms_verify_code_with_options.return_value = models.SendSmsVerifyCodeResponse(
            status_code=503, body=models.SendSmsVerifyCodeResponseBody(code="OK"),
        )
        self.assertFalse(sms.send_sms("13800000000")["success"])

    def test_check_accepts_only_ok_with_pass(self):
        self.client.check_sms_verify_code_with_options.return_value = models.CheckSmsVerifyCodeResponse(
            status_code=200,
            body=models.CheckSmsVerifyCodeResponseBody(
                code="OK", success=True,
                model=models.CheckSmsVerifyCodeResponseBodyModel(verify_result="PASS"),
            ),
        )

        self.assertEqual(sms.check_sms_code("13800000000", "123456"), (True, "验证成功"))
        request, _ = self.client.check_sms_verify_code_with_options.call_args.args
        self.assertIsInstance(request, models.CheckSmsVerifyCodeRequest)
        self.assertEqual(request.phone_number, "13800000000")
        self.assertEqual(request.verify_code, "123456")

    def test_check_rejects_unknown_even_with_pass_model(self):
        self.client.check_sms_verify_code_with_options.return_value = models.CheckSmsVerifyCodeResponse(
            status_code=200,
            body=models.CheckSmsVerifyCodeResponseBody(
                code="UNKNOWN", success=False,
                model=models.CheckSmsVerifyCodeResponseBodyModel(verify_result="PASS"),
            ),
        )
        self.assertFalse(sms.check_sms_code("13800000000", "123456")[0])

    def test_check_rejects_wrong_code(self):
        self.client.check_sms_verify_code_with_options.return_value = models.CheckSmsVerifyCodeResponse(
            status_code=200,
            body=models.CheckSmsVerifyCodeResponseBody(
                code="OK", success=True,
                model=models.CheckSmsVerifyCodeResponseBodyModel(verify_result="FAIL"),
            ),
        )
        self.assertEqual(sms.check_sms_code("13800000000", "000000"), (False, "验证码错误或已过期"))

    def test_missing_configuration_cannot_send_or_accept_any_code(self):
        with patch.object(sms, "SMS_ENABLED", False):
            self.assertFalse(sms.send_sms("13800000000")["success"])
            self.assertFalse(sms.check_sms_code("13800000000", "123456")[0])
        sms.AliyunSmsClient.get_client.assert_not_called()


if __name__ == "__main__":
    unittest.main()

import os
import time
import base64
import hmac
import hashlib
import json
import httpx

from core.config import settings

class SmsService:
    def __init__(self):
        self.access_key = settings.NAVER_CLOUD_SMS_ACCESS_KEY
        self.secret_key = settings.NAVER_CLOUD_SMS_SECRET_KEY
        self.service_id = settings.NAVER_CLOUD_SMS_SERVICE_ID
        self.api_url = f"https://sens.apigw.ntruss.com/sms/v2/services/{self.service_id}/messages"

    def get_signature(self, timestamp: str) -> str:
        """
        요청에 필요한 서명(Signature)을 생성합니다.
        Java 코드의 getSignature() 메서드와 동일한 로직입니다.
        """
        secret_key_bytes = self.secret_key.encode('utf-8')
        message = (
            "POST "
            f"/sms/v2/services/{self.service_id}/messages\n"
            f"{timestamp}\n"
            f"{self.access_key}"
        ).encode('utf-8')
        
        signature = hmac.new(
            secret_key_bytes, 
            message, 
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')

    def send_sms(self, phone_number: str, verification_code: str):
        """
        Naver Cloud SENS API를 통해 SMS를 전송합니다.
        Java 코드의 sendSms() 메서드와 동일한 로직입니다.
        """
        timestamp = str(int(time.time() * 1000))
        signature = self.get_signature(timestamp)

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-ncp-apigw-timestamp": timestamp,
            "x-ncp-iam-access-key": self.access_key,
            "x-ncp-apigw-signature-v2": signature,
        }

        body = {
            "type": "SMS",
            "contentType": "COMM",
            "countryCode": "82",
            "from": "07045718337",
            "content": f"[Theyday] 인증번호 [{verification_code}]를 입력해주세요",
            "messages": [{"to": phone_number}],
        }
        try:
            with httpx.Client() as client:
                response = client.post(self.api_url, headers=headers, content=json.dumps(body))
                response.raise_for_status()  # HTTP 오류가 발생하면 예외를 일으킴
                print(f"SMS 전송 성공: {response.status_code}, {response.text}")
        except httpx.RequestError as e:
            print(f"SMS 전송 실패: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"응답 본문: {e.response.text}")
        except httpx.HTTPStatusError as e:
            print(f"SMS 전송 실패: {e}")
            print(f"응답 본문: {e.response.text}")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from core.config import settings

# Jinja2 템플릿 환경 설정 (templates 폴더가 있어야 함)
template_env = Environment(loader=FileSystemLoader("templates"))

class MailService:
    def __init__(self):
        # YAML 설정에 해당하는 값들을 환경 변수에서 가져옴
        self.mail_username = settings.MAIL_USERNAME
        self.mail_password = settings.MAIL_PASSWORD
        self.mail_server = settings.MAIL_SERVER
        self.mail_port = int(settings.MAIL_PORT)
        
    def get_html_content(self, template_name: str, to: str, code: str) -> str:
        """Jinja2 템플릿을 렌더링하여 HTML 본문을 생성합니다."""
        template = template_env.get_template(template_name)
        return template.render(to=to, code=code)

    def send_simple_mail_message(self, to: str, code: str, is_exist: bool):
        """
        SMTP 서버를 통해 이메일을 전송합니다.
        is_exist 값에 따라 다른 제목과 템플릿을 사용합니다.
        """
        if is_exist:
            subject = "[Theyday] 로그인 인증번호를 안내드립니다."
            template_name = "login_email.html"
        else:
            subject = "[Theyday] 회원가입 인증번호를 안내드립니다."
            template_name = "signup_email.html"

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.mail_username
        message["To"] = to
        
        html_content = self.get_html_content(template_name, to, code)
        part = MIMEText(html_content, "html", "utf-8")
        message.attach(part)
      
        try:
            with smtplib.SMTP(self.mail_server, self.mail_port) as server:
                server.starttls()
                server.login(self.mail_username, self.mail_password)
                server.sendmail(self.mail_username, to, message.as_string())
        except Exception as e:
            print(f"이메일 전송 실패: {e}")
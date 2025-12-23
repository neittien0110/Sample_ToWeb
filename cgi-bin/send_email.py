import smtplib
import json
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_config(config_file):
    """Đọc cấu hình từ file JSON."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Khong tim thay file {config_file}")
        exit(1)

def send_email(to_email, subject, body):
    # Load cấu hình
    config = load_config('config.json')
    
    sender_email = config['sender_email']
    password = config['password']
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']

    # Tạo cấu trúc Email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Kết nối tới server Gmail qua SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, message.as_string())
        print(f"Thanh cong {to_email}!")
    except Exception as e:
        print(f"Co loi {e}")

if __name__ == "__main__":
    # Thiết lập tham số dòng lệnh
    parser = argparse.ArgumentParser(description="Gửi email qua Gmail cá nhân.")
    parser.add_argument("--to", required=True, help="Địa chỉ email người nhận")
    parser.add_argument("--subject", required=True, help="Tiêu đề email")
    parser.add_argument("--body", required=True, help="Nội dung email")

    args = parser.parse_args()

    # Gọi hàm gửi mail
    send_email(args.to, args.subject, args.body)
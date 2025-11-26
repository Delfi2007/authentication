"""
OTP Service for Two-Factor Authentication
Sends OTP codes via SMS using Fast2SMS or console (free options)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os

class OTPService:
    """Handle OTP delivery"""
    
    def __init__(self):
        self.delivery_method = 'email'  # 'console', 'email', 'sms', or 'fast2sms'
        
        # Gmail SMTP Configuration (100% FREE)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('GMAIL_SENDER', 'your-email@gmail.com')  # Your Gmail
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD', 'your-app-password')  # Gmail App Password
        
        # Fast2SMS Configuration (Paid service)
        self.fast2sms_api_key = os.getenv('FAST2SMS_API_KEY', 'YOUR_FAST2SMS_API_KEY')
        
    def send_otp_console(self, phone_number, otp):
        """Print OTP to console (for testing)"""
        print("\n" + "="*50)
        print("📱 TWO-FACTOR AUTHENTICATION")
        print("="*50)
        print(f"Phone Number: {phone_number}")
        print(f"Your OTP Code: {otp}")
        print(f"Valid for: 10 minutes")
        print("="*50 + "\n")
        return True, "OTP sent to console (check terminal)"
    
    def send_otp_email(self, email, otp, username):
        """Send OTP via email (FREE using Gmail)"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🔐 Your Two-Factor Authentication Code"
            message["From"] = self.sender_email
            message["To"] = email
            
            # HTML content
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #4CAF50; color: white; padding: 20px; text-align: center;">
                  <h1>🔐 Two-Factor Authentication</h1>
                </div>
                <div style="padding: 30px; background: #f5f5f5;">
                  <h2>Hello {username},</h2>
                  <p>Your authentication code is:</p>
                  <div style="background: white; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; border: 2px solid #4CAF50; border-radius: 10px; margin: 20px 0;">
                    {otp}
                  </div>
                  <p><strong>This code will expire in 10 minutes.</strong></p>
                  <p style="color: #666; font-size: 12px;">If you didn't request this code, please ignore this email.</p>
                </div>
                <div style="background: #333; color: white; padding: 15px; text-align: center; font-size: 12px;">
                  <p>Face Recognition Authentication System</p>
                </div>
              </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            # Send email via Gmail SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, email, message.as_string())
            
            print(f"\n✅ OTP Email sent successfully to {email}")
            print(f"OTP Code: {otp} (Valid for 10 minutes)\n")
            return True, f"OTP sent to your email: {email}"
        
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False, f"Failed to send OTP: {str(e)}"
    
    def send_otp(self, phone_number, otp, email=None, username=None):
        """Send OTP using configured method"""
        if self.delivery_method == 'fast2sms':
            return self.send_otp_fast2sms(phone_number, otp)
        elif self.delivery_method == 'email' and email:
            return self.send_otp_email(email, otp, username or 'User')
        elif self.delivery_method == 'console':
            return self.send_otp_console(phone_number, otp)
        else:
            # Default to console (no paid service required)
            return self.send_otp_console(phone_number, otp)
    
    def send_otp_fast2sms(self, phone_number, otp):
        """
        Send OTP via Fast2SMS (Free for Indian numbers)
        Get API key from: https://www.fast2sms.com/
        """
        try:
            # Remove country code if present (Fast2SMS needs 10-digit number)
            clean_number = phone_number.replace('+91', '').replace('+', '').replace('-', '').replace(' ', '')
            
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            payload = {
                "route": "v3",
                "sender_id": "TXTIND",
                "message": f"Your verification code is: {otp}. Valid for 10 minutes. - Face Auth System",
                "language": "english",
                "flash": 0,
                "numbers": clean_number,
            }
            
            headers = {
                "authorization": self.fast2sms_api_key,
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache"
            }
            
            response = requests.post(url, data=payload, headers=headers)
            result = response.json()
            
            if result.get('return'):
                print(f"✅ SMS sent successfully to {phone_number}")
                print(f"Response: {result}")
                return True, "OTP sent via SMS"
            else:
                raise Exception(result.get('message', 'Unknown error'))
        
        except Exception as e:
            print(f"❌ Failed to send SMS: {str(e)}")
            # Fallback to console for testing if SMS fails
            print("Falling back to console delivery...")
            return self.send_otp_console(phone_number, otp)

# Initialize global OTP service
otp_service = OTPService()

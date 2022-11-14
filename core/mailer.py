import smtplib, ssl
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
from .config import settings

class Mailer:

    def __init__(self):
        self.port = settings.MAILER_PORT 
        self.smtp_server_domain_name = settings.MAILER_DOMAIN
        self.sender_mail = settings.MAILER_USERNAME
        self.pasword = settings.MAILER_PASSWORD
        self.origin = settings.FRONTEND_URL

    def send(self, email, subject, content):
        try :
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = Address("MSEUFCI Class Scheduling", "class_schedules", self.sender_mail)
            msg['To'] = email 
            msg.set_content(content)

            server = smtplib.SMTP(self.smtp_server_domain_name, self.port)

            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender_mail, self.pasword)

            server.send_message(msg)

        except Exception as e: 
            print(e)

        finally: 
            server.quit()


    def send_password_reset(self, email, token): 
        msg = EmailMessage()
        msg['Subject'] = 'MSEUFCI Scheduling Password Reset'
        msg['From'] = self.sender_mail 
        msg['To'] = email
        msg.set_content(f'''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="flex flex-col justify-center items-center w-full">
                <div class="relative flex min-h-screen flex-col justify-center overflow-hidden bg-gray-50 py-6 sm:py-12">
                    <img src="https://asset.cloudinary.com/dfua49gkk/fe43ea85497cc64f089494d27415a618" alt="" class="absolute top-1/2 left-1/2 max-w-none -translate-x-1/2 -translate-y-1/2" width="1308" />
                    <div class="absolute inset-0 bg-[url(/img/grid.svg)] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
                        <div class="relative bg-white px-6 pt-10 pb-8 shadow-xl ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg sm:rounded-lg sm:px-10">
                            <div class="mx-auto max-w-md">
                                <img src="https://res.cloudinary.com/dfua49gkk/image/upload/v1668132679/class-scheduling/logo-filled_heuqyp.png" alt="Tailwind Play" style="height: 64px"/>
                                <h1 class="text-2xl font-semibold font-sans">Manuel S. Enverga University Foundation Candelaria Incorporated.</h1>
                                <div class="divide-y divide-gray-300/50">
                                <div class="space-y-6 py-8 text-base leading-7 text-gray-600">
                                    <p>We have received your request for password reset</p>
                                    <p>Please follow this link to reset your password</p>
                                    <a href="{self.origin}/forgot-password" class="text-red-500 hover:text-red-600">Reset Password &rarr;</a>
                                </div>
                                <div class="pt-8 text-base font-semibold leading-7">
                                    <p class="text-gray-900">Login to website</p>
                                    <a href="{self.origin}/login" class="text-sky-500 hover:text-sky-600">MSEUFCI Scheduling &rarr;</a>
                                    </p>
                                </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        ''', subtype='html')

        with smtplib.SMTP(self.smtp_server_domain_name, self.port) as server: 
            server.starttls()
            server.login(self.sender_mail, self.pasword)
            server.send_message(msg)

    
    def send_account_verification(self, email, token): 
        msg = EmailMessage()
        msg['Subject'] = 'MSEUFCI Scheduling Password Reset'
        msg['From'] = self.sender_mail 
        msg['To'] = email
        msg.set_content(f'''
        <!DOCTYPE html>
        <html>

        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        </head>

        <body class="flex flex-col justify-center items-center w-full">
        <div class="relative flex min-h-screen flex-col justify-center overflow-hidden bg-gray-50 py-6 sm:py-12">
            <img src="https://asset.cloudinary.com/dfua49gkk/fe43ea85497cc64f089494d27415a618" alt="" class="absolute top-1/2 left-1/2 max-w-none -translate-x-1/2 -translate-y-1/2" width="1308" />
            <div
            class="absolute inset-0 bg-[url(/img/grid.svg)] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]">
            </div>
            <div
            class="relative bg-white px-6 pt-10 pb-8 shadow-xl ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg sm:rounded-lg sm:px-10">
            <div class="mx-auto max-w-md">
                <img src="https://res.cloudinary.com/dfua49gkk/image/upload/v1668132679/class-scheduling/logo-filled_heuqyp.png" alt="Tailwind Play" style="height: 64px"/>
                <h1 class="text-2xl font-semibold font-sans">Manuel S. Enverga University Foundation Candelaria Incorporated.
                </h1>
                <div class="divide-y divide-gray-300/50">
                <div class="space-y-6 py-8 text-base leading-7 text-gray-600">
                    <p>You've registered for MSEUFCI Class Scheduling System</p>
                    <p>Please follow this link to verify your account</p>
                    <a href="{self.origin}/verify-account/{token}" class="text-blue-500 hover:text-blue-600">Verify Account &rarr;</a>
                </div>
                <div class="pt-8 text-base font-semibold leading-7">
                    <p class="text-gray-900">Login to website</p>
                    <a href="{self.origin}/login" class="text-sky-500 hover:text-sky-600">MSEUFCI Scheduling &rarr;</a>
                    </p>
                </div>
                </div>
            </div>
            </div>
        </div>
        </div>
        </body>

        </html>
        ''', subtype='html')

        with smtplib.SMTP(self.smtp_server_domain_name, self.port) as server: 
            server.starttls()
            server.login(self.sender_mail, self.pasword)
            server.send_message(msg)


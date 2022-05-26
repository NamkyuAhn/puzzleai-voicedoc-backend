import re

from django.core.exceptions import ValidationError

regex_email    = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9-.]+$'
regex_password = '^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d~!@#$%^&*()+|=]{8,20}$' #'숫자', '문자' 무조건 1개 이상, '최소 8자에서 최대 20자' 허용

class Validation:
    def email_validate(value):
        if not re.match(regex_email,value):
            raise ValidationError('not in email format')
    def password_validate(value):
        if not re.match(regex_password,value):
            raise ValidationError('not in password format')
import secrets

def generate_otp_code():
    """
    Генерирует безопасный 6-значный одноразовый код (OTP).
    """
    return str(secrets.randbelow(900000) + 100000)

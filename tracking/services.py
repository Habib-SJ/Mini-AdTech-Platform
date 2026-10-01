from tracking.models import Click, Impression
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired


class InvalidClickTokenError(Exception):
    default_message = "The click token is invalid."
    def __init__(self, message=None):
        super().__init__(message or self.default_message)


class ClickTokenExpiredError(InvalidClickTokenError):   
    default_message = "Click token has expired."


class ClickTokenTamperedError(InvalidClickTokenError): 
    default_message = "The token signature is invalid or tampered with."

signer = TimestampSigner()

def sign_impression_id(impression_id):
    return signer.sign(str(impression_id))

def unsign_impression_id(signed_value, max_age_seconds=3600):
    try:
        original_value = signer.unsign(signed_value, max_age=max_age_seconds)
        return original_value
    except BadSignature:
        raise ClickTokenTamperedError
    except SignatureExpired:
        raise ClickTokenExpiredError
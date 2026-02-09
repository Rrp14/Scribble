from src.auth.security import hash_passwd,verify_passwd


def test_password_hash_and_verify():
    password="StrongPass@123"

    hashed=hash_passwd(password)

    assert hashed!=password


    assert verify_passwd(password,hashed) is True

    assert verify_passwd("WeakPass@123",hashed) is False
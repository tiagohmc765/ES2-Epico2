from greenherb.auth.password_hasher import PasswordHasher


def test_tu_auth_01_hash_de_password_devolve_valor_diferente_da_password_original():
    hasher = PasswordHasher()

    password_hash = hasher.hash("Admin123!")

    assert password_hash != "Admin123!"


def test_tu_auth_02_verify_devolve_true_para_password_correta():
    hasher = PasswordHasher()

    password_hash = hasher.hash("Admin123!")

    assert hasher.verify("Admin123!", password_hash) is True


def test_tu_auth_03_verify_devolve_false_para_password_errada():
    hasher = PasswordHasher()

    password_hash = hasher.hash("Admin123!")

    assert hasher.verify("Errada123!", password_hash) is False

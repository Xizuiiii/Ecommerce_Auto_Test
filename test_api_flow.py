def test_login_returns_real_access_token(api_client):
    assert api_client.token
    assert len(api_client.token) > 20

    profile = api_client.get_user_profile()
    assert profile["username"] == "emilys"
    assert profile["email"] == "emily.johnson@x.dummyjson.com"


def test_refresh_auth_session(api_client):
    refreshed_tokens = api_client.refresh_auth_session()

    assert refreshed_tokens.access_token
    assert refreshed_tokens.refresh_token
    assert api_client.get_user_profile()["username"] == "emilys"


def test_add_product_to_cart(api_client):
    cart = api_client.add_to_cart(item_id=15, user_id=1, quantity=1)

    assert cart["userId"] == 1
    assert cart["products"][0]["id"] == 15
    assert cart["products"][0]["quantity"] == 1
    assert cart["totalProducts"] >= 1


def test_get_user_cart_items(api_client):
    carts = api_client.get_cart_items(user_id=1)

    assert carts["carts"]
    assert carts["carts"][0]["userId"] == 1

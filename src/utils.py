from flask import request

def get_cookie(request):
    return request.cookies.get('login_cookie')


def extract_cookie_data(cookie):
    
    if cookie is None:
        return None

    cookie_data = {}

    [id, email, user_type] = cookie.split(":")
    cookie_data['id'] = id
    cookie_data['email'] = email
    cookie_data['user_type'] = user_type

    return cookie_data


def get_base_data(request):
    cookie = get_cookie(request)
    cookie_data = extract_cookie_data(cookie)

    if cookie:
        data = {'is_login': True, 'user_type': cookie_data['user_type'], "id": cookie_data["id"]}
    else:
        data = {'is_login': False, 'user_type': None}
    print(f'{data=}')
    return data
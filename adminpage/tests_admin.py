from django.test import TestCase, Client
from django.contrib.auth.models import User
from adminpage.views_admin import AdminLogin, AdminLogout
from codex.baseerror import ValidateError, PrivilegeError
import json

# 单元测试
# 测试管理员登录、非管理员登录和密码输入错误的情况
class AdminLoginUnitTest(TestCase):

    def setUp(self):
        User.objects.create_superuser('admin', 'a@test.com', '12345678a')
        User.objects.create_user('ordinaryUser', 'test@test.com', '12345678b')

    # 路由测试
    def test_login_url(self):
        c = Client()
        response = c.post('/api/a/login', {"username": "admin", "password": "12345678a"})
        self.assertEqual(response.status_code, 200)

    # 非管理员登录
    def test_login_ordinaryuser(self):
        admin_login = AdminLogin()
        admin_login.input = {}
        admin_login.input['username'] = 'ordinaryUser'
        admin_login.input['password'] = '12345678b'
        self.assertRaises(PrivilegeError, admin_login.post)

    # 管理员登录，密码错误
    def test_login_superuser_wrong_password(self):
        admin_login = AdminLogin()
        admin_login.input = {}
        admin_login.input['username'] = 'admin'
        admin_login.input['password'] = '12345678b'
        self.assertRaises(ValidateError, admin_login.post)

# 管理员登录：功能测试（需要移动到功能测试文件夹）
class AdminLoginFuncTest(TestCase):

    def setUp(self):
        pass

    # 管理员登录
    def test_login_superuser(self):
        c = Client()
        response = c.post('/api/a/login', {"username": "admin", "password": "12345678a"})
        response_content = response.content.decode()
        response_content_dict = json.loads(response_content)
        self.assertEqual(response_content_dict['code'], 0)
'''
class AdminLogoutTest(TestCase):

    def setUp(self):
        self.super_user = User.objects.create_superuser('admin', 'a@test.com', '12345678a')
        self.ordinary_user = User.objects.create_user('ordinaryUser', 'test@test.com', '12345678b')

    # 路由测试
    def test_logout_url(self):
        c = Client()
        # response = c.post('/api/a/login', {"username": "admin", "password": "12345678a"})
        #response = c.post('/api/a/logout')

    # 管理员登出
    def test_admin_logout(self):
        admin_logout = AdminLogout()
        admin_logout.request = self.super_user
        self.assertRaises(ValidateError, admin_logout.post)

    # 非管理员登出
'''

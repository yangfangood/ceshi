"""
  宠物模块 --- 异常场景测试
  测试各种异常情况：参数缺失、类型错误、边界值、重复创建等

"""
from http.client import responses

import pytest
import requests
import yaml
from pathlib import Path

from yaml import safe_load


class TestPetNegative:
    """宠物模块异常场景测试"""
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        config_path = Path(__file__).parent.parent/"config"/"config.yaml"
        with open(config_path,"r",encoding="utf-8") as f:  # 将打开的文件对象赋值给f
            config = yaml.safe_load(f)

        cls.base_url = config["env"]["base_url"]
        cls.timeout = config["env"].get("timeout",10)

        cls.max_response_time = config["env"].get("max_response_time",4)
        # 读取database部分
        cls.db_config = config.get("dababase",{})
        print(f"\n📁 配置加载成功: base_url={cls.base_url}")

    def setup_method(self):
        """每个测试前执行"""
        self.test_pet_id = 99999  # 使用一个较大的ID避免冲突

    def tearmethod(self):
        """每个测试后执行"""
        try:
            requests.delete(f"{self.base_url}/pet/{self.test_pet_id}",timeout=5)
        except:
            pass

    # 参数缺失测试

    def test_add_pet_missing_name(self):
        """创建宠物时，缺失name"""
        pet_data = {
            "id": self.test_pet_id,
            "status": "available",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
            # 缺少 name 字段
        }
        response = requests.post(
            f"{self.base_url}/pet",
            json = pet_data,
            timeout = self.timeout
        )

        #期望返回400 或者 422（参数错误）
        assert response.status_code in [400,422],f"期望400或422，实际是{response.status_code}"
        print(f"✅ 缺少name字段，正确返回{response.status_code}")

    def test_add_pet_missing_status(self):
        pet_data = {
            "id": self.test_pet_id,
            "name": "测试狗狗",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
            # 缺少 status 字段
        }

        response = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], \
            f"期望400或422，实际{response.status_code}"
        print(f"✅ 缺少status字段，正确返回{response.status_code}")

    def test_add_pet_missing_id(self):

        pet_data = {
            # "id": self.test_pet_id,
            "name": "测试狗狗",
            "status": "available",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
            # 缺少 id 字段
        }
        response = requests.post(
            f"{self.base_url}/pet",
            json = pet_data,
            timeout = self.timeout
        )
        # 有些API会自动生成ID，所以可能成功
        # 期望：要么成功（自动生成ID），要么返回错误
        assert response.status_code in [200, 400, 422], \
            f"状态码异常: {response.status_code}"

        if response.status_code == 200:
            # 如果成功，验证返回了ID
            data = response.json()
            assert "id" in data, "返回结果缺少id字段"
            print(f"✅ 缺少id字段，服务器自动生成了ID: {data['id']}")
        else:
            print(f"✅ 缺少id字段，正确返回{response.status_code}")

    # ===========参数类型错误测试==========
    def test_add_pet_id_wrong_type(self):
        """测试4：id 字段类型错误（传字符串）"""
        pet_data = {
            "id": "not_a_number",  # 应该是整数，这里传字符串
            "name": "测试狗狗",
            "status": "available",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        response = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        # 期望返回 400 或 422（类型错误）
        assert response.status_code in [400, 422], \
            f"期望400或422，实际{response.status_code}"
        print(f"✅ id类型错误，正确返回{response.status_code}")

    def test_add_pet_name_wrong_type(self):
        """测试5：name 字段类型错误（传数字）"""
        pet_data = {
            "id": self.test_pet_id,
            "name": 12345,  # 应该是字符串，这里传数字
            "status": "available",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        response = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        # 有些API会自动转换，所以可能成功
        assert response.status_code in [200, 400, 422], \
            f"状态码异常: {response.status_code}"

        if response.status_code == 200:
            # 如果成功，验证返回的是字符串
            data = response.json()
            assert isinstance(data["name"], str), "name应该是字符串"
            print(f"✅ name类型错误，服务器自动转换为字符串: {data['name']}")
        else:
            print(f"✅ name类型错误，正确返回{response.status_code}")

    # ==================== 3. 参数值非法测试 ====================

    def test_add_pet_invalid_status(self):
        """测试6：status 字段传入非法值"""
        pet_data = {
            "id": self.test_pet_id,
            "name": "测试狗狗",
            "status": "invalid_status_xxx",  # 非法状态
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        response = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        # 期望返回 400 或 422
        assert response.status_code in [400, 422], \
            f"期望400或422，实际{response.status_code}"
        print(f"✅ status值非法，正确返回{response.status_code}")

    def test_add_pet_negative_id(self):
        """测试7：id 字段传入负数"""
        pet_data = {
            "id": -1,  # 负数ID
            "name": "测试狗狗",
            "status": "available",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        response = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        # 期望：要么返回错误，要么接受负数
        assert response.status_code in [200, 400, 422], \
            f"状态码异常: {response.status_code}"
        print(f"✅ 负数ID测试完成，返回{response.status_code}")

    # ==================== 4. 边界值测试 ====================

    @pytest.mark.parametrize("name,expected_status", [
        ("", [200, 400, 422]),  # 空字符串
        ("a", [200, 400, 422]),  # 1个字符
        ("a" * 50, [200, 400, 422]),  # 50个字符
        ("a" * 100, [200, 400, 422]),  # 100个字符
        ("a" * 500, [200, 400, 422]),  # 500个字符（可能超长）
        ("测试狗狗🐶🐱🐭", [200, 400, 422]),  # emoji
        ("test@#$%^&*()", [200, 400, 422]),  # 特殊字符
        ("   ", [200, 400, 422]),  # 空格
    ])
    def test_add_pet_name_boundary(self, name, expected_status):
        """测试8：name 字段边界值测试"""
        pet_data = {
            "id": self.test_pet_id,
            "name": name,
            "status": "available",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        response = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        assert response.status_code in expected_status, \
            f"name='{name[:20]}...' 返回状态码 {response.status_code} 不在预期中"  # name[:20]：   取字符串的前 20 个字符

        if response.status_code == 200:
            data = response.json()
            print(f"✅ name='{name[:20]}...' 成功，返回name='{data['name']}'")
        else:
            print(f"✅ name='{name[:20]}...' 被拒绝，返回{response.status_code}")

    # ==================== 5. 重复创建测试 ====================

    def test_add_pet_duplicate_id(self):
        """测试9：重复创建相同ID的宠物"""
        pet_data = {
            "id": self.test_pet_id,
            "name": "第一次创建",
            "status": "available",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        # 第一次创建
        response1 = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )
        assert response1.status_code == 200, "第一次创建失败"
        print(f"✅ 第一次创建成功: ID={self.test_pet_id}")

        # 第二次创建相同ID
        response2 = requests.post(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        # 期望返回冲突或错误
        assert response2.status_code in [400, 409, 422], \
            f"期望返回错误码，实际{response2.status_code}"
        print(f"✅ 重复创建正确返回{response2.status_code}")

    # ==================== 6. 更新不存在资源测试 ====================

    def test_update_nonexistent_pet(self):
        """测试10：更新不存在的宠物"""
        nonexistent_id = 88888888
        pet_data = {
            "id": nonexistent_id,
            "name": "新名字",
            "status": "sold",
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        response = requests.put(
            f"{self.base_url}/pet",
            json=pet_data,
            timeout=self.timeout
        )

        # 期望返回 404（未找到）或 400
        assert response.status_code in [404, 400, 422], \
            f"期望404/400，实际{response.status_code}"
        print(f"✅ 更新不存在的宠物，正确返回{response.status_code}")

    # ==================== 7. 删除不存在资源测试 ====================

    def test_delete_nonexistent_pet(self):
        """测试11：删除不存在的宠物"""
        nonexistent_id = 88888888

        response = requests.delete(
            f"{self.base_url}/pet/{nonexistent_id}",
            timeout=self.timeout
        )

        # 期望返回 404（未找到）
        assert response.status_code == 404, \
            f"期望404，实际{response.status_code}"
        print(f"✅ 删除不存在的宠物，正确返回404")

    # ==================== 8. 查询参数无效测试 ====================

    def test_get_pet_invalid_id(self):
        """测试12：查询宠物时传入无效ID"""
        invalid_ids = [-1, 0, "abc", "not_a_number", 999999999]

        for pet_id in invalid_ids:
            response = requests.get(
                f"{self.base_url}/pet/{pet_id}",
                timeout=self.timeout
            )

            # 期望返回 404（未找到）或 400（参数错误）
            assert response.status_code in [404, 400], \
                f"ID={pet_id} 返回{response.status_code}"

        print(f"✅ 所有无效ID查询测试通过")

    # ==================== 9. 空请求体测试 ====================

    def test_add_pet_empty_body(self):
        """测试13：发送空请求体"""
        response = requests.post(
            f"{self.base_url}/pet",
            json={},  # 空字典
            timeout=self.timeout
        )

        # 期望返回 400 或 422
        assert response.status_code in [400, 422], \
            f"期望400/422，实际{response.status_code}"
        print(f"✅ 空请求体测试通过，返回{response.status_code}")

    # ==================== 10. 请求方法错误测试 ====================

    def test_wrong_http_method(self):
        """测试14：使用错误的HTTP方法"""
        # GET 请求不应该创建资源
        response = requests.get(
            f"{self.base_url}/pet",
            json={"id": self.test_pet_id, "name": "测试"},
            timeout=self.timeout
        )

        # 期望返回 405（方法不允许）或 400
        assert response.status_code in [405, 400, 404], \
            f"期望405/400，实际{response.status_code}"
        print(f"✅ 错误HTTP方法测试通过，返回{response.status_code}")




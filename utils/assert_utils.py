"""
    断言工具类封装
"""
import allure


class AssertUtils:
    @staticmethod
    @allure.step("验证状态码")
    def assert_status_code(response, expected):
        """
        验证状态码
        :param response: Response 对象
        :param expected: 期望的状态码或列表
        isinstance: 检查字段类型, 判断excepted的数据类型是不是列表
        这里为什么except的数据类型想要列表，因为有些情况期望的状态码是几个中的一个[200, 201, 202]
        """
        if isinstance(expected, list):
            assert response.status_code in expected,  f"期望状态码 {expected}，实际 {response.status_code}" # 断言状态码是否在except列表中
        else:
            assert response.status_code == expected, \
                f"期望状态码 {expected}，实际 {response.status_code}"

    @staticmethod
    @allure.step("验证响应时间")
    def assert_response_time(response, max_seconds=2):
        """
        验证响应时间
        :param response: Response 对象
        :param max_seconds: 最大允许时间（秒）
        """
        elapsed = response.elapsed.total_seconds()
        assert elapsed < max_seconds, \
            f"响应时间 {elapsed:.2f}秒 超过限制 {max_seconds}秒"

        allure.attach(f"{elapsed:.2f}秒", name="响应时间", attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    @allure.step("验证响应字段存在")
    def assert_field_exists(data, field):
        """
        验证字段存在
        :param data: 响应数据
        :param field: 字段名
        """
        assert field in data, f"响应结果缺少 {field} 字段"

    @staticmethod
    @allure.step("验证字段类型")
    def assert_field_type(data, field, expected_type):
        """
        验证字段类型
        :param data: 响应数据
        :param field: 字段名
        :param expected_type: 期望的类型
        """
        actual_type = type(data[field])
        assert isinstance(data[field], expected_type), \
            f"{field} 应该是 {expected_type.__name__}，实际是 {actual_type.__name__}"

    @staticmethod
    @allure.step("验证字段值")
    def assert_field_value(data, field, expected_value):
        """
        验证字段值
        :param data: 响应数据
        :param field: 字段名
        :param expected_value: 期望的值
        """
        actual_value = data[field]
        assert actual_value == expected_value, \
            f"{field} 期望 {expected_value}，实际 {actual_value}"

    @staticmethod
    @allure.step("验证宠物数据")
    def assert_pet_equal(actual, expected):
        """
        验证两个宠物数据是否相等
        :param actual: 实际数据
        :param expected: 期望数据
        """
        # 验证基本字段
        AssertUtils.assert_field_value(actual, "id", expected["id"])
        AssertUtils.assert_field_value(actual, "name", expected["name"])
        AssertUtils.assert_field_value(actual, "status", expected["status"])

        # 验证 category
        if "category" in expected:
            assert "category" in actual, "缺少 category 字段"
            AssertUtils.assert_field_value(actual["category"], "id", expected["category"]["id"])
            AssertUtils.assert_field_value(actual["category"], "name", expected["category"]["name"])

        # 验证 photoUrls
        if "photoUrls" in expected:
            assert "photoUrls" in actual, "缺少 photoUrls 字段"
            assert actual["photoUrls"] == expected["photoUrls"], \
                f"photoUrls 不一致: 期望 {expected['photoUrls']}, 实际 {actual['photoUrls']}"

    @staticmethod
    @allure.step("验证响应结构")
    def assert_response_structure(data, required_fields):
        """
        验证响应结构
        :param data: 响应数据
        :param required_fields: 必要字段列表
        """
        for field in required_fields:
            AssertUtils.assert_field_exists(data, field)
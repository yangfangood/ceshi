"""
    创建测试数据工厂
"""
"""
测试数据工厂
"""
import random
from faker import Faker

fake = Faker(locale='zh_CN')


class PetDataFactory:
    """宠物测试数据工厂"""

    @staticmethod
    def create_pet_data(pet_id=None, name=None, status=None, category=None, photo_urls=None):
        """
        动态生成宠物测试数据
        :param pet_id: 宠物 ID，默认随机
        :param name: 宠物名称，默认随机
        :param status: 宠物状态，默认随机
        :param category: 分类，默认随机
        :param photo_urls: 照片 URL，默认随机
        :return: 宠物数据字典
        """
        return {
            "id": pet_id or fake.random_int(1000, 9999),
            "name": name or fake.name(),
            "status": status or random.choice(["available", "pending", "sold"]),
            "category": category or {
                "id": fake.random_int(1, 100),
                "name": fake.word()
            },
            "photoUrls": photo_urls or [fake.url() for _ in range(random.randint(1, 3))]
        }

    def create_invalid_pet_data(scenario):
        """
        创建无效的测试数据
        :param scenario: 场景类型--告诉函数要生成哪种错误场景的数据。
        :return: 无效的宠物数据
        """
        if scenario == "missing_name":
            return {
                "id":fake.random_int(1000,9999),
                "status": random.choice(["available", "pending", "sold"])  # 有效的状态
            }
        elif scenario == "missing_status":
            return {
                "id":fake.random_int(1000,9999),
                "name":fake.name()
            }
        elif scenario == "wrong_id_type":
            return {
                "id": fake.word(),
                "name": fake.name(),
                "status": "available"
            }
        elif scenario == "invalid_status":
            return {
                "id": fake.random_int(1000, 9999),
                "name": fake.name(),
                "status": "invalid_status_xxx"
            }
        return {}

    @staticmethod
    def get_boundry_name():
        """获取边界值测试数据
           提供一组边界值测试数据
        """
        return [
            ("", "空字符串"),
            ("a", "1个字符"),
            ("a" * 50, "50个字符"),
            ("a" * 100, "100个字符"),
            ("测试狗狗🐶🐱🐭", "emoji"),
            ("test@#$%^&*()", "特殊字符"),
        ]
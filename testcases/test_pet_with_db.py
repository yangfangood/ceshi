"""
宠物模块测试 - 带数据库验证
"""
import allure
import pytest
import time


@allure.feature("宠物管理模块")
class TestPetAPIWithDB:
    """宠物模块测试（含数据库验证）"""

    @allure.story("新增宠物")
    class TestAddPet:
        """新增宠物测试组"""

        @pytest.mark.parametrize("name,status", [
            ("测试狗狗", "available"),
            ("测试猫咪", "pending"),
            ("测试兔子", "sold")
        ])
        @allure.title("新增宠物并验证数据库 - {name}")
        def test_add_pet_with_db(self, pet_api, assert_utils, db_utils, test_pet_id, name, status):
            """测试新增宠物，并验证数据正确写入数据库"""

            # 1. 准备数据
            pet_data = {
                "id": test_pet_id,
                "name": name,
                "status": status,
                "category": {"id": 1, "name": "test"},
                "photoUrls": ["https://test.com/1.jpg"]
            }

            # 2. 调用 API 创建宠物
            response = pet_api.create_pet(pet_data)
            assert_utils.assert_status_code(response, 200)

            # 3. 验证 API 返回数据
            data = response.json()
            assert_utils.assert_pet_equal(data, pet_data)

            # 4. 验证数据库（关键步骤）
            # 注意：可能需要等待数据库同步
            time.sleep(0.5)  # 短暂等待，确保数据写入
            db_utils.verify_pet(test_pet_id, {
                "id": test_pet_id,
                "name": name,
                "status": status
            })

            # 5. 清理：删除宠物
            pet_api.delete_pet(test_pet_id)
            # 可选：验证数据库中已被删除
            time.sleep(0.5)
            db_pet = db_utils.get_pet(test_pet_id)
            assert db_pet is None, f"清理后数据库中还存在 ID={test_pet_id} 的宠物"

            print(f"✅ 测试通过: {name} - {status}")

    @allure.story("数据库验证")
    class TestDBOnly:
        """纯数据库验证测试"""

        @allure.title("验证数据库中已存在的宠物")
        def test_verify_existing_pet(self, pet_api, assert_utils, db_utils):
            """验证通过 API 创建的宠物确实在数据库中"""
            test_id = int(time.time() * 1000) % 1000000
            pet_data = {
                "id": test_id,
                "name": "数据库验证狗",
                "status": "available",
                "category": {"id": 1, "name": "test"},
                "photoUrls": ["https://test.com/1.jpg"]
            }

            # 创建
            create_response = pet_api.create_pet(pet_data)
            assert_utils.assert_status_code(create_response, 200)

            # 等待数据库同步
            time.sleep(0.5)

            # 验证数据库
            db_utils.verify_pet(test_id, pet_data)

            # 清理
            pet_api.delete_pet(test_id)
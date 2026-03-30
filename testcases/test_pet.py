"""
    宠物模块测试
"""
from asyncio import timeout
from pathlib import Path

# testcases/test_pet.py
import yaml
import os
import requests # 发http请求的工具
import pytest # 测试框架-帮我们运行测试的工具
import pymysql
from jsonschema import validate, ValidationError
import json
import json # 处理json数据的工具

#测试类
class TestPetAPI:
    """宠物模块接口测试"""


    """
        @classmethod是python的类方法装饰器 ， 用来定义属于类本身而不是实例的方法 
        类方法只加载一次，所有测试共享
        
        概念对比：
               1. 实例方法： 第一个参数：self    调用方法：  实例.方法()               访问内容：  可以访问实例属性和类属性      指向：当前实例
               2. 类方法：   第一个参数: cls    调用方法： 类.方法()或实例.方法()      访问内容：  只能 访问类属性              指向：当前类
               3. 静态方法：  第一个参数: 无     调用方法： 类.方法()或实例.方法()      访问内容：不能访问类属性
        # 方式1：通过类调用
                MyClass.my_class_method()  # ✅ 推荐

        # 方式2：通过实例调用
                obj = MyClass()
                obj.my_class_method()  # ✅ 也可以 
        初始化配置的应用场景              
    """

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        # 加载配置
        config_path = Path(__file__).parent.parent/"config"/"config.yaml"
        with  open(config_path,"r",encoding="utf-8") as f: # as f 把打开的文件对象赋值给f
            # 解析后的 config 是一个字典
            config = yaml.safe_load(f) #安全加载方法，把yaml内容转成python对象，只加载标准类型
        # 此处 使用with 不需要在手动关闭文件
        cls.base_url = config["env"]["base_url"]
        cls.timeout = config["env"].get("timeout",10)
        """
        .get()的基本语法：
        字典.get(键, 默认值)
        dict["key"] 键不存在时会报错
        dict.get("key") 键不存在时返回none
        dict.get("key", 默认值) 键不存在时 返回默认值
        """
        cls.max_response_time = config["env"].get("max_response_time",2) # 从配置中读取max_response_time，如果没有这个字段就默认值为2
        # 从配置中取出 database 部分
        cls.db_config = config.get("database", {})  # ← 这里设置 db_config
        # 打印配置加载成功
        print(f"\n📁 配置加载成功: base_url={cls.base_url}")


    def setup_method(self):
        """
        每个测试方法执行前运行

        :return:
        """
        self.pet_id = 12345  # 固定测试ID


    def teardown_method(self):
        """
        是 pytest 中每个测试方法执行后自动运行的钩子函数，用于清理测试数据。
        每个测试方法执行后运行，确保清理
        test_add_pet() 假如这个方法测试失败，里面的断言失败，测试中断，但是 teardown_method 仍然会执行！✅ 宠物被删除
                       如果没有teardown_method，失败后创建的宠物不会被删除，导致服务器上积累大量测试数据

        在方法末尾清理的明显确实是，当测试过程中失败，则 不能执行清理数据的部分


        :return:
        """
        try:
            delete_response = requests.delete(
                f"{self.base_url}/pet/{self.pet_id}",
                timeout=5
            )
            if delete_response.status_code == 200:
                print(f"🧹 清理成功: 已删除宠物 ID={self.pet_id}")
            elif delete_response.status_code == 404:
                print(f"ℹ️ 清理跳过: 宠物 ID={self.pet_id} 不存在")
            else:
                print(f"⚠️ 清理异常: 状态码 {delete_response.status_code}")
        except Exception as e:
            print(f"⚠️ 清理警告: {e}")


    def test_get_pet_by_id(self):
        """测试根据ID查询宠物 - 正向用例"""
        pet_id = 1

        response = requests.get(
            f"{self.base_url}/pet/{pet_id}",
            headers={"accept": "application/json"},
            timeout=self.timeout
        )

        # 断言
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        assert response.elapsed.total_seconds() < self.max_response_time, \
            f"响应时间过长: {response.elapsed.total_seconds():.2f}秒"
        assert response.json()["id"] == pet_id, "返回的ID不匹配"
        assert "name" in response.json(), "返回结果缺少name字段"

    def test_get_pet_not_found(self):
        """测试查询不存在的宠物 - 异常用例"""
        pet_id = 99999999

        response = requests.get(
            f"{self.base_url}/pet/{pet_id}",
            timeout=self.timeout
        )

        assert response.status_code == 404, "期望404"
        assert response.json()["message"] == "Pet not found", "错误消息不正确"

    @pytest.mark.parametrize("name,status", [
        ("测试狗狗", "available"),
        ("测试猫咪", "pending"),
        ("测试兔子", "sold")
    ])
    def test_add_pet_2(self, name, status):
        # ========准备数据===========
        pet_data = {
            "id": 12345,
            "name": name,
            "status": status,
            "category": {"id": 1, "name": name},
            "photoUrls": ["https://test.com/1.jpg"]  # 地址这里为什么使用[]
        }
        # ===========发送请求=========
        # response对象包含状态码、响应数据

        import time
        start_time = time.time()

        response = requests.post(f"{self.base_url}/pet",
                                 headers={"Content-Type": "application/json"},
                                 json=pet_data,
                                 timeout = self.timeout)
        response_time = time.time()-start_time
        data = response.json()

        assert response.status_code == 200,f"期望200，实际{response.status_code}"
        # 断言响应时间
        assert response_time < self.max_response_time,f"响应时间过长：{response_time:.2f},限制：{self.max_response_time}s"
        """
            response.headers.get("Content-Type","") 响应头中找Content-Type字段，如果没有这个字段返回空字符串
            .startswith("application/json") 检查字符串是否以application/json开头 返回值为true 或者false
        """
        assert response.headers.get("Content-Type","").startswith("application/json"),"返回格式不是json"

        # 断言响应结构完整性
        """
            assert 元素 in 容器, "错误信息"
            如果元素在容器中，断言通过；如果元素不在容器中，断言失败并显示错误信息。
        """
        required_fields = ["id","name","status","category","photoUrls"]
        for field in required_fields:
            assert field in data,f"返回结果缺少{field}字段"

        # ========== 断言5：字段类型验证 ==========
        """
            isinstance()函数用于判断一个对象是否属于指定的数据类型
            isinstance(对象, 类型)
            返回值：  true
                    false
            
        """
        assert isinstance(data["id"],int),f"id 应该是整数，实际是 {type(data['id'])}"
        assert isinstance(data["name"], str), f"name 应该是字符串"
        assert isinstance(data["status"], str), f"status 应该是字符串"
        assert isinstance(data["category"], dict), f"category 应该是字典"
        assert isinstance(data["photoUrls"], list), f"photoUrls 应该是列表"

        #======数据内容验证====
        assert data["id"] == pet_data.get("id"),f""
        assert data["name"] == pet_data.get("name"),f""
        assert data["status"] == pet_data.get("status"),f""
        # ====断言  category 验证 ===
        assert data["category"]["id"] == pet_data["category"]["id"], \
            f"category.id 不一致"
        assert data["category"]["name"] == pet_data["category"]["name"], \
            f"category.name 不一致"

        # 断言状态值的合法性
        allowed_statuses = ["available", "pending", "sold"]
        assert data["status"] in allowed_statuses, \
            f"status 必须是 {allowed_statuses} 之一，实际是 {data['status']}"
        # ========== 断言9：photoUrls 验证 ==========
        assert len(data["photoUrls"]) > 0, "photoUrls 不能为空"
        # 比较两个列表中第一个元素是否相等
        # pet_data["photoUrls"] = ["https://test.com/1.jpg"]
        # pet_data["photoUrls"][0] = "https://test.com/1.jpg"

        assert data["photoUrls"][0] == pet_data["photoUrls"][0], \
            f"photoUrls 不一致"

        # ========== 清理数据 ==========
        delete_response = requests.delete(f"{self.base_url}/pet/{pet_data['id']}")
        assert delete_response.status_code in [200, 404], \
            f"清理失败，状态码 {delete_response.status_code}"

        print(f"\n✅ 测试通过: {name} - {status}")
        print(f"   响应时间: {response_time:.2f}秒")



    @pytest.mark.parametrize("name,status", [
        ("测试狗狗", "available"),
        ("测试猫咪", "pending"),
        ("测试兔子", "sold")
    ])
    def try_test_add_pet(self, name, status):
        """测试新增宠物 - 参数化用例"""
        pet_data = {
            "id": 12345,  # 固定ID方便清理
            "name": name,
            "status": status,
            "category": {"id": 1, "name": "test"},
            "photoUrls": ["https://test.com/1.jpg"]
        }

        # 新增宠物
        response = requests.post(
            f"{self.base_url}/pet",
            headers={"Content-Type": "application/json"},
            json=pet_data  # 要发送的数据，请求体-----自动把 Python 字典转换成 JSON 字符串
        )

        # 验证api返回成功
        assert response.status_code == 200
        pet_id = response.json()["id"]
        # 数据库验证
        # 连接数据库
        conn = pymysql.connect(
            host = "localhost",
            user = "test_user",
            password = "admin",
            database = "petstore"
        )
        try:
            # try中是尝试执行的代码（可能会出错）
            cursor = conn.cursor() # 创建游标
            cursor.execute("SELECT name,status FROM pets WHERE id = %s",(pet_id,))  # 执行SQL
            db_result = cursor.fetchone() # 获取查询结果
            #断言数据库中有这条记录
            assert db_result is not None,f"数据库中找不到ID为{pet_id}的宠物"

            # 断言数据库中的数据正确
            assert db_result[0] == name,f"数据库中的名字{db_result[0]}与预期{name}不一致"
            assert db_result[1] == status, f"数据库中的状态{db_result[1]}与预期{status}不一致"
        finally:
            # 无论如何都会执行的代码
            cursor.close() # 4. 关闭游标（无论是否出错都会执行）
            conn.close()   # 5. 关闭连接（无论是否出错都会执行）
        """
            with conn.cursor() as cursor:
        cursor.execute("SELECT name,status FROM pets WHERE id = %s", (pet_id,))
        db_result = cursor.fetchone()
        
        assert db_result is not None, f"数据库中找不到ID为{pet_id}的宠物"
        assert db_result[0] == name, f"数据库中的名字{db_result[0]}与预期{name}不一致"
        assert db_result[1] == status, f"数据库中的状态{db_result[1]}与预期{status}不一致"
# 退出 with 块后，cursor 和 conn 自动关闭
        """


        assert response.elapsed.total_seconds() < 2 ,f"响应时间过长：{response.elapsed.total_seconds()}" #断言响应时间不超过2s
        assert response.headers["Content-Type"] == "application/json" , "返回格式不是json"
        data = response.json()
        required_fields = ["id","name","status","category","photoUrls"]
        for field in required_fields:
            assert field in data,f"返回结果缺少{field}字段"
        # 检查字段类型
        assert isinstance(data["id"],int),f"id应该是整数,实际是{type(data['id'])}" #后面id用单引号，否则字符串会提前结束
        assert isinstance(data["name"],str),f"name应该是字符串"
        assert isinstance(data["status"],str),f"status应该是字符串"
        assert response.json()["name"] == name
        assert response.json()["status"] == status

        # 2. 验证 category 内容正确（新增）
        assert data["category"]["id"] == pet_data["category"]["id"]
        assert data["category"]["name"] == pet_data["category"]["name"]

        # 3. 验证 photoUrls 正确（新增）
        assert data["photoUrls"] == pet_data["photoUrls"]

        # 4. 验证状态值在允许范围内（新增）
        allowed_statuses = ["available", "pending", "sold"]
        assert data["status"] in allowed_statuses, f"status 必须是 {allowed_statuses} 之一"
        # 清理：删除刚创建的宠物
        requests.delete(f"{self.base_url}/pet/{pet_data['id']}")

    # ==================== 辅助方法 ====================

    def _verify_pet_in_database(self, pet_data):
        """验证数据库中的宠物数据"""
        try:
            conn = pymysql.connect(
                host=self.db_config.get("host"),
                user=self.db_config.get("user"),
                password=self.db_config.get("password"),
                database=self.db_config.get("database"),
                charset="utf8mb4"
            )

            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT name, status FROM pets WHERE id = %s",
                    (pet_data["id"],)
                )
                db_result = cursor.fetchone()

                assert db_result is not None, f"数据库中找不到ID为{pet_data['id']}的宠物"
                assert db_result[0] == pet_data["name"], \
                    f"数据库中的名字 {db_result[0]} 与预期 {pet_data['name']} 不一致"
                assert db_result[1] == pet_data["status"], \
                    f"数据库中的状态 {db_result[1]} 与预期 {pet_data['status']} 不一致"

                print(f"   ✅ 数据库验证通过")

        except pymysql.Error as e:
            print(f"   ⚠️ 数据库验证失败: {e}")
            # 数据库验证失败不中断测试，只打印警告
            # 如果需要严格验证，可以改为 raise
        finally:
            if conn:
                conn.close()


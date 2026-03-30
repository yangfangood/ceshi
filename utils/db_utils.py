"""
    数据库验证
"""
import pymysql
import allure

class DBUtils:
    def __init__(self, config):
        """
        DBUtils 的构造函数
                初始化数据库连接
                :param config: 数据库配置字典
                构造函数的执行过程：
                1. 创建对象
                2. 自动调用__init__
                3. 执行__init__的代码

                """
        self.config = config
        self.conn = None

    def _get_connection(self):
        """获取数据库连接"""
        if self.conn is None or not self.conn.open:
            self.conn = pymysql.connect(
                host = self.config.get("host"),
                port = self.config.get("port"),
                user = self.config.get("user"),
                password = self.config.get("password"),
                database = self.config.get("database"),
                charset = self.config.get("charset"),
                cursorclass=pymysql.cursors.DictCursor  # 返回字典格式
            )
        return self.conn

    def close(self):
        """关闭数据库连接"""
        if self.conn and self.conn.open:
            self.conn.close()
            self.conn = None

    @allure.step("查询数据库中的宠物")
    def get_pet(self,pet_id):
        """
        根据id查询宠物
        :param pet_id:  宠物id
        :return: pet_data
        """
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id,name,status,category_id,photo_urls FROM pets WHERE id=%s",
                (pet_id,)
            )
            return cursor.fetchone()

    def verify_pet(self,pet_id,expected_data):
        """

        :param pet_id:
        :param except_data:期望的宠物数据
        :return:
        """
        actual = self.get_pet(pet_id)
        assert actual is not None,f"数据库中找不到 ID 为 {pet_id} 的宠物"

        # 验证字段
        assert actual["id"] == expected_data["id"],f"ID 不匹配: 期望 {self.expected_data['id']}, 实际 {actual['id']}"
        assert actual["name"] == expected_data["name"], \
            f"name 不匹配: 期望 {expected_data['name']}, 实际 {actual['name']}"
        assert actual["status"] == expected_data["status"], \
            f"status 不匹配: 期望 {expected_data['status']}, 实际 {actual['status']}"
        allure.attach(f"数据库验证通过: ID={pet_id}", name="数据库验证")

    @allure.step("删除数据库中的宠物")
    def delete_pet(self, pet_id):
        """
        删除数据库中的宠物记录
        :param pet_id: 宠物 ID
        """
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM pets WHERE id = %s", (pet_id,))
            conn.commit()
        allure.attach(f"已删除数据库中的宠物 ID={pet_id}", name="数据库清理")

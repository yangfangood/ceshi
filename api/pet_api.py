"""
        宠物模块api封装
"""
import allure

from api.base_api import BaseAPI


class PetAPI(BaseAPI):

    # 定义所有接口路径
    PET_PATH = "/pet"
    PET_BY_ID_PATH = "/pet/{pet_id}"
    PET_FIND_BY_STATUS = "/pet/findByStatus"

    @allure.step("宠物创建")
    def create_pet(self,pet_data):
        """
        创建宠物
        :param pet_data: 宠物数据
        :return: response 对象
        """
        return self.post(self.PET_PATH,json=pet_data)
    @allure.step("宠物查询")
    def get_pet(self,pet_id):
        """

        :param pet_id: 宠物id
        :return: 返回查询结果
        """
        return self.get(self.PET_BY_ID_PATH)

    @allure.step("宠物删除")
    def pet_delete(self,pet_id):
        """

        :param pet_id: 宠物id
        :return: 删除结果
        """
        return self.delete(self.PET_BY_ID_PATH)

    @allure.step("宠物更新")
    def pet_update(self,pet_data):
        """
         覆盖原有宠物信息
        :param pet_data: 宠物信息
        :return:
        """
        return self.put(self.PET_PATH,json=pet_data)

    @allure.step("删除宠物")
    def delete_pet(self, pet_id):
        path = self.PET_BY_ID_PATH.format(pet_id=pet_id)
        return self.delete(path)


    @allure.step("按状态查询宠物")
    def find_by_status(self, status):
        """
        按状态查询宠物列表
        :param status: 宠物状态
        :return: Response 对象
        """
        return self.get(self.PET_FIND_BY_STATUS, params={"status": status})


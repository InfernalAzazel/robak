class JdySerialize:
    """
    简道云数据序列化

    """

    @staticmethod
    def subform(subform_field, data):
        """
        子表单创建和更新 JSON 序列化

        例子:
                subform_field = '_widget_1623150457402'

                data = [{
                '_id': '60bf5e3456262300083b2775',
                '_widget_1623150457454': '启用',
                '_widget_1623150457516': '百事',
                '_widget_1623150457539': '002',
                '_widget_1623150923283': '张三002'
                    }, {
                '_id': '60bf5e91ff26fc00077e2f9d',
                '_widget_1623150457454': '启用',
                '_widget_1623150457516': '可乐',
                '_widget_1623150457539': '001',
                '_widget_1623150923283': '张三001'
                }]

        :param subform_field: string 子表单字段名称
        :param data: list 数据
        :return: subform_data JSON
        """

        subform_data = {subform_field: {}}
        subform_data[subform_field]['value'] = []

        children = {}

        for data_value in data:
            for key, value in data_value.items():
                if key == '_id':
                    children[key] = {}
                    children[key]['value'] = value
                else:
                    children[key] = {}
                    children[key]['value'] = value
            subform_data[subform_field]['value'].append(children)
            children = {}

        # logger.info(subform_data)
        return subform_data

    @staticmethod
    def member_array_err_to_none(value, name):
        """
        防止多选成员取空值导致异常

        :param value: json
        :param name: string
        :return: result
         """
        arr = []
        if len(value[name]) <= 0:
            return None

        for v in value[name]:
            arr.append(v['username'])
        return arr

    @staticmethod
    def member_err_to_none(value, name):
        """
        防止成员取空值导致异常

        :param value: json
        :param name: string
        :return: result
         """
        try:
            return value[name]['username']
        except:
            return None

    @staticmethod
    def department_err_to_none(value, name):
        """
        防止部门取空值导致异常

        :param value: json
        :param name: string
        :return: result
        """
        try:
            return value[name]['dept_no']
        except:
            return None

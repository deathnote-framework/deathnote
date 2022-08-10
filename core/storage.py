class LocalStorage:
    @staticmethod
    def get_all():
        return globals().keys()

    @staticmethod
    def add(name):
        globals()[name] = None

    @staticmethod
    def set(name, value):
        globals()[name] = value

    @staticmethod
    def update(name, value):
        try:
            globals()[name].update(value)
        except Exception:
            pass

    @staticmethod
    def add_array(name, value):
        try:
            globals()[name].append(value)
        except Exception:
            pass

    @staticmethod
    def get_array(name, value):
        try:
            return globals()[name][value]
        except Exception:
            return None

    @staticmethod
    def set_array(name, value1, value2):
        try:
            globals()[name][value1] = value2
        except Exception:
            pass

    @staticmethod
    def delete_element(name, value):
        try:
            del globals()[name][value]
        except Exception:
            pass

    @staticmethod
    def delete(name):
        try:
            del globals()[name]
        except Exception:
            pass

    @staticmethod
    def get(name):
        try:
            return globals()[name]
        except Exception:
            return None


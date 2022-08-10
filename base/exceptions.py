class DeathnoteException(Exception):
    def __init__(self, msg: str = ""):
        super(DeathnoteException, self).__init__(msg)

class OptionValidationError(DeathnoteException):
    pass

class StopThreadPoolExecutor(DeathnoteException):
    pass

class WasNotFoundException(DeathnoteException):
    pass

class MaxLengthException(DeathnoteException):
    pass

from spiflash.serialflash import SerialFlashManager


class Spi(SerialFlashManager):


    @staticmethod
    def close(device):
        if device:
            device._spi._controller.terminate()
            
            

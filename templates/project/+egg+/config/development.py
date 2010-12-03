from pecan.configuration import PecanConfig

class Development(PecanConfig):
    port    = '8080'
    host    = '0.0.0.0'
    threads = 1


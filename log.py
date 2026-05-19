class ConsoleLogger:
    LEVELS = {"INFO", "WARN", "DEBUG", "ERROR", "SUCCESS"}

    @staticmethod
    def log(msg: str, level: str = "INFO"):
        level = level.upper()
        if level not in ConsoleLogger.LEVELS:
            level = "INFO"
        print(f"[{level}] {msg}")

    @staticmethod
    def info(msg: str):
        ConsoleLogger.log(msg)

    @staticmethod
    def warn(msg: str):
        ConsoleLogger.log(msg, "WARN")

    @staticmethod
    def debug(msg: str):
        ConsoleLogger.log(msg, "DEBUG")

    @staticmethod
    def error(msg: str):
        ConsoleLogger.log(msg, "ERROR")

    @staticmethod
    def success(msg: str):
        ConsoleLogger.log(msg, "SUCCESS")

    @staticmethod
    def error_generic(exception: Exception):
        ConsoleLogger.log(f"Unexpected error occurred: {exception}", "ERROR")
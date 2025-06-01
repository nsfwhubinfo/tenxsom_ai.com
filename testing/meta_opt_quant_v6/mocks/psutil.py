
class Process:
    def memory_info(self):
        class MemInfo:
            rss = 100 * 1024 * 1024  # 100MB dummy
        return MemInfo()

def cpu_count():
    import multiprocessing
    return multiprocessing.cpu_count()

class virtual_memory:
    total = 8 * 1024**3  # 8GB dummy

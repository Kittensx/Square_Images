import os
import psutil
import multiprocessing


class WorkerAdvisor:
    @staticmethod
    def get_recommended_workers():
        cpu_count = multiprocessing.cpu_count()
        available_memory = psutil.virtual_memory().available / (1024 ** 3)

        if available_memory < 4:
            return max(2, cpu_count // 2)
        elif available_memory > 16:
            return min(cpu_count * 2, cpu_count + 4)
        return cpu_count


class SystemEstimator:
    def __init__(self, bin_folder):
        self.bin_folder = bin_folder        

    def get_image_info(self):
        total_size = 0
        total_images = 0
        for root, _, files in os.walk(self.bin_folder):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".nef")):
                    fp = os.path.join(root, file)
                    total_size += os.path.getsize(fp)
                    total_images += 1
        return total_images, total_size

    def calculate_overhead(self):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk_io = psutil.disk_io_counters().read_time + psutil.disk_io_counters().write_time

        factor = 1.0
        if cpu > 50:
            factor += (cpu - 50) / 100
        if mem > 50:
            factor += (mem - 50) / 100

        disk_penalty = min(disk_io / 2000, 0.5)
        return max(1.0, min(factor + disk_penalty, 1.5))

    def estimate_processing_time(self, avg_time_per_mb=0.02):
        images, total_size = self.get_image_info()
        size_mb = total_size / (1024 ** 2)
        workers = WorkerAdvisor.get_recommended_workers()
        overhead = self.calculate_overhead()

        base_time = size_mb * avg_time_per_mb
        adjusted_time = base_time / workers * overhead

        return {
            "total_images": images,
            "total_size_mb": size_mb,
            "max_workers": workers,
            "overhead_factor": overhead,
            "time_per_image": (base_time / images) if images else 0,
            "sequential_time": base_time,
            "estimated_time": adjusted_time
        }

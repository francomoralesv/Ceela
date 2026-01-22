#!/usr/bin/env python3
"""
Script para detectar recursos del sistema y calcular configuración óptima
para Docker y Gunicorn.
"""

import os
import sys
import platform
import subprocess
import json


def get_cpu_count():
    """Obtiene el número de CPUs/cores disponibles"""
    try:
        # Intenta obtener cores físicos
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["sysctl", "-n", "hw.physicalcpu"],
                capture_output=True,
                text=True,
                check=True
            )
            physical_cores = int(result.stdout.strip())

            result = subprocess.run(
                ["sysctl", "-n", "hw.logicalcpu"],
                capture_output=True,
                text=True,
                check=True
            )
            logical_cores = int(result.stdout.strip())

        elif platform.system() == "Linux":
            # Cores físicos
            result = subprocess.run(
                ["lscpu", "-p=CORE"],
                capture_output=True,
                text=True,
                check=True
            )
            cores = [line for line in result.stdout.split('\n') if not line.startswith('#') and line.strip()]
            physical_cores = len(set(cores))

            # Cores lógicos (con hyperthreading)
            logical_cores = os.cpu_count()
        else:
            # Fallback
            physical_cores = os.cpu_count()
            logical_cores = os.cpu_count()

        return physical_cores, logical_cores
    except Exception as e:
        print(f"⚠️  Error detectando CPUs: {e}")
        cpu_count = os.cpu_count() or 4
        return cpu_count, cpu_count


def get_memory_info():
    """Obtiene información de memoria del sistema"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                check=True
            )
            memory_bytes = int(result.stdout.strip())
            memory_gb = memory_bytes / (1024 ** 3)

        elif platform.system() == "Linux":
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                mem_total = [line for line in meminfo.split('\n') if 'MemTotal' in line][0]
                memory_kb = int(mem_total.split()[1])
                memory_gb = memory_kb / (1024 ** 2)
        else:
            memory_gb = 8.0  # Fallback

        return memory_gb
    except Exception as e:
        print(f"⚠️  Error detectando memoria: {e}")
        return 8.0


def calculate_workers(physical_cores, workload_type="balanced"):
    """
    Calcula el número óptimo de workers según el tipo de carga

    workload_type:
    - "io_bound": Muchas operaciones I/O (DB, APIs externas) - más workers
    - "cpu_bound": Cálculos intensivos - menos workers
    - "balanced": Mix de ambos (recomendado)
    """
    if workload_type == "io_bound":
        # Para I/O intensivo: 2-4 workers por core
        workers = (physical_cores * 3) + 1
    elif workload_type == "cpu_bound":
        # Para CPU intensivo: 1-2 workers por core
        workers = (physical_cores * 2) + 1
    else:  # balanced
        # Fórmula estándar de Gunicorn: (2 x cores) + 1
        workers = (physical_cores * 2) + 1

    return workers


def calculate_threads(workers, memory_gb):
    """Calcula threads óptimos por worker"""
    # Cada worker con threads consume más memoria
    # Regla general: 2-4 threads por worker
    if memory_gb >= 16:
        threads = 4
    elif memory_gb >= 8:
        threads = 3
    else:
        threads = 2

    return threads


def calculate_postgres_config(memory_gb, cores):
    """Calcula configuración óptima para PostgreSQL"""
    # Shared buffers: 25% de RAM (máximo recomendado)
    shared_buffers_gb = min(int(memory_gb * 0.25), 8)

    # Effective cache size: 50-75% de RAM
    effective_cache_gb = int(memory_gb * 0.5)

    # Work mem: RAM / (max_connections * 2-3)
    # Asumiendo 200 conexiones máximas
    work_mem_mb = int((memory_gb * 1024) / (200 * 3))

    # Maintenance work mem: 5-10% de RAM
    maintenance_work_mem_mb = int(memory_gb * 1024 * 0.05)

    # Workers paralelos
    max_worker_processes = min(cores, 8)
    max_parallel_workers = min(cores, 8)
    max_parallel_workers_per_gather = min(int(cores / 2), 4)

    return {
        "shared_buffers": f"{shared_buffers_gb}GB",
        "effective_cache_size": f"{effective_cache_gb}GB",
        "work_mem": f"{work_mem_mb}MB",
        "maintenance_work_mem": f"{maintenance_work_mem_mb}MB",
        "max_worker_processes": max_worker_processes,
        "max_parallel_workers": max_parallel_workers,
        "max_parallel_workers_per_gather": max_parallel_workers_per_gather,
        "max_connections": 200,
    }


def calculate_redis_config(memory_gb):
    """Calcula configuración óptima para Redis"""
    # Redis debería usar 10-15% de RAM total
    redis_memory_gb = max(int(memory_gb * 0.12), 1)

    return {
        "maxmemory": f"{redis_memory_gb}gb",
        "maxmemory_policy": "allkeys-lru",
    }


def calculate_docker_limits(memory_gb, cores):
    """Calcula límites de recursos para Docker"""
    # PostgreSQL: 20-30% de recursos
    postgres_memory = int(memory_gb * 0.25)
    postgres_cpus = max(int(cores * 0.25), 2)

    # Redis: 10-15% de recursos
    redis_memory = int(memory_gb * 0.12)
    redis_cpus = max(int(cores * 0.15), 1)

    # App: 50-60% de recursos (el resto)
    app_memory = int(memory_gb * 0.5)
    app_cpus = max(int(cores * 0.5), 4)

    # Frontend: 10-15% de recursos
    frontend_memory = int(memory_gb * 0.13)
    frontend_cpus = max(int(cores * 0.1), 2)

    return {
        "postgres": {"cpus": postgres_cpus, "memory": f"{postgres_memory}G"},
        "redis": {"cpus": redis_cpus, "memory": f"{redis_memory}G"},
        "app": {"cpus": app_cpus, "memory": f"{app_memory}G"},
        "frontend": {"cpus": frontend_cpus, "memory": f"{frontend_memory}G"},
    }


def print_report():
    """Genera el reporte completo"""
    print("=" * 70)
    print("🔍 DETECTOR DE RECURSOS DEL SISTEMA")
    print("=" * 70)
    print()

    # Información del sistema
    print(f"💻 Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"🖥️  Arquitectura: {platform.machine()}")
    print()

    # CPUs
    physical_cores, logical_cores = get_cpu_count()
    print(f"⚙️  CPUs Físicos: {physical_cores}")
    print(f"⚙️  CPUs Lógicos: {logical_cores} (con hyperthreading)")
    print()

    # Memoria
    memory_gb = get_memory_info()
    print(f"💾 RAM Total: {memory_gb:.2f} GB")
    print()

    print("=" * 70)
    print("📊 CONFIGURACIÓN RECOMENDADA")
    print("=" * 70)
    print()

    # Gunicorn workers
    workers_io = calculate_workers(physical_cores, "io_bound")
    workers_cpu = calculate_workers(physical_cores, "cpu_bound")
    workers_balanced = calculate_workers(physical_cores, "balanced")
    threads = calculate_threads(workers_balanced, memory_gb)

    print("🔧 GUNICORN (Backend App)")
    print(f"   Workers (I/O intensivo):      {workers_io}")
    print(f"   Workers (CPU intensivo):      {workers_cpu}")
    print(f"   Workers (Balanceado) ⭐:       {workers_balanced} ← Recomendado")
    print(f"   Threads por worker:           {threads}")
    print(f"   Conexiones simultáneas:       ~{workers_balanced * threads}")
    print()

    # PostgreSQL
    print("🐘 POSTGRESQL")
    postgres_config = calculate_postgres_config(memory_gb, physical_cores)
    for key, value in postgres_config.items():
        print(f"   {key:30} = {value}")
    print()

    # Redis
    print("🔴 REDIS")
    redis_config = calculate_redis_config(memory_gb)
    for key, value in redis_config.items():
        print(f"   {key:30} = {value}")
    print()

    # Docker limits
    print("🐳 LÍMITES DOCKER")
    docker_limits = calculate_docker_limits(memory_gb, physical_cores)
    for service, limits in docker_limits.items():
        print(f"   {service:15} CPUs: {limits['cpus']:2}   Memory: {limits['memory']}")
    print()

    print("=" * 70)
    print("📝 VARIABLES DE ENTORNO PARA docker-compose.yml")
    print("=" * 70)
    print()
    print(f"APP_WORKERS={workers_balanced}")
    print(f"APP_THREADS={threads}")
    print(f"APP_TIMEOUT=1800")
    print(f"WEB_CONCURRENCY={workers_balanced}")
    print()

    print("=" * 70)
    print("💡 RECOMENDACIONES")
    print("=" * 70)
    print()

    if memory_gb < 8:
        print("⚠️  Memoria baja detectada. Considera:")
        print("   - Reducir workers a", workers_balanced // 2)
        print("   - Usar 2 threads por worker")
        print("   - Limitar PostgreSQL shared_buffers a 1GB")
    elif memory_gb >= 32:
        print("✅ Excelente cantidad de RAM disponible")
        print("   - Puedes aumentar workers si tienes muchos usuarios concurrentes")
        print("   - Considera usar workers =", workers_io, "para cargas I/O intensivas")

    if physical_cores <= 2:
        print("⚠️  CPUs limitados detectados. Considera:")
        print("   - Reducir workers a", (physical_cores * 2) + 1)
        print("   - Priorizar threads sobre workers")
    elif physical_cores >= 8:
        print("✅ Excelente cantidad de CPUs")
        print("   - Configuración actual aprovechará bien el hardware")

    print()

    # Exportar a JSON
    output = {
        "system": {
            "os": platform.system(),
            "physical_cores": physical_cores,
            "logical_cores": logical_cores,
            "memory_gb": round(memory_gb, 2),
        },
        "gunicorn": {
            "workers": workers_balanced,
            "threads": threads,
            "workers_io_bound": workers_io,
            "workers_cpu_bound": workers_cpu,
        },
        "postgresql": postgres_config,
        "redis": redis_config,
        "docker_limits": docker_limits,
    }

    with open("resources_config.json", "w") as f:
        json.dump(output, f, indent=2)

    print("💾 Configuración guardada en: resources_config.json")
    print()


if __name__ == "__main__":
    try:
        print_report()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


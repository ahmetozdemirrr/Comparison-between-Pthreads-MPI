#!/usr/bin/env python3
import subprocess
import time
import csv
import matplotlib.pyplot as plt
import math

# Number of shots to try:
tosses_list = [1_000_000, 10_000_000, 50_000_000, 100_000_000, 500_000_000, 1_000_000_000] 

# number of processes to try for MPI
mpi_process_counts = [4, 8, 16, 32, 64, 128]
# Define colors and line styles for MPI processes
mpi_colors = {
    4: 'lightcoral',
    8: 'lightskyblue',
    16: 'goldenrod',
    32: 'lightseagreen',
    64: 'orchid',
    128: 'lightgray'
}
mpi_line_styles = ['-', '--', '-.', ':', (0, (3, 5, 1, 5)), (0, (1, 10))]  # Different line styles

# number of threads to tyr for Pthreads
thread_counts = [4, 8, 16, 64, 256, 1024, 4096, 16384, 65536]
thread_colors = {
    4: 'purple',
    8: 'cyan',
    16: 'green',
    64: 'red',
    256: 'blue',
    1024: 'brown',
    4096: 'orange',
    16384: 'pink',
    65536: 'yellow'
}

# number of processes to try for MPI
mpi_process_count = 4  

# out. file
output_file = "extended_performance_results.csv"

# compiling
subprocess.run(["make", "clean"])
subprocess.run(["make", "all"])


with open(output_file, mode='w', newline='') as csvfile:

    fieldnames = ["Method", "Tosses", "Threads/Processes", "Time(s)", "Estimated_PI"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # C code tests
    for tosses in tosses_list:
        start_time = time.time()
        result = subprocess.run(["make", "run-c", f"ARGS={tosses}"], capture_output=True, text=True)
        end_time = time.time()

        output = result.stdout
        pi_value = None
        for line in output.split('\n'):
            if "Estimated Pi:" in line:
                pi_value = line.split(":")[1].strip()
                break
        
        writer.writerow({
            "Method": "C",
            "Tosses": tosses,
            "Threads/Processes": 1,
            "Time(s)": end_time - start_time,
            "Estimated_PI": pi_value
        })

    # MPI tests with different process counts
    for mpi_count in mpi_process_counts:
        for tosses in tosses_list:
            start_time = time.time()
            result = subprocess.run(
                ["make", "run-mpi", f"ARGS={tosses}", f"PROCS={mpi_count}"], 
                capture_output=True, text=True
            )
            end_time = time.time()

            output = result.stdout
            pi_value = None
            for line in output.split('\n'):
                if "Estimated Pi:" in line:
                    pi_value = line.split(":")[1].strip()
                    break
            
            writer.writerow({
                "Method": "MPI",
                "Tosses": tosses,
                "Threads/Processes": mpi_count,
                "Time(s)": end_time - start_time,
                "Estimated_PI": pi_value
            })

    # Pthreads tests
    for tosses in tosses_list:
        for th in thread_counts:
            start_time = time.time()
            result = subprocess.run(["make", "run-pthreads", f"ARGS={tosses}", f"THREADS={th}"], capture_output=True, text=True)
            end_time = time.time()

            output = result.stdout
            pi_value = None
            for line in output.split('\n'):
                if "Estimated Pi:" in line:
                    pi_value = line.split(":")[1].strip()
                    break
            
            writer.writerow({
                "Method": "Pthreads",
                "Tosses": tosses,
                "Threads/Processes": th,
                "Time(s)": end_time - start_time,
                "Estimated_PI": pi_value
            })

print(f"Results have been written to {output_file}.")

# drawing grafics
tosses_data = []
c_times = []
mpi_times = []
pthreads_times = {th: [] for th in thread_counts}

# Read the CSV and prepare the values for the chart
with open(output_file, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

# Collect all unique tosses values (ordered)
unique_tosses = sorted(list(set(int(row['Tosses']) for row in data)))

# Get C data
for t in unique_tosses:
    row = next((r for r in data if r['Method']=='C' and int(r['Tosses'])==t), None)
    if row:
        c_times.append(float(row['Time(s)']))
    else:
        c_times.append(None)

# Get MPI data
for t in unique_tosses:
    row = next((r for r in data if r['Method']=='MPI' and int(r['Tosses'])==t), None)
    if row:
        mpi_times.append(float(row['Time(s)']))
    else:
        mpi_times.append(None)

# Get Pthreads data
for th in thread_counts:
    for t in unique_tosses:
        row = next((r for r in data if r['Method']=='Pthreads' and int(r['Tosses'])==t and int(r['Threads/Processes'])==th), None)
        if row:
            pthreads_times[th].append(float(row['Time(s)']))
        else:
            pthreads_times[th].append(None)

# Time vs throughput graph (C vs MPI vs Pthreads)
plt.figure(figsize=(10,6))
plt.plot(unique_tosses, c_times, marker='o', label='C (single-core)', color='black')

# Add all MPI process counts to the graph
for idx, mpi_count in enumerate(mpi_process_counts):
    mpi_times_current = []
    for t in unique_tosses:
        row = next((r for r in data if r['Method'] == 'MPI' and int(r['Tosses']) == t and int(r['Threads/Processes']) == mpi_count), None)
        if row:
            mpi_times_current.append(float(row['Time(s)']))
        else:
            mpi_times_current.append(None)
    color = mpi_colors.get(mpi_count, 'gray')
    line_style = mpi_line_styles[idx % len(mpi_line_styles)]
    plt.plot(unique_tosses, mpi_times_current, marker='o', linestyle=line_style, label=f'MPI ({mpi_count} procs)', color=color, alpha=0.7)

for th in thread_counts:
    color = thread_colors.get(th, 'gray')
    plt.plot(unique_tosses, pthreads_times[th], marker='o', label=f'Pthreads ({th} threads)', color=color, alpha=0.6)

# Add legend with smaller font and move it outside the plot
plt.legend(fontsize='small', loc='upper left', bbox_to_anchor=(1, 1))

plt.xlabel('Number of Tosses (log scale)')
plt.ylabel('Time (s)')
plt.title('Performance Comparison')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('performance_comparison.png', dpi=300)
plt.close()

# A separate chart for scaling only Pthreads (different thread counts)
plt.figure(figsize=(10,6))
for th in thread_counts:
    color = thread_colors.get(th, 'gray')
    plt.plot(unique_tosses, pthreads_times[th], marker='o', label=f'{th} threads', color=color, alpha=0.6)

plt.xlabel('Number of Tosses (log scale)')
plt.ylabel('Time (s)')
plt.title('Pthreads Scaling')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('pthreads_scaling.png', dpi=300)
plt.close()

print("Graphs saved as 'performance_comparison.png' and 'pthreads_scaling.png'.")

# A separate chart for scaling only MPI (different process counts)
mpi_times_per_count = {count: [] for count in mpi_process_counts}

# Get MPI data for all process counts
for mpi_count in mpi_process_counts:
    for t in unique_tosses:
        row = next((r for r in data if r['Method'] == 'MPI' and int(r['Tosses']) == t and int(r['Threads/Processes']) == mpi_count), None)
        if row:
            mpi_times_per_count[mpi_count].append(float(row['Time(s)']))
        else:
            mpi_times_per_count[mpi_count].append(None)

# Plot the MPI scaling graph
plt.figure(figsize=(10,6))
for mpi_count in mpi_process_counts:
    plt.plot(unique_tosses, mpi_times_per_count[mpi_count], marker='o', label=f'{mpi_count} processes', alpha=0.6)

plt.xlabel('Number of Tosses (log scale)')
plt.ylabel('Time (s)')
plt.title('MPI Scaling')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('mpi_scaling.png', dpi=300)
plt.close()

print("MPI Scaling graph saved as 'mpi_scaling.png'.")

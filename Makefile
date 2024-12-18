# General definitions
CC = gcc # C compiler
MPICC = mpicc
PYTHON3 = python3 # python interpreter

CFLAGS = -g -Wall

INTERNAL_CFLAGS = \
	-std=gnu99 \
	-D_GNU_SOURCE \
	-D_FILE_OFFSET_BITS=64 \
	-Iinclude \
	$(CFLAGS)

INTERNAL_LDFLAGS = $(LDFLAGS)

INTERNAL_LIBS = -lfl -lm $(LDLIBS)

# Default values
DEFAULT_ARGS = 10000  # Default number of tosses

# Targets
TARGET_C = monte_carlo_with_C/monte_carlo_c
SRC_C = monte_carlo_with_C/monte_carlo_c.c

TARGET_MPI = monte_carlo_with_MPI/monte_carlo_mpi
SRC_MPI = monte_carlo_with_MPI/monte_carlo_mpi.c

TARGET_PTHREADS = monte_carlo_with_Pthreads/monte_carlo_pthreads
SRC_PTHREADS = monte_carlo_with_Pthreads/monte_carlo_pthreads.c

PYTHON_WRAPPER = run_experiments.py  # Python wrapper file

.PHONY: all clean setup run-c run-mpi run-pthreads


# Add the setup target for installing Python dependencies
setup:
	@echo "Setting up Python environment..."
	pip install -r requirements.txt


# Compile all targets
all: c mpi pthreads


# Compile the plain C code
c: $(TARGET_C)
	@echo "C code compilation..."
$(TARGET_C): $(SRC_C)
	$(CC) $(INTERNAL_CFLAGS) -o $(TARGET_C) $(SRC_C) $(INTERNAL_LDFLAGS) $(INTERNAL_LIBS)


# Compile the MPI code
mpi: $(TARGET_MPI)
	@echo "MPI code compilation..."
$(TARGET_MPI): $(SRC_MPI)
	$(MPICC) $(INTERNAL_CFLAGS) -o $(TARGET_MPI) $(SRC_MPI) $(INTERNAL_LDFLAGS) $(INTERNAL_LIBS)


# Compile the Pthread code
pthreads: $(TARGET_PTHREADS)
	@echo "Pthreads code compilation..."

$(TARGET_PTHREADS): $(SRC_PTHREADS)
	$(CC) $(INTERNAL_CFLAGS) -pthread -o $(TARGET_PTHREADS) $(SRC_PTHREADS) $(INTERNAL_LDFLAGS) $(INTERNAL_LIBS)


# Run commands for each target
run-c:
	@echo "Running C code with ARGS=$(ARGS)"

	@if [ -z "$(ARGS)" ]; then \
		echo "No ARGS provided. Using default: $(DEFAULT_ARGS)"; \
		./$(TARGET_C) $(DEFAULT_ARGS); \
	else \
		./$(TARGET_C) $(ARGS); \
	fi


run-mpi:
	@echo "Running MPI code with ARGS=$(ARGS) and PROCS=$(PROCS)"

	@if [ -z "$(ARGS)" ]; then \
		echo "No ARGS provided. Using default: $(DEFAULT_ARGS)"; \
		mpiexec -n $(PROCS) ./$(TARGET_MPI) $(DEFAULT_ARGS); \
	else \
		mpiexec -n $(PROCS) ./$(TARGET_MPI) $(ARGS); \
	fi


run-pthreads:
	@echo "Running Pthreads code with ARGS=$(ARGS) (tosses) and possibly THREADS=$(THREADS)"

	@if [ -z "$(ARGS)" ]; then \
		echo "No ARGS provided. Using default: $(DEFAULT_ARGS) and 4 threads"; \
		./$(TARGET_PTHREADS) $(DEFAULT_ARGS) 4; \
	else \
		if [ -z "$(THREADS)" ]; then \
			echo "No THREADS provided. Using 4 threads by default"; \
			./$(TARGET_PTHREADS) $(ARGS) 4; \
		else \
			./$(TARGET_PTHREADS) $(ARGS) $(THREADS); \
		fi \
	fi


# Run the Python wrapper for experiments
experiment:
	@echo "Running experiments using Python wrapper..."
	$(PYTHON3) $(PYTHON_WRAPPER)


# Clean up generated files
clean:
	rm -f $(TARGET_C) $(TARGET_MPI) $(TARGET_PTHREADS) performance_comparison.png pthreads_scaling.png mpi_scaling.png extended_performance_results.csv


# Help command to list available targets
help:
	@echo "Available targets:"
	@echo "  setup          Install Python dependencies from requirements.txt."
	@echo "  all            Compile all targets (C, MPI, Pthreads)."
	@echo "  c              Compile the plain C implementation."
	@echo "  mpi            Compile the MPI implementation."
	@echo "  pthreads       Compile the Pthreads implementation."
	@echo "  run-c          Run the C implementation with ARGS (default: 10000)."
	@echo "  run-mpi        Run the MPI implementation with ARGS and PROCS (default: 10000, 4 processes)."
	@echo "  run-pthreads   Run the Pthreads implementation with ARGS and THREADS (default: 10000, 4 threads)."
	@echo "  experiment     Run the Python wrapper to execute experiments and generate graphs."
	@echo "  clean          Remove compiled files and generated artifacts."
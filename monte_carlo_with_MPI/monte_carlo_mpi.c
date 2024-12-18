/* monte_carlo_mpi.c */

#include <mpi.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>


int main(int argc, char * argv[])
{
	/*********** MPI ***********/
	
	int rank; /* current processor ID (main processor's ID is 0) */
	int size; /* total number of processors */
    long long number_of_tosses = 0; /* total tosses provided by the user */
    long long local_tosses = 0; /* tosses each process will handle */
    long long local_circle_count = 0; /* circle hits for each process */
    long long global_circle_count = 0; /* total circle hits across all processes */
	
	MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
	
	if (rank == 0) 
	{
        if (argc != 2) 
        {
            fprintf(stderr, "Usage: %s <number_of_tosses>\n", argv[0]);
            MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        }
        number_of_tosses = atoll(argv[1]);
    }
	/* Broadcast the number of tosses to all processes */
    MPI_Bcast(&number_of_tosses, 1, MPI_LONG_LONG, 0, MPI_COMM_WORLD);

    /* Calculate the number of tosses for each process */
    local_tosses = number_of_tosses / size;

    /* Seed the random number generator */
    srand(time(NULL) + rank);

    /* Perform local tosses and count circle hits */
    for (long long i = 0; i < local_tosses; i++) 
    {
        double x = ((double)rand() / RAND_MAX) * 2 - 1;
        double y = ((double)rand() / RAND_MAX) * 2 - 1;

        if ((x * x + y * y) <= 1.0) 
        {
            local_circle_count++;
        }
    }
    /* Reduce all local circle counts to a global count in process 0 */
    MPI_Reduce(&local_circle_count, &global_circle_count, 1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    /* Process 0 calculates and prints the estimated value of Pi */
    if (rank == 0) 
    {
        double pi_estimate = 4.0 * ((double)global_circle_count / number_of_tosses);
        printf("Estimated Pi: %.6lf\n", pi_estimate);
    }
    /* Finalize MPI environment */
    MPI_Finalize();

    return EXIT_SUCCESS;
}

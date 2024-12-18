/* monte_carlo_pthreads.c */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

/* Global variables shared among threads */
long long number_of_tosses;
long long global_circle_count = 0; 
int thread_count;

pthread_mutex_t mutex;

void * thread_work(void * rank);

int main(int argc, char * argv[]) 
{
    if (argc != 3) 
    {
        fprintf(stderr, "Usage: %s <number_of_tosses> <number_of_threads>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    number_of_tosses = atoll(argv[1]);
    thread_count = atoi(argv[2]);

    pthread_t * thread_handles = malloc(thread_count * sizeof(pthread_t));

    /* Initialize mutex */
    pthread_mutex_init(&mutex, NULL);

    /* Create threads */
    for (int i = 0; i < thread_count; i++) 
    {
        long my_rank = i;
        pthread_create(&thread_handles[i], NULL, thread_work, (void *)my_rank);
    }

    /* Join threads */
    for (int i = 0; i < thread_count; i++) 
    {
        pthread_join(thread_handles[i], NULL);
    }

    /* Compute and print pi estimate */
    double pi_estimate = 4.0 * ((double)global_circle_count / (double)number_of_tosses);
    printf("Estimated Pi: %.6lf\n", pi_estimate);

    /* Clean up */
    pthread_mutex_destroy(&mutex);
    free(thread_handles);

    return EXIT_SUCCESS;
}

void * thread_work(void * rank) 
{
    long my_rank = (long) rank;
    /* calculate the toss count for each thread */
    long long local_tosses = number_of_tosses / thread_count;

    /* random number generator seed assignment (use rank for different seed) */
    unsigned int seed = (unsigned int)(time(NULL) + my_rank);

    long long local_circle_count = 0;

    for (long long i = 0; i < local_tosses; i++) 
    {
        double x = (double)rand_r(&seed) / RAND_MAX * 2.0 - 1.0;
        double y = (double)rand_r(&seed) / RAND_MAX * 2.0 - 1.0;

        if (x*x + y*y <= 1.0) 
        {
            local_circle_count++;
        }
    }
    /* do mutex protected aggregation for global result */
    pthread_mutex_lock(&mutex);
    global_circle_count += local_circle_count;
    pthread_mutex_unlock(&mutex);

    return NULL;
}

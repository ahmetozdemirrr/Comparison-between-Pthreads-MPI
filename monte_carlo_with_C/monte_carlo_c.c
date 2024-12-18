/* monte_carlo_c.c */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>


typedef struct shots
{
    double x_axis;
    double y_axis;
}
Shots;


int main(int argc, char * argv[]) 
{   
    /* argument controls */
    if (argc != 2) 
    {
        fprintf(stderr, "Usage: %s <number_of_tosses>\n", argv[0]);
        return EXIT_FAILURE;
    }
    long long int number_of_tosses = atoll(argv[1]); /* taking shot number from ARGS (Makefile) */

    if (number_of_tosses <= 0) 
    {
        fprintf(stderr, "Error: number_of_tosses must be a positive integer.\n");
        return EXIT_FAILURE;
    }
    srand(time(NULL)); /* setting seed */

    int circle_count = 0; /* number of inside-coordinat (in circle) */

    /* for using large numbers we use dynamic mem-alloc */

    Shots * shots = (Shots *)malloc(number_of_tosses * sizeof(Shots)); 
    
    if (shots == NULL) 
    {
        fprintf(stderr, "Memory allocation failed for shots array.\n");
        return EXIT_FAILURE;
    }
    
    int * circle_mark = (int *)malloc(number_of_tosses * sizeof(int));

    if (circle_mark == NULL) 
    {
        fprintf(stderr, "Memory allocation failed for circle_mark array.\n");
        free(shots);
        return EXIT_FAILURE;
    }

    for (int i = 0; i < number_of_tosses; ++i)
    {
        circle_mark[i] = 0;
    }

    for (int i = 0; i < number_of_tosses; ++i)
    {
        shots[i].x_axis = ((double)rand() / RAND_MAX) * 2 - 1;
        shots[i].y_axis = ((double)rand() / RAND_MAX) * 2 - 1;

        /* checking if it's in the circle equation */
        if (((shots[i].x_axis * shots[i].x_axis) + (shots[i].y_axis * shots[i].y_axis)) <= 1.0)
        {
            circle_mark[i] = 1;
            circle_count++;
        }
        /* 
            DEBUG:
            printf("Shot %d: (x: %.2lf, y: %.2lf) -> %s\n", 
                i + 1, 
                shots[i].x_axis, 
                shots[i].y_axis, 
                circle_mark[i] == 1 ? "Inside" : "Outside");
        */
    }

    /* Calculate Pi */
    double pi_estimate = 4.0 * ((double)circle_count / number_of_tosses);
    printf("\nEstimated Pi: %.6lf\n", pi_estimate);

    free(shots);
    free(circle_mark);
    
    return EXIT_SUCCESS;
}

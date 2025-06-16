#include <stdio.h>

struct Point
{
    int x;
    int y;
};

int sum_array(int *arr, int n)
{
    int sum = 0;
    for (int i = 0; i < n; i++)
        sum = sum + arr[i];
    return sum;
}

int factorial(int n)
{
    if (n <= 1)
        return 1;
    return n * factorial(n - 1);
}

void print_point(struct Point p)
{
    printf("Point: (%d, %d)\n", p.x, p.y);
}

int main()
{
    int arr[5] = {1, 2, 3, 4, 5};
    struct Point p = {10, 20};
    int fact = factorial(5);
    int total = sum_array(arr, 5);

    printf("Factorial(5): %d\n", fact);
    printf("Sum of array: %d\n", total);
    print_point(p);

    return 0;
}
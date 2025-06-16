#include <stdio.h>

#define MAX_SIZE 100
#define SQUARE(x) ((x) * (x))

// Function to calculate factorial
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Function to find the sum of squares from 1 to n
int sum_of_squares(int n) {
    int sum = 0;
    for (int i = 1; i <= n; i++) {
        sum += SQUARE(i);
    }
    return sum;
}

int main() {
    int n = 5;
    int fact = factorial(n);
    int sum = sum_of_squares(n);
    
    printf("Factorial of %d is: %d\n", n, fact);
    printf("Sum of squares from 1 to %d is: %d\n", n, sum);
    
    return 0;
} 
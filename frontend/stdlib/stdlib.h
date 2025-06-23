// Standard library functions - simplified for parser compatibility
int malloc(unsigned long size);
void free(int ptr);
int calloc(unsigned long num, unsigned long size);
int realloc(int ptr, unsigned long size);

// Program termination
void exit(int status);
void abort(void);

// String conversion
int atoi(char *str);
long atol(char *str);
double atof(char *str);

// Random numbers
int rand(void);
void srand(unsigned int seed);

// Environment
char *getenv(char *name);

// Constants
#define NULL 0
#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1

// Standard I/O functions
int printf(const char* format, ...);
int scanf(const char* format, ...);
int puts(const char* str);
int getchar(void);
int putchar(int c);

// File operations
typedef void* FILE;
FILE* fopen(const char* filename, const char* mode);
int fclose(FILE* stream);
int fprintf(FILE* stream, const char* format, ...);
int fscanf(FILE* stream, const char* format, ...);
int fgetc(FILE* stream);
int fputc(int c, FILE* stream);

// Standard streams
extern FILE* stdin;
extern FILE* stdout;
extern FILE* stderr; 
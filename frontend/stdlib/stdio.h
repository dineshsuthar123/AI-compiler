// Standard I/O functions - simplified for parser compatibility
int printf(char *format);
int scanf(char *format);
int puts(char *str);
int getchar(void);
int putchar(int c);

// Simplified file operations
int fopen(char *filename, char *mode);
int fclose(int stream);
int fprintf(int stream, char *format);
int fscanf(int stream, char *format);
int fgetc(int stream);
int fputc(int c, int stream);
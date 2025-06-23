// String manipulation functions - simplified for parser compatibility
unsigned long strlen(char *str);
char *strcpy(char *dest, char *src);
char *strncpy(char *dest, char *src, unsigned long n);
char *strcat(char *dest, char *src);
char *strncat(char *dest, char *src, unsigned long n);
int strcmp(char *str1, char *str2);
int strncmp(char *str1, char *str2, unsigned long n);
char *strchr(char *str, int c);
char *strrchr(char *str, int c);
char *strstr(char *haystack, char *needle);

// Memory functions
int memcpy(int dest, int src, unsigned long n);
int memmove(int dest, int src, unsigned long n);
int memcmp(int ptr1, int ptr2, unsigned long n);
int memset(int ptr, int value, unsigned long n);
int memchr(int ptr, int value, unsigned long n);

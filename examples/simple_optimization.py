from ai_compiler import Compiler

def main():
    # Sample C code to optimize
    source_code = """
    #include <stdio.h>
    
    int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }
    
    int main() {
        int n = 10;
        printf("Fibonacci(%d) = %d\n", n, fibonacci(n));
        return 0;
    }
    """
    
    # Initialize compiler
    compiler = Compiler()
    
    try:
        # Compile and optimize the code
        output_file = compiler.compile(
            source_code,
            output_file="optimized_fibonacci"
        )
        print(f"Successfully compiled to: {output_file}")
        
    except Exception as e:
        print(f"Compilation failed: {str(e)}")

if __name__ == "__main__":
    main() 
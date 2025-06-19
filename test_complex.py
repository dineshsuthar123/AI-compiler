#!/usr/bin/env python3

from simple_compiler import ModernCompiler

def test_original_complex_code():
    """Test the original complex C code that was failing."""
    compiler = ModernCompiler()
    
    original_code = '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_POINTS 100

struct Point {
    double x, y;
};

typedef struct {
    struct Point* points;
    int size;
} Polygon;

double distance(struct Point a, struct Point b) {
    return sqrt((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y));
}

double perimeter(Polygon* poly) {
    double peri = 0.0;
    for (int i = 0; i < poly->size; i++) {
        struct Point a = poly->points[i];
        struct Point b = poly->points[(i + 1) % poly->size];
        peri += distance(a, b);
    }
    return peri;
}

void apply(struct Point* p, void (*func)(struct Point*)) {
    func(p);
}

void scale(struct Point* p) {
    p->x *= 2;
    p->y *= 2;
}

int save_polygon(const char* filename, Polygon* poly) {
    FILE* file = fopen(filename, "w");
    if (!file) return -1;
    for (int i = 0; i < poly->size; i++) {
        fprintf(file, "%lf %lf\\n", poly->points[i].x, poly->points[i].y);
    }
    fclose(file);
    return 0;
}

int main() {
    Polygon poly;
    poly.size = 4;
    poly.points = (struct Point*)malloc(poly.size * sizeof(struct Point));

    poly.points[0] = (struct Point){0, 0};
    poly.points[1] = (struct Point){0, 3};
    poly.points[2] = (struct Point){4, 3};
    poly.points[3] = (struct Point){4, 0};

    printf("Perimeter before scaling: %.2f\\n", perimeter(&poly));

    for (int i = 0; i < poly.size; i++) {
        apply(&poly.points[i], scale);
    }

    printf("Perimeter after scaling: %.2f\\n", perimeter(&poly));

    save_polygon("polygon.txt", &poly);

    free(poly.points);
    return 0;
}'''
    
    print("Testing Original Complex C Code")
    print("="*60)
    print("This code uses:")
    print("  - Struct definitions")
    print("  - Typedef declarations")  
    print("  - Function pointers")
    print("  - Dynamic memory allocation (malloc/free)")
    print("  - File I/O (fopen, fprintf, fclose)")
    print("  - Math functions (sqrt)")
    print("  - Complex expressions and member access")
    print("  - Floating-point arithmetic")
    print("="*60)
    
    try:
        result = compiler.compile_and_execute(original_code)
        if result['success']:
            print(f"✅ SUCCESS!")
            print(f"Output: {result['output']}")
        else:
            print(f"❌ FAILED")
            print(f"Error: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False
    
    return True

def test_simplified_struct():
    """Test a simplified version with structs."""
    compiler = ModernCompiler()
    
    simple_struct_code = '''#include <stdio.h>

struct Point {
    double x, y;
};

int main() {
    struct Point p;
    p.x = 3.0;
    p.y = 4.0;
    printf("Point: (%.1f, %.1f)\\n", p.x, p.y);
    return 0;
}'''
    
    print("\nTesting Simplified Struct Code")
    print("="*40)
    print("This tests basic struct support")
    print("="*40)
    
    try:
        result = compiler.compile_and_execute(simple_struct_code)
        if result['success']:
            print(f"✅ SUCCESS!")
            print(f"Output: {result['output']}")
        else:
            print(f"❌ FAILED")
            print(f"Error: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Complex C Code Support")
    print("="*70)
    
    # Test simplified struct first
    struct_success = test_simplified_struct()
    
    # Test original complex code
    complex_success = test_original_complex_code()
    
    print("\n" + "="*70)
    print(f"Results:")
    print(f"  Simplified struct: {'✅ PASS' if struct_success else '❌ FAIL'}")
    print(f"  Complex code: {'✅ PASS' if complex_success else '❌ FAIL'}")
    
    if complex_success:
        print("\n🎉 CONGRATULATIONS! Your AI compiler can now handle complex C code!")
    else:
        print(f"\n📝 Progress made! The compiler handles many features but needs struct/typedef support.")

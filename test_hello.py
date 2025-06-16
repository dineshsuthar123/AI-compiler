from frontend.parser.c_parser import CParser
from ir.ir_generator import IRGenerator
import llvmlite.binding as llvm

def main():
    # Read C source code
    with open('examples/hello.c', 'r') as f:
        source_code = f.read()
    
    # Parse C code to AST
    parser = CParser()
    ast = parser.parse(source_code)
    
    # Generate IR from AST
    ir_generator = IRGenerator()
    ir_generator.visit(ast)
    
    # Initialize LLVM
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    
    # Create a target machine
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    
    # Compile the module
    llvm_ir = str(ir_generator.module)
    mod = llvm.parse_assembly(llvm_ir)
    mod.triple = llvm.get_default_triple()
    mod.data_layout = str(target_machine.target_data)
    mod.verify()
    
    # Generate object code
    import ctypes
    with llvm.create_mcjit_compiler(mod, target_machine) as engine:
        # Get the main function address
        main_addr = engine.get_function_address("main")
        # Convert to a callable C function
        main_func = ctypes.CFUNCTYPE(ctypes.c_int)(main_addr)
        # Execute the function
        main_func()

if __name__ == '__main__':
    main()
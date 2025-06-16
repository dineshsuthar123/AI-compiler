from llvmlite import ir
from llvmlite import binding as llvm
import ctypes

class IRExecutor:
    """Executes LLVM IR code and returns the result."""
    
    def __init__(self):
        """Initialize the LLVM execution engine."""
        # Initialize LLVM
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        
        # Create execution engine
        self.target = llvm.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine()
        self.engine = llvm.create_mcjit_compiler(llvm.parse_assembly(""), self.target_machine)
        
        # Set the data layout
        self.data_layout = self.target_machine.target_data
        llvm.set_option("", "--data-layout=" + str(self.data_layout))
    
    def execute(self, ir_code: str) -> int:
        """Execute LLVM IR code and return the result.
        
        Args:
            ir_code: LLVM IR code to execute
            
        Returns:
            The return value of the main function
        """
        mod = None
        try:
            # Parse the IR code
            mod = llvm.parse_assembly(ir_code)
            mod.verify()
            
            # Set the data layout
            mod.data_layout = str(self.data_layout)
            
            # Add the module to the engine
            self.engine.add_module(mod)
            self.engine.finalize_object()
            
            # Get the main function
            main_func = self.engine.get_function_address("main")
            main_func = ctypes.CFUNCTYPE(ctypes.c_int)(main_func)
            
            # Execute the main function
            result = main_func()
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to execute LLVM IR: {str(e)}")
        finally:
            if mod is not None:
                self.engine.remove_module(mod)
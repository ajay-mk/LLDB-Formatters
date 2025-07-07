import lldb

def dereferenced_type(type_ref: lldb.SBType) -> lldb.SBType:
    """Helper function to get the dereferenced type if it's a reference."""
    if type_ref.IsReferenceType():
        return type_ref.GetDereferencedType()
    return type_ref

class EigenMatrixProvider:
    """LLDB formatter for Eigen::Matrix objects."""
    
    def __init__(self, valobj: lldb.SBValue, dict):
        self.valobj = valobj
        self.rows = 0
        self.cols = 0
        self.data_ptr = None
        self.scalar_type = None
        self.update()

    def num_children(self) -> int:
        """Return the total number of elements in the matrix."""
        return self.rows * self.cols

    def has_children(self) -> bool:
        """Return True if the matrix has elements."""
        return self.num_children() > 0

    def get_child_index(self, name):
        """Not used for array-like display."""
        return None

    def get_child_at_index(self, index):
        """Return the matrix element at the given linear index."""
        if not self.data_ptr or not self.data_ptr.IsValid() or index >= self.num_children():
            return None
            
        try:
            # Calculate row and column from linear index
            # Eigen uses column-major storage by default
            row = index % self.rows
            col = index // self.rows
            
            # Create child at the calculated offset
            element_size = self.scalar_type.GetByteSize()
            offset = index * element_size
            child_name = f'[{row},{col}]'
            
            return self.data_ptr.CreateChildAtOffset(child_name, offset, self.scalar_type)
            
        except Exception:
            return None

    def update(self):
        """Called when the value might have changed. Parse the Eigen object structure."""
        try:
            # Get the scalar type from template parameters
            this_type = dereferenced_type(self.valobj.GetType())
            self.scalar_type = this_type.GetTemplateArgumentType(0)
            
            # Find the data pointer
            self.data_ptr = self._find_data_pointer()
            
            # Get dimensions
            self.rows, self.cols = self._get_dimensions()
            
        except Exception:
            self.rows = 0
            self.cols = 0
            self.data_ptr = None
            self.scalar_type = None

    def _find_data_pointer(self):
        """Find the data pointer in the Eigen object structure."""
        # Try different possible locations for the data pointer
        candidates = [
            # Modern Eigen versions
            ['m_storage', 'm_data'],
            # Alternative storage patterns
            ['storage', 'data'],
            ['m_storage', 'data'],
            # Direct data member
            ['m_data'],
            ['data'],
        ]
        
        for path in candidates:
            current = self.valobj
            for member_name in path:
                current = current.GetChildMemberWithName(member_name)
                if not current.IsValid():
                    break
            if current.IsValid():
                return current
                
        return None

    def _get_dimensions(self):
        """Get the matrix dimensions."""
        rows = 1
        cols = 1
        
        # Try to get dimensions from various possible member locations
        dimension_candidates = [
            # Common patterns in Eigen
            (['m_storage', 'm_rows'], ['m_storage', 'm_cols']),
            (['m_rows'], ['m_cols']),
            (['rows'], ['cols']),
            (['m_storage', 'rows'], ['m_storage', 'cols']),
        ]
        
        for row_path, col_path in dimension_candidates:
            # Try to get rows
            current = self.valobj
            for member_name in row_path:
                current = current.GetChildMemberWithName(member_name)
                if not current.IsValid():
                    break
            if current.IsValid():
                try:
                    rows = current.GetValueAsUnsigned()
                    if rows > 0:
                        # Now try to get cols
                        current = self.valobj
                        for member_name in col_path:
                            current = current.GetChildMemberWithName(member_name)
                            if not current.IsValid():
                                break
                        if current.IsValid():
                            cols = current.GetValueAsUnsigned()
                            if cols > 0:
                                return rows, cols
                except:
                    continue
        
        # Fallback: try to infer from type name or total size
        return self._infer_dimensions()

    def _infer_dimensions(self):
        """Fallback method to infer dimensions when direct member access fails."""
        # Try to get size information
        size_candidates = [
            ['m_storage', 'm_size'],
            ['m_size'],
            ['size'],
        ]
        
        total_size = 0
        for path in size_candidates:
            current = self.valobj
            for member_name in path:
                current = current.GetChildMemberWithName(member_name)
                if not current.IsValid():
                    break
            if current.IsValid():
                try:
                    total_size = current.GetValueAsUnsigned()
                    if total_size > 0:
                        break
                except:
                    continue
        
        if total_size > 0:
            # For vectors, assume it's either Nx1 or 1xN
            # We can check the type name to see if it's a Vector type
            type_name = str(self.valobj.GetType())
            if 'Vector' in type_name or 'vector' in type_name:
                return total_size, 1
            else:
                # For matrices, assume square if we can't determine otherwise
                import math
                side = int(math.sqrt(total_size))
                if side * side == total_size:
                    return side, side
                else:
                    # Fallback to treating as vector
                    return total_size, 1
        
        # Ultimate fallback
        return 1, 1

class EigenArrayProvider:
    """LLDB formatter for Eigen::Array objects.
    
    Arrays in Eigen have the same structure as matrices, so we can reuse
    the same implementation.
    """
    
    def __init__(self, valobj: lldb.SBValue, dict):
        # Delegate to the matrix provider since the structure is the same
        self.matrix_provider = EigenMatrixProvider(valobj, dict)
        
    def num_children(self) -> int:
        return self.matrix_provider.num_children()
        
    def has_children(self) -> bool:
        return self.matrix_provider.has_children()
        
    def get_child_index(self, name):
        return self.matrix_provider.get_child_index(name)
        
    def get_child_at_index(self, index):
        return self.matrix_provider.get_child_at_index(index)
        
    def update(self):
        self.matrix_provider.update()

def __lldb_init_module(debugger, internal_dict):
    """Register the formatters with LLDB."""
    # Register Eigen::Matrix formatter with more specific patterns
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenMatrixProvider -x "^Eigen::Matrix<.+>$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenMatrixProvider -x "^Eigen::MatrixXd$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenMatrixProvider -x "^Eigen::MatrixXf$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenMatrixProvider -x "^Eigen::MatrixXi$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenMatrixProvider -x "^Eigen::VectorXd$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenMatrixProvider -x "^Eigen::VectorXf$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenMatrixProvider -x "^Eigen::VectorXi$"')
    
    # Register Eigen::Array formatter
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenArrayProvider -x "^Eigen::Array<.+>$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenArrayProvider -x "^Eigen::ArrayXd$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenArrayProvider -x "^Eigen::ArrayXf$"')
    debugger.HandleCommand('type synthetic add -l eigen_formatter.EigenArrayProvider -x "^Eigen::ArrayXi$"')
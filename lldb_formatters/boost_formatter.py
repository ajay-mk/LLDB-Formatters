import lldb
from utils import *

# Naming conventions from a LLDB STL formatter I found online :)

class BoostSmallVectorSynthProvider:
    def __init__(self, valobj: lldb.SBValue, dict):
        self.valobj = valobj
    
    def num_children(self):
        return self.valobj.GetChildMemberWithName('m_holder').GetChildMemberWithName('m_size').GetValueAsUnsigned()
    
    def has_children(self):
        return self.num_children() > 0

    def get_child_index(self, name):
        return None

    def get_child_at_index(self, index):
        obj_type = dereferenced_type(self.valobj.GetType())
        value_type: lldb.SBType = obj_type.GetTemplateArgumentType(0)

        return self.valobj.GetChildMemberWithName('m_holder').GetChildMemberWithName('m_start').CreateChildAtOffset(
            f'[{index}]',
            index * value_type.GetByteSize(),
            value_type
        )

    def update(self):
        pass


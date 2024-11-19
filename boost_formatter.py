import lldb

def dereferenced_type(type_ref: lldb.SBType) -> lldb.SBType:
    if type_ref.IsReferenceType():
        return type_ref.GetDereferencedType()
    return type_ref

class BoostSmallVectorProvider:
    def __init__(self, valobj: lldb.SBValue, dict):
        self.valobj = valobj

    def num_children(self) -> int:
        return self.valobj.GetChildMemberWithName('m_holder').GetChildMemberWithName('m_size').GetValueAsUnsigned()

    def has_children(self) -> bool:
        return True

    def get_child_index(self, name):
        return None

    def get_child_at_index(self, index):
        this_type = dereferenced_type(self.valobj.GetType())
        value_type: lldb.SBType = this_type.GetTemplateArgumentType(0)

        return (self.valobj.GetChildMemberWithName('m_holder').GetChildMemberWithName('m_start')
            .CreateChildAtOffset(f'[{index}]', index * value_type.GetByteSize(), value_type))

    def update(self):
        pass

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('type synthetic add -l boost_formatter.BoostSmallVectorProvider -x "^boost::container::small_vector<.+>$"')
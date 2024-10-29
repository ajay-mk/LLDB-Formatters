import lldb

def dereferenced_type(obj_type: lldb.SBType) -> lldb.SBType:
    if obj_type.IsReferenceType():
        return obj_type.GetDereferencedType()
    return obj_type

def size_as_summary(valobj: lldb.SBValue) -> str:
    return 'size = ' + str(valobj.GetNumChildren())

def SizeSummaryProvider(valobj: lldb.SBValue, dict) -> str:
    return size_as_summary(valobj)
import lldb

def dereferenced_type(type_ref: lldb.SBType) -> lldb.SBType:
    if type_ref.IsReferenceType():
        return type_ref.GetDereferencedType()
    return type_ref

# See https://live.boost.org/doc/libs/1_85_0/doc/html/boost/container/small_vector.html
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

# See https://www.boost.org/doc/libs/1_86_0/doc/html/boost/container/map.html
class BoostContainerMapProvider:
    def __init__(self, valobj: lldb.SBValue, dict):
        self.valobj = valobj
        self.update()

    def num_children(self) -> int:
        return self.size

    def has_children(self) -> bool:
        return self.size > 0

    def get_child_index(self, name):
        return None

    def get_child_at_index(self, index):
        if index < 0 or index >= self.size:
            return None

        if self.node_list is None:
            self._build_node_list()

        if index < len(self.node_list):
            node_ptr = self.node_list[index]
            # The value is typically stored in the node
            # For map, value_type is std::pair<const Key, T>
            value = node_ptr.GetChildMemberWithName('m_value')
            if not value.IsValid():
                # Try alternative member names
                value = node_ptr.GetChildMemberWithName('m_data')

            return value.CreateValueFromExpression(f'[{index}]', f'*({self.value_type_str}*)0x{node_ptr.GetValueAsUnsigned():x}')

        return None

    def _build_node_list(self):
        """Build a list of all nodes in the tree by in-order traversal"""
        self.node_list = []

        # Get the tree structure
        tree = self.valobj.GetChildMemberWithName('m_data')
        if not tree.IsValid():
            tree = self.valobj.GetChildMemberWithName('m_tree')

        if tree.IsValid():
            # Get the header/root node
            header = tree.GetChildMemberWithName('m_header')
            if not header.IsValid():
                header = tree.GetChildMemberWithName('data_').GetChildMemberWithName('m_header')

            if header.IsValid():
                # Get the parent of header, which is the root of the tree
                root = header.GetChildMemberWithName('m_parent')
                if root.IsValid() and root.GetValueAsUnsigned() != 0:
                    self._traverse_tree(root)

    def _traverse_tree(self, node):
        """In-order traversal of the red-black tree"""
        if node.GetValueAsUnsigned() == 0:
            return

        # Traverse left subtree
        left = node.GetChildMemberWithName('m_left')
        if left.IsValid() and left.GetValueAsUnsigned() != 0:
            self._traverse_tree(left)

        # Add current node
        self.node_list.append(node)

        # Traverse right subtree
        right = node.GetChildMemberWithName('m_right')
        if right.IsValid() and right.GetValueAsUnsigned() != 0:
            self._traverse_tree(right)

    def update(self):
        self.size = 0
        self.node_list = None
        self.value_type_str = None

        try:
            # Get the size from the tree structure
            tree = self.valobj.GetChildMemberWithName('m_data')
            if not tree.IsValid():
                tree = self.valobj.GetChildMemberWithName('m_tree')

            if tree.IsValid():
                # Try to get node count
                node_count = tree.GetChildMemberWithName('m_node_count')
                if not node_count.IsValid():
                    # Try alternative locations
                    data = tree.GetChildMemberWithName('data_')
                    if data.IsValid():
                        node_count = data.GetChildMemberWithName('m_node_count')

                if node_count.IsValid():
                    self.size = node_count.GetValueAsUnsigned()

            # Get value type for later use
            this_type = dereferenced_type(self.valobj.GetType())
            # For map<K,V>, value_type is std::pair<const K, V>
            value_type = this_type.GetTemplateArgumentType(0)
            mapped_type = this_type.GetTemplateArgumentType(1)

            # Build the pair type string
            self.value_type_str = f'std::pair<const {value_type.GetName()}, {mapped_type.GetName()}>'
        except:
            pass


# See https://www.boost.org/doc/libs/1_86_0/doc/html/boost/unordered_map.html
class BoostUnorderedMapProvider:
    def __init__(self, valobj: lldb.SBValue, dict):
        self.valobj = valobj
        self.update()

    def num_children(self) -> int:
        return self.size

    def has_children(self) -> bool:
        return self.size > 0

    def get_child_index(self, name):
        return None

    def get_child_at_index(self, index):
        if index < 0 or index >= self.size:
            return None

        if self.node_list is None:
            self._build_node_list()

        if index < len(self.node_list):
            node_ptr = self.node_list[index]
            # Get the value from the node
            # Try common member names for the value
            value = node_ptr.GetChildMemberWithName('value_')
            if not value.IsValid():
                value = node_ptr.GetChildMemberWithName('m_value')
            if not value.IsValid():
                # The value might be stored directly in the node after the hash
                value = node_ptr

            return value.CreateValueFromExpression(f'[{index}]', f'({self.value_type_str}){{*({self.value_type_str}*)0x{value.GetLoadAddress():x}}}')

        return None

    def _build_node_list(self):
        """Build a list of all nodes by traversing the hash table buckets"""
        self.node_list = []

        # Get the table structure
        table = self.valobj.GetChildMemberWithName('table_')
        if not table.IsValid():
            table = self.valobj.GetChildMemberWithName('m_table')

        if not table.IsValid():
            return

        # Get buckets
        buckets = table.GetChildMemberWithName('buckets_')
        if not buckets.IsValid():
            buckets = table.GetChildMemberWithName('m_buckets')

        # Get bucket count
        bucket_count = table.GetChildMemberWithName('bucket_count_')
        if not bucket_count.IsValid():
            bucket_count = table.GetChildMemberWithName('m_bucket_count')

        if not buckets.IsValid() or not bucket_count.IsValid():
            return

        bucket_count_val = bucket_count.GetValueAsUnsigned()

        # Iterate through buckets and collect nodes
        for i in range(min(bucket_count_val, 10000)):  # Limit to prevent infinite loops
            bucket = buckets.GetChildAtIndex(i)
            if bucket.IsValid():
                # Get the first node in the bucket
                node = bucket.GetChildMemberWithName('next_')
                if not node.IsValid():
                    node = bucket

                # Traverse the linked list in this bucket
                visited = set()
                while node.IsValid() and node.GetValueAsUnsigned() != 0:
                    node_addr = node.GetValueAsUnsigned()
                    if node_addr in visited:
                        break
                    visited.add(node_addr)

                    self.node_list.append(node)

                    if len(self.node_list) >= self.size:
                        return

                    # Get next node in the chain
                    next_node = node.GetChildMemberWithName('next_')
                    if not next_node.IsValid():
                        break
                    node = next_node

    def update(self):
        self.size = 0
        self.node_list = None
        self.value_type_str = None

        try:
            # Get the size
            table = self.valobj.GetChildMemberWithName('table_')
            if not table.IsValid():
                table = self.valobj.GetChildMemberWithName('m_table')

            if table.IsValid():
                size_member = table.GetChildMemberWithName('size_')
                if not size_member.IsValid():
                    size_member = table.GetChildMemberWithName('m_size')

                if size_member.IsValid():
                    self.size = size_member.GetValueAsUnsigned()

            # Get value type
            this_type = dereferenced_type(self.valobj.GetType())
            key_type = this_type.GetTemplateArgumentType(0)
            mapped_type = this_type.GetTemplateArgumentType(1)

            # For unordered_map, value_type is std::pair<const Key, T>
            self.value_type_str = f'std::pair<const {key_type.GetName()}, {mapped_type.GetName()}>'
        except:
            pass


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('type synthetic add -l boost_formatter.BoostSmallVectorProvider -x "^boost::container::small_vector<.+>$"')
    debugger.HandleCommand('type synthetic add -l boost_formatter.BoostContainerMapProvider -x "^boost::container::map<.+>$"')
    debugger.HandleCommand('type synthetic add -l boost_formatter.BoostUnorderedMapProvider -x "^boost::unordered_map<.+>$"')
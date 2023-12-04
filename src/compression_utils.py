import copy
from queue import *
from typing import *
from byte_utils import *

ETB_CHAR = "\x17"

class HuffmanNode:
    # >> [MC] Provide proper docstrings for ALL methods, including helpers you write (-1)
    def __init__(self, char: str, freq: int,
                 zero_child: Optional["HuffmanNode"] = None,
                 one_child: Optional["HuffmanNode"] = None):
        self.char = char
        self.freq = freq
        self.zero_child = zero_child
        self.one_child = one_child

    def is_leaf(self) -> bool:
        return self.zero_child is None and self.one_child is None
    # Override __lt__ for tie breaking
    def __lt__(self, other):
        if self.freq == other.freq:
            return self.char < other.char
        return self.freq < other.freq

class ReusableHuffman:
    def __init__(self, corpus: str):
        self._encoding_map: dict[str, str] = dict()
        self._build_huffman_trie(corpus)

    def _build_huffman_trie(self, corpus: str):
        # >> [MC] Notice how bloated with code your constructor got? When so much is happening
        # it's hard to see the constituent pieces, debug, and interpret. This would've been the
        # perfect opportunity to decompose into helper methods that each took a part of the job:
        # (0.5 off for each that there wasn't a helper made for): (a) Finding the character distribution,
        # (b) building the Huffman Trie, (c) constructing the encoding map. (-0.5)
        # Create dict with freq, char values
        freq_dict: Dict[str, int] = dict()
        for char in corpus:
            freq_dict[char] = freq_dict.get(char, 0) + 1

        priority_queue: PriorityQueue = PriorityQueue()
        # Create a leaf node for each item and add to queue
        for char, freq in freq_dict.items():
            leaf_node = HuffmanNode(char, freq)
            priority_queue.put((freq, leaf_node))
        # Add ETB_CHAR to queue
        etb_leaf = HuffmanNode(ETB_CHAR, 1)
        priority_queue.put((1, etb_leaf))
        # Pop two smallest freq, assign zero or one bit
        # Create internal node with zero and one nodes
        # Enqueue internal node and loop until size of queue is 1
        while priority_queue.qsize() > 1:
            freq1, node1 = priority_queue.get()
            freq2, node2 = priority_queue.get()

            zero_node: Union[HuffmanNode, None]
            one_node: Union[HuffmanNode, None]

            if freq1 == freq2:
                zero_node, one_node = (node1, node2) if node1.char < node2.char else (node2, node1)
            else:
                zero_node, one_node = (node1, node2) if freq1 < freq2 else (node2, node1)

            internal_node = HuffmanNode(char='', freq=freq1 + freq2, zero_child=zero_node, one_child=one_node)
            priority_queue.put((freq1 + freq2, internal_node))
        # Make last node in queue the root node
        # Call gen encoding map to get encoding map
        root = priority_queue.get()[1]
        self._huffman_trie_root = root
        self._generate_encoding_map(root, '')

    def _generate_encoding_map(self, node: HuffmanNode, code: str):
        # Recursively generates encoding map with huff codes
        if node.is_leaf():
            self._encoding_map[node.char] = code
        else:
            if node.zero_child:
                self._generate_encoding_map(node.zero_child, code + '0')
            if node.one_child:
                self._generate_encoding_map(node.one_child, code + '1')
# >> [MC] Leave just a single newline between the end of one method and the start of the next


    def get_encoding_map(self) -> dict[str, str]:
        return copy.deepcopy(self._encoding_map)


    # Compression
    # ---------------------------------------------------------------------------

    def compress_message(self, message: str) -> bytes:
        bitstring = ''
        # Make bitstring out of all char's
        for char in message:
            bitstring += self._encoding_map[char]
        # Add padding if not dividable by 8
        bitstring += self._encoding_map[ETB_CHAR]
        if len(bitstring) % 8 != 0:
            padding_size = 8 - len(bitstring) % 8
            bitstring += '0' * padding_size
        # Make list of strings per 8 bits and convert to bytes
        bitstring_chunks = [bitstring[i:i + 8] for i in range(0, len(bitstring), 8)]
        compressed_bytes = bitstrings_to_bytes(bitstring_chunks)

        return compressed_bytes

    # Decompression
    # ---------------------------------------------------------------------------

    def decompress(self, compressed_msg: bytes) -> str:
        bit_list = []
        # Creates a list holding 8 bit strings
        for byte in compressed_msg:
            bit_list.append(byte_to_bitstring(byte))

        # Join the bit strings into a single string
        compressed_bits = ''.join(bit_list)

        # Pointer to traverse the huffman trie
        current_node = self._huffman_trie_root
        decompressed_message = ''

        for bit in compressed_bits:
            # >> [MC] Notice how your if-condition bodies are just two different assignments to
            # the same variable? Usually this means that a ternary statement would be more appropriate
            # to use here, e.g., thatVariable = true_val if (condition) else false_val
            if bit == '0':
                current_node = current_node.zero_child
            else:
                current_node = current_node.one_child

            if current_node.is_leaf():
                # Append the char to decompressed message
                if current_node.char == ETB_CHAR:
                    # Stop processing bits when ETB is encountered
                    break
                decompressed_message += current_node.char
                # Reset pointer to root for the next char
                current_node = self._huffman_trie_root

        return decompressed_message
        
# ===================================================
# >>> [MC] Summary
# 
# ---------------------------------------------------
# >>> [MC] Style Checklist
# [X] = Good, [~] = Mixed bag, [ ] = Needs improvement
# 
# [X] Variables and helper methods named and used well
# [~] Proper and consistent indentation and spacing
# [ ] Proper JavaDocs provided for ALL methods
# [X] Logic is adequately simplified
# [X] Code repetition is kept to a minimum
# ---------------------------------------------------
# Correctness:       94.0 / 100 (-1.5 / missed test)
# Mypy Penalty:         -5 (-5 if mypy wasn't clean)
# Style Penalty:      -1.5
# Total:             87.5 / 100
# ===================================================
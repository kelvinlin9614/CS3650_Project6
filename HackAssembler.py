import os
import re


class TableSymbol:
    symbol = {
        'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'R0': 0, 'R1': 1,
        'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8,
        'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14,
        'R15': 15, 'SCREEN': 0x4000, 'KBD': 0x6000
    }
    next_address = 16

    def resolve(self, symbol):
        if not (symbol in self.symbol):
            self.symbol[symbol] = self.next_address
            self.next_address += 1
        return self.symbol[symbol]

    def register_label(self, label, address):
        self.symbol[label] = address


class Translator:
    def __init__(self, file, symbol_table):
        self.file = file
        self.symbol_table = symbol_table

    def encode(self, instruction):
        if instruction[0] == '@':
            self._write(self._encode_a(instruction))
        else:
            self._write(self._encode_c(instruction))

    def _write(self, line):
        self.file.write(line + '\n')

    def _encode_destination(self, destination):
        encode = ""
        encode += '1' if 'A' in destination else '0'
        encode += '1' if 'D' in destination else '0'
        encode += '1' if 'M' in destination else '0'
        return encode

    def _encode_opcode(self, opcode):
        if 'M' in opcode:
            opcode = opcode.replace('M', 'A')
            first_bit = "1"
        else:
            first_bit = "0"
        if opcode == '0':
            return first_bit + "101010"
        elif opcode == '1':
            return first_bit + "111111"
        elif opcode == '-1':
            return first_bit + "111010"
        elif opcode == 'D':
            return first_bit + "001100"
        elif opcode == 'A':
            return first_bit + "110000"
        elif opcode == '!D':
            return first_bit + "001101"
        elif opcode == '!A':
            return first_bit + "110001"
        elif opcode == '-D':
            return first_bit + "001111"
        elif opcode == '-A':
            return first_bit + "110011"
        elif opcode == 'D+1':
            return first_bit + "011111"
        elif opcode == 'A+1':
            return first_bit + "110111"
        elif opcode == 'D-1':
            return first_bit + "001110"
        elif opcode == 'A-1':
            return first_bit + "110010"
        elif opcode == 'D+A':
            return first_bit + "000010"
        elif opcode == 'D-A':
            return first_bit + "010011"
        elif opcode == 'A-D':
            return first_bit + "000111"
        elif opcode == 'D&A':
            return first_bit + "000000"
        elif opcode == 'D|A':
            return first_bit + "010101"
        else:
            print("Unknown opcode: " + opcode)

    def _encode_jump(self, jump):
        if jump == 'JGT':
            return "001"
        elif jump == 'JEQ':
            return "010"
        elif jump == 'JGE':
            return "011"
        elif jump == 'JLT':
            return "100"
        elif jump == 'JNE':
            return "101"
        elif jump == 'JLE':
            return "110"
        elif jump == 'JMP':
            return "111"
        else:
            return "000"

    def _encode_a(self, instruction):
        address = instruction[1:]
        if not address.isdigit():
            address = self.symbol_table.resolve(address)
        return "{0:016b}".format(int(address))

    def _encode_c(self, instruction):
        if ';' in instruction:
            operation, jump = instruction.split(';')
        else:
            operation = instruction
            jump = ""
        if '=' in operation:
            destination, opcode = operation.split('=')
        else:
            destination = ""
            opcode = operation
        return "111" + self._encode_opcode(opcode) + self._encode_destination(
            destination) + self._encode_jump(jump)


class Parser:
    def __init__(self, code_writer, symbol_table):
        self.writer = code_writer
        self.symbol_table = symbol_table

    def parseFile(self, filename):
        # register labels in symbol table and keep only instructions
        instructions = []
        with open(filename) as file:
            for line in file.readlines():
                line = self._strip(line)
                if len(line):
                    if line[0] == '(':
                        self.symbol_table.register_label(line[1:-1],
                                                         len(instructions))
                    else:
                        instructions.append(line)
        # encode instructions
        for instruction in instructions:
            self.writer.encode(instruction)

    def _strip(self, line):
        line = re.sub('//.*', '', line)
        line = re.sub(r'\s', '', line)
        return line


def write_to_file(fname):
    hack_filename = os.path.splitext(fname)[0] + ".hack"
    with open(hack_filename, "w") as asm_file:
        symbol_table = TableSymbol()
        writer = Translator(asm_file, symbol_table)
        parser = Parser(writer, symbol_table)
        parser.parseFile(fname)


def main():
    filename = input("Enter asm file name: ")
    filename_last_four_str = filename[-4:]
    if filename_last_four_str == ".asm":
        write_to_file(filename)
    else:
        print("invalid!")
        print("Usage: <filename>.asm")


main()
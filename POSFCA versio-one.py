#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
from pathlib import Path

class POSFCACompiler:
    def __init__(self):
        self.output_dir = Path.cwd()
    
    def compile(self, kernel_py):
        with open(kernel_py, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        asm = [
            "BITS 16",
            "ORG 0x7C00",
            "",
            "start:",
            "    xor ax, ax",
            "    mov ds, ax",
            "    mov es, ax",
            "    mov ss, ax",
            "    mov sp, 0x7C00",
            "",
            "    mov ax, 0x0003",
            "    int 0x10",
            "",
            "    ; Вывод строк",
        ]
        
        strings = []
        counter = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('print('):
                match = re.search(r'print\("([^"]*)"\)', line)
                if match:
                    text = match.group(1)
                    label = f'msg_{counter}'
                    counter += 1
                    strings.append((label, text))
                    asm.append(f'    mov si, {label}')
                    asm.append('    call print_string')
                    asm.append('    call newline')  # Добавляем перевод строки!
        
        asm.append("")
        for label, text in strings:
            asm.append(f'{label}: db "{text}", 0')
        
        asm.extend([
            "",
            "newline:",
            "    pusha",
            "    mov ah, 0x0E",
            "    mov al, 13",    # Возврат каретки
            "    int 0x10",
            "    mov al, 10",    # Перевод строки
            "    int 0x10",
            "    popa",
            "    ret",
            "",
            "print_string:",
            "    pusha",
            ".loop:",
            "    lodsb",
            "    or al, al",
            "    jz .done",
            "    mov ah, 0x0E",
            "    int 0x10",
            "    jmp .loop",
            ".done:",
            "    popa",
            "    ret",
            "",
            "halt:",
            "    hlt",
            "    jmp halt",
            "",
            "times 510-($-$$) db 0",
            "dw 0xAA55"
        ])
        
        with open('kernel.asm', 'w') as f:
            f.write('\n'.join(asm))
        
        result = subprocess.run(
            ['nasm', '-f', 'bin', 'kernel.asm', '-o', 'posfca.bin'],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print("❌ Ошибка:", result.stderr)
            return
        
        print("✅ Компиляция успешна!")
        size = Path('posfca.bin').stat().st_size
        print(f"📊 Размер: {size} байт")
        print("\n🚀 Запуск: qemu-system-i386 -fda posfca.bin -m 64 -vga std")

# Создаём тестовое ядро
with open('kernel.py', 'w') as f:
    f.write('''
print("========================================")
print("  POSFCA Kernel v2.0")
print("  English Version")
print("========================================")
print("")
print("Hello World from POSFCA!")
print("System initialized successfully!")
print("All systems operational.")
print("")
print("Kernel is running smoothly.")
print("This is a production build.")
print("========================================")

while 1:
    pass
''')

if __name__ == '__main__':
    compiler = POSFCACompiler()
    compiler.compile('kernel.py')
EOF

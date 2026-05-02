# Working DSL Script Example
# This script demonstrates working DSL capabilities

# Set up variables
project_name = "SUMD Project"
working_dir = cwd()

# Basic arithmetic
result = 1 + 2 * 3
print("Arithmetic result:")
print(result)

# String operations
text = "hello world"
text_len = len(text)
print("Text length:")
print(text_len)

# File operations
if exists("SUMD.md"):
    print("SUMD.md exists")
    content = read_file("SUMD.md")
    lines = len(content.splitlines())
    print("SUMD.md lines:")
    print(lines)
else:
    print("SUMD.md does not exist")

# List Python files
python_files = list_files("*.py")
print("Python files found:")
print(len(python_files))

# Type conversion
number = 42
number_str = str(number)
print("Number as string:")
print(number_str)

print("DSL script completed successfully!")

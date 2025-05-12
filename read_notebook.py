import json

def read_notebook(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"Successfully opened {filename}")
            notebook = json.load(f)
            print(f"Successfully parsed notebook JSON")
            
            print("\nNotebook Contents:")
            print("==================")
            
            for i, cell in enumerate(notebook['cells']):
                print(f"\nCell {i+1}:")
                print("---------")
                if cell['cell_type'] == 'code':
                    print("Code Cell:")
                    try:
                        source = ''.join(cell['source'])
                        print(source)
                    except Exception as e:
                        print(f"Error reading code: {str(e)}")
                elif cell['cell_type'] == 'markdown':
                    print("Markdown Cell:")
                    try:
                        source = ''.join(cell['source'])
                        print(source)
                    except Exception as e:
                        print(f"Error reading markdown: {str(e)}")
                print("-" * 80)
    except FileNotFoundError:
        print(f"Could not find file: {filename}")
    except json.JSONDecodeError as e:
        print(f"Error parsing notebook JSON: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    read_notebook('Model_d.ipynb') 
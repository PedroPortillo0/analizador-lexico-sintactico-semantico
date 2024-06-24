from flask import Flask, request, render_template_string
import re
import ply.lex as lex

app = Flask(__name__)

# Definición de tokens para el analizador léxico
tokens = [
    'INT', 'ID', 'NUM', 'SYM', 'ERR', 'WHILE', 'DO', 'ENDDO', 'ENDWHILE'
]

t_INT = r'\bint\b'
t_WHILE = r'\bWHILE\b'
t_DO = r'\bDO\b'
t_ENDDO = r'\bENDDO\b'
t_ENDWHILE = r'\bENDWHILE\b'
t_ID = r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'
t_NUM = r'\b\d+\b'
t_SYM = r'[;{}()\[\]=<>!+-/*]'
t_ERR = r'.'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# Plantilla HTML para mostrar resultados
html_template = '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
   <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
    body {
      font-family: 'Open Sans', sans-serif;
      background-color: #f0f8ff;
      margin: 0;
      padding: 20px;
      color: #333;
    }
    h1 {
      text-align: center;
      color: #3498db; /* Azul para confianza y claridad */
      margin-bottom: 30px;
    }
    h2 {
      text-align: center;
      color: #3498db; /* Verde para positividad y crecimiento */
      margin-bottom: 20px;
    }
    form {
      background-color: #fff;
      padding: 25px;
      border-radius: 10px;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
      max-width: 700px;
      margin: 0 auto 30px auto;
      display: flex;
      flex-direction: column;
      gap: 15px;
    }
    textarea {
      width: 100%;
      padding: 15px;
      border: 2px solid #3498db;
      border-radius: 5px;
      font-family: 'Open Sans', sans-serif;
      font-size: 16px;
    }
    input[type="submit"] {
      background-color: #3498db; 
      color: white;
      padding: 12px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      font-size: 16px;
    }
    input[type="submit"]:hover {
      background-color:#3498db;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    th, td {
      border: 1px solid #ddd;
      padding: 12px;
      text-align: left;
    }
    th {
      background-color: #3498db; /* Azul para encabezados */
      color: white;
    }
    tr:nth-child(even) {
      background-color: #f2f2f2;
    }
    tr:hover {
      background-color: #eaf2f8;
    }
    .container {
      max-width: 900px;
      margin: 0 auto;
    }
  </style>
  <title>Analizador</title>
</head>
<body>
  <div class="container">
    <h1>Analizador</h1>
    <form method="post">
      <textarea name="code" rows="10" cols="50">{{ code }}</textarea><br>
      <input type="submit" value="Analizar">
    </form>
    <div>
      <h2>Analizador Léxico</h2>
      <table>
        <tr>
          <th>Tokens</th><th>INT</th><th>ID</th><th>Números</th><th>Símbolos</th><th>WHILE</th><th>DO</th><th>ENDDO</th><th>ENDWHILE</th><th>Error</th>
        </tr>
        {% for row in lexical %}
        <tr>
          <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td><td>{{ row[5] }}</td><td>{{ row[6] }}</td><td>{{ row[7] }}</td><td>{{ row[8] }}</td><td>{{ row[9] }}</td>
        </tr>
        {% endfor %}
        <tr>
          <td>Total</td><td>{{ total['INT'] }}</td><td>{{ total['ID'] }}</td><td>{{ total['NUM'] }}</td><td>{{ total['SYM'] }}</td><td>{{ total['WHILE'] }}</td><td>{{ total['DO'] }}</td><td>{{ total['ENDDO'] }}</td><td>{{ total['ENDWHILE'] }}</td><td>{{ total['ERR'] }}</td>
        </tr>
      </table>
    </div>
    <div>
      <h2>Analizador Sintáctico y Semántico</h2>
      <table>
        <tr>
          <th>Sintáctico</th><th>Semántico</th>
        </tr>
        <tr>
          <td>{{ syntactic }}</td><td>{{ semantic }}</td>
        </tr>
      </table>
    </div>
  </div>
</body>
</html>
'''

def analyze_lexical(code):
    lexer.input(code)
    results = {'INT': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'WHILE': 0, 'DO': 0, 'ENDDO': 0, 'ENDWHILE': 0, 'ERR': 0}
    rows = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        row = [''] * 10
        if tok.type in results:
            results[tok.type] += 1
            row[list(results.keys()).index(tok.type)] = 'x'
        row[0] = tok.value
        rows.append(row)
    return rows, results

def analyze_syntactic(code):
    errors = []
    stack = []

    # Verificar la estructura de bloques y sentencias
    tokens = re.findall(r'\b(int|WHILE|DO|ENDDO|ENDWHILE)\b|.', code)
    
    for token in tokens:
        if token == 'DO':
            stack.append('DO')
        elif token == 'ENDDO':
            if not stack or stack.pop() != 'DO':
                errors.append("Falta 'DO' correspondiente a 'ENDDO'.")
        elif token == 'WHILE':
            stack.append('WHILE')
        elif token == 'ENDWHILE':
            if not stack or stack.pop() != 'WHILE':
                errors.append("Falta 'WHILE' correspondiente a 'ENDWHILE'.")
    
    if stack:
        errors.append("Bloques 'DO' o 'WHILE' sin cerrar.")

    # Verificar la estructura de las declaraciones de variables y asignaciones
    var_pattern = r'\bint\s+[a-zA-Z_][a-zA-Z_0-9]*\s*=\s*\d+;'
    assign_pattern = r'[a-zA-Z_][a-zA-Z_0-9]*\s*=\s*[^;]+;'
    if not re.findall(var_pattern, code):
        errors.append("Falta declaración de variables con 'int'.")
    if not re.findall(assign_pattern, code):
        errors.append("Falta asignación de variables.")

    # Verificar la estructura de los bucles y condiciones
    if re.search(r'WHILE\s*\(\s*int\s+\w+\s*==\s*\d+\s*\)', code):
        errors.append("Condición 'WHILE' no debe contener 'int'. Use solo la variable.")
    
    # Verificar balanceo de llaves y paréntesis
    if code.count('{') != code.count('}'):
        errors.append("Desbalanceo de llaves '{' y '}'.")
    if code.count('(') != code.count(')'):
        errors.append("Desbalanceo de paréntesis '(' y ')'.")

    if not errors:
        return "Sintaxis correcta"
    else:
        return " ".join(errors)

def analyze_semantic(code):
    errors = []
    variable_types = {}

    # Identificar y almacenar los tipos de las variables
    for var_declaration in re.findall(r'\bint\s+(\w+)\s*=\s*(\d+);', code):
        var_name, value = var_declaration
        variable_types[var_name] = 'int'

    # Verificar las asignaciones de variables
    for assign in re.findall(r'(\w+)\s*=\s*([^;]+);', code):
        var_name, expression = assign
        if var_name not in variable_types:
            errors.append(f"Variable '{var_name}' no declarada antes de la asignación.")
        else:
            # Verificar que las variables en la expresión estén declaradas
            for token in re.findall(r'\b\w+\b', expression):
                if not token.isdigit() and token not in variable_types:
                    errors.append(f"Uso de variable no declarada '{token}' en la expresión '{expression}'.")

    # Verificar condiciones lógicas
    logical_checks = re.findall(r'WHILE\s*\((.+)\)', code)
    for check in logical_checks:
        match = re.search(r'(\w+)\s*==\s*(\d+)', check)
        if match:
            var_name, value = match.groups()
            if var_name not in variable_types:
                errors.append(f"Uso de variable no declarada '{var_name}' en la condición 'WHILE'.")

    if not errors:
        return "Uso correcto de las estructuras semánticas"
    else:
        return " ".join(errors)

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_results = []
    total_results = {'INT': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'WHILE': 0, 'DO': 0, 'ENDDO': 0, 'ENDWHILE': 0, 'ERR': 0}
    syntactic_result = ''
    semantic_result = ''
    if request.method == 'POST':
        code = request.form['code']
        lexical_results, total_results = analyze_lexical(code)
        syntactic_result = analyze_syntactic(code)
        semantic_result = analyze_semantic(code)
    return render_template_string(html_template, code=code, lexical=lexical_results, total=total_results, syntactic=syntactic_result, semantic=semantic_result)

if __name__ == '__main__':
    app.run(debug=True)

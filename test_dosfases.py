import sys
import os
# Agregar el path de src/components para importar la clase
components_path = os.path.join(os.path.dirname(__file__), 'src', 'components')
if components_path not in sys.path:
    sys.path.insert(0, components_path)
from Metodo2F_NEW import SimplexDosFasesTablaCompleta

solver = SimplexDosFasesTablaCompleta()
resultado = solver.solve_from_data(
    n_vars=2,
    n_cons=2,
    c=[2, 3],
    A=[[1, 3], [2, 1]],
    b=[9, 8],
    signs=[">=", ">="],
    obj_type="min"
)
print(resultado)

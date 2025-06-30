// API para conectar con el backend Python
import { spawn } from 'child_process';
import path from 'path';

export interface ProblemaRequest {
  metodo: 'gran-m' | 'dos-fases';
  tipo: 'minimizar' | 'maximizar';
  objetivo: number[];
  restricciones: {
    coeficientes: number[];
    tipo: '<=' | '>=' | '=';
    rhs: number;
  }[];
}

export interface ResultadoResponse {
  exito: boolean;
  solucion?: {
    variables: { [key: string]: number };
    valorOptimo: number;
    iteraciones: any[];
    mensaje: string;
  };
  error?: string;
}

export async function resolverSimplex(problema: ProblemaRequest): Promise<ResultadoResponse> {
  return new Promise((resolve) => {
    try {
      // Ruta al wrapper Python
      const pythonScript = path.join(process.cwd(), 'python_wrapper.py');
      
      // Preparar los datos para Python
      const datosEntrada = {
        metodo: problema.metodo,
        tipo: problema.tipo,
        objetivo: problema.objetivo,
        restricciones: problema.restricciones
      };
      
      // Ejecutar el script Python
      const python = spawn('python', [pythonScript], {
        cwd: path.dirname(pythonScript)
      });
      
      let salida = '';
      let error = '';
      
      // Enviar datos de entrada
      python.stdin.write(JSON.stringify(datosEntrada));
      python.stdin.end();
      
      python.stdout.on('data', (data) => {
        salida += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        error += data.toString();
      });
      
      python.on('close', (code) => {
        if (code === 0) {
          try {
            // Intentar parsear la salida JSON
            const resultado = JSON.parse(salida.trim());
            resolve(resultado);
          } catch (parseError) {
            // Si no es JSON válido, enviar como texto plano
            resolve({
              exito: true,
              solucion: {
                variables: {},
                valorOptimo: 0,
                iteraciones: [],
                mensaje: salida
              }
            });
          }
        } else {
          resolve({
            exito: false,
            error: `Error en Python (código ${code}): ${error || salida}`
          });
        }
      });
      
      python.on('error', (err) => {
        resolve({
          exito: false,
          error: `Error ejecutando Python: ${err.message}`
        });
      });
      
    } catch (err) {
      resolve({
        exito: false,
        error: `Error general: ${err instanceof Error ? err.message : String(err)}`
      });
    }
  });
}

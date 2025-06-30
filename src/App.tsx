import React, { useState, useEffect } from "react";
import "./App_CLEAN.css";

// Tipos
type Restriction = {
  coefficients: number[];
  sign: "<=" | ">=" | "=";
  rhs: number;
};

type Problem = {
  method: "granm" | "dosfases";
  objType: "min" | "max";
  numVars: number;
  numRestrictions: number;
  objective: number[];
  restrictions: Restriction[];
};

const DEFAULT_PROBLEM: Problem = {
  method: "granm",
  objType: "min",
  numVars: 2,
  numRestrictions: 2,
  objective: [1, 1],
  restrictions: [
    { coefficients: [1, 1], sign: "<=", rhs: 1 },
    { coefficients: [1, 1], sign: "<=", rhs: 1 },
  ],
};

const App: React.FC = () => {
  const [tab, setTab] = useState<"setup" | "solve" | "tutorial">("setup");
  const [problem, setProblem] = useState<Problem>(DEFAULT_PROBLEM);
  const [solution, setSolution] = useState<React.ReactNode>(null);

  // Sincroniza variables y restricciones cuando cambia el número
  useEffect(() => {
    setProblem((prev) => ({
      ...prev,
      objective: Array(prev.numVars).fill(1),
      restrictions: Array(prev.numRestrictions)
        .fill(0)
        .map((_, i) =>
          prev.restrictions[i]
            ? {
                ...prev.restrictions[i],
                coefficients: Array(prev.numVars).fill(1),
              }
            : {
                coefficients: Array(prev.numVars).fill(1),
                sign: "<=",
                rhs: 1,
              }
        ),
    }));
    // eslint-disable-next-line
  }, [problem.numVars, problem.numRestrictions]);

  // Función de validación para números finitos
  const isValidNumber = (value: number): boolean => {
    return !isNaN(value) && isFinite(value);
  };

  // Handlers de cambios
  const handleObjective = (i: number, value: number) => {
    if (!isValidNumber(value)) {
      console.warn(`Valor inválido para función objetivo: ${value}`);
      return;
    }
    setProblem((p) => {
      const arr = [...p.objective];
      arr[i] = value;
      return { ...p, objective: arr };
    });
  };
  const handleRestrictionCoeff = (ri: number, vi: number, value: number) => {
    if (!isValidNumber(value)) {
      console.warn(`Valor inválido para coeficiente: ${value}`);
      return;
    }
    setProblem((p) => {
      const restr = [...p.restrictions];
      const coeffs = [...restr[ri].coefficients];
      coeffs[vi] = value;
      restr[ri] = { ...restr[ri], coefficients: coeffs };
      return { ...p, restrictions: restr };
    });
  };
  const handleRestrictionSign = (ri: number, value: "<=" | ">=" | "=") => {
    setProblem((p) => {
      const restr = [...p.restrictions];
      restr[ri] = { ...restr[ri], sign: value };
      return { ...p, restrictions: restr };
    });
  };
  const handleRestrictionRhs = (ri: number, value: number) => {
    if (!isValidNumber(value)) {
      console.warn(`Valor inválido para lado derecho de restricción: ${value}`);
      return;
    }
    setProblem((p) => {
      const restr = [...p.restrictions];
      restr[ri] = { ...restr[ri], rhs: value };
      return { ...p, restrictions: restr };
    });
  };

  // Paso a solve
  const goToSolve = () => {
    setTab("solve");
    setSolution(null);
  };

  // Simulación de solución
  const solveProblem = async () => {
    console.log("Iniciando solución...");
    setSolution(<div>Procesando...</div>);
    try {
      const payload = toBackendPayload(problem);
      console.log("Payload enviado:", payload);
      
      console.log("Enviando solicitud a:", "http://localhost:8003/solve");
      const res = await fetch("http://localhost:8003/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      console.log("Respuesta del servidor:", res.status, res.statusText);
      
      if (!res.ok) {
        const errorText = await res.text();
        console.error("Error del servidor:", errorText);
        throw new Error(`Error del servidor: ${res.status} - ${errorText}`);
      }
      
      console.log("Parseando respuesta JSON...");
      const data: BackendResponse = await res.json();
      console.log("Datos recibidos:", data);
      
      // Verificar si hay error en la respuesta
      if ('error' in data) {
        throw new Error(data.error as string);
      }
      
      setSolution(<SolutionReal data={data} problem={problem} />);
      setTimeout(() => {
        document.getElementById("solutionResults")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (e) {
      console.error("Error en solveProblem:", e);
      setSolution(
        <div style={{color:'red', padding: '20px', background: '#ffebee', borderRadius: '8px'}}>
          <h4>Error al resolver el problema:</h4>
          <p>{(e as any).message}</p>
          <p><small>Revisa la consola del navegador para más detalles</small></p>
        </div>
      );
    }
  };

  // Render
  return (
    <div className="container">
      {/* HEADER */}
      <div className="header">
        <h1>🚛 Optimizador de Transporte</h1>
        <p>Método Gran M y Dos Fases para Programación Lineal</p>
      </div>
      <div className="content">
        {/* TABS */}
        <Tabs tab={tab} setTab={setTab} />
        {/* SETUP */}
        {tab === "setup" && (
          <ConfigForm
            problem={problem}
            setProblem={setProblem}
            goToSolve={goToSolve}
            handleObjective={handleObjective}
            handleRestrictionCoeff={handleRestrictionCoeff}
            handleRestrictionSign={handleRestrictionSign}
            handleRestrictionRhs={handleRestrictionRhs}
          />
        )}
        {/* SOLVE */}
        {tab === "solve" && (
          <SolveSection
            problem={problem}
            solveProblem={solveProblem}
            setTab={setTab}
            solution={solution}
          />
        )}
        {/* TUTORIAL */}
        {tab === "tutorial" && <TutorialSection objType={problem.objType} />}
      </div>
    </div>
  );
};

// COMPONENTES INTERNOS

const Tabs: React.FC<{ tab: string; setTab: (tab: any) => void }> = ({ tab, setTab }) => (
  <div className="tabs">
    <button className={`tab-button${tab === "setup" ? " active" : ""}`} onClick={() => setTab("setup")}>
      Configuración
    </button>
    <button className={`tab-button${tab === "solve" ? " active" : ""}`} onClick={() => setTab("solve")}>
      Resolver
    </button>
    <button className={`tab-button${tab === "tutorial" ? " active" : ""}`} onClick={() => setTab("tutorial")}>
      Tutorial
    </button>
  </div>
);

type ConfigFormProps = {
  problem: Problem;
  setProblem: React.Dispatch<React.SetStateAction<Problem>>;
  goToSolve: () => void;
  handleObjective: (i: number, value: number) => void;
  handleRestrictionCoeff: (ri: number, vi: number, value: number) => void;
  handleRestrictionSign: (ri: number, value: "<=" | ">=" | "=") => void;
  handleRestrictionRhs: (ri: number, value: number) => void;
};

const ConfigForm: React.FC<ConfigFormProps> = ({
  problem,
  setProblem,
  goToSolve,
  handleObjective,
  handleRestrictionCoeff,
  handleRestrictionSign,
  handleRestrictionRhs,
}) => (
  <>
    <div className="variable-explanation">
      <h3>🎯 Contexto del Problema de Transporte</h3>
      <p><strong>Variables de decisión:</strong></p>
      <ul>
        <li><span className="highlight">x₁</span> = Cantidad de productos a transportar del Almacén 1 a la Ciudad 1</li>
        <li><span className="highlight">x₂</span> = Cantidad de productos a transportar del Almacén 1 a la Ciudad 2</li>
        <li><span className="highlight">x₃</span> = Cantidad de productos a transportar del Almacén 2 a la Ciudad 1</li>
        <li><span className="highlight">x₄</span> = Cantidad de productos a transportar del Almacén 2 a la Ciudad 2</li>
      </ul>
      <p><strong>Objetivo:</strong> {problem.objType === "min" ? "Minimizar el costo total" : "Maximizar los beneficios"} de transporte</p>
    </div>
    <div className="form-section">
      <h3>📊 Parámetros del Problema</h3>
      <div className="form-row">
        <div className="form-group">
          <label>Método de resolución:</label>
          <select
            value={problem.method}
            onChange={(e) => setProblem((p) => ({ ...p, method: e.target.value as "granm" | "dosfases" }))}
          >
            <option value="granm">Gran M</option>
            <option value="dosfases">Dos Fases</option>
          </select>
        </div>
        <div className="form-group">
          <label>Tipo de optimización:</label>
          <select
            value={problem.objType}
            onChange={(e) => setProblem((p) => ({ ...p, objType: e.target.value as "min" | "max" }))}
          >
            <option value="min">Minimizar</option>
            <option value="max">Maximizar</option>
          </select>
        </div>
        <div className="form-group">
          <label>Número de variables:</label>
          <input
            type="number"
            min={2}
            max={10}
            value={problem.numVars}
            onChange={(e) =>
              setProblem((p) => ({
                ...p,
                numVars: Number(e.target.value),
              }))
            }
          />
        </div>
        <div className="form-group">
          <label>Número de restricciones:</label>
          <input
            type="number"
            min={1}
            max={10}
            value={problem.numRestrictions}
            onChange={(e) =>
              setProblem((p) => ({
                ...p,
                numRestrictions: Number(e.target.value),
              }))
            }
          />
        </div>
      </div>
    </div>
    <div className="form-section">
      <h3>💰 Función Objetivo</h3>
      <p><strong>{problem.objType === 'min' ? 'Minimizar' : 'Maximizar'}:</strong> Z = {problem.objective.map((coef, i) => `${coef}x${i + 1}`).join(' + ')}</p>
      <div className="form-row">
        {problem.objective.map((v, i) => (
          <div className="form-group" key={i}>
            <label>{`${problem.objType === 'min' ? 'Costo' : 'Beneficio'} x${i + 1}:`}</label>
            <input
              type="number"
              value={v}
              step={0.01}
              onChange={(e) => handleObjective(i, Number(e.target.value))}
            />
          </div>
        ))}
      </div>
    </div>
    <div className="form-section">
      <h3>⚖️ Restricciones</h3>
      <div className="restrictions-container">
        {problem.restrictions.map((r, ri) => (
          <div className="restriction" key={ri}>
            <h4>{`Restricción ${ri + 1}`}</h4>
            <div className="form-row">
              {r.coefficients.map((c, vi) => (
                <div className="form-group" key={vi}>
                  <label>{`Coef. x${vi + 1}:`}</label>
                  <input
                    type="number"
                    value={c}
                    step={0.01}
                    onChange={(e) => handleRestrictionCoeff(ri, vi, Number(e.target.value))}
                  />
                </div>
              ))}
              <div className="form-group">
                <label>Signo:</label>
                <select
                  value={r.sign}
                  onChange={(e) => handleRestrictionSign(ri, e.target.value as "<=" | ">=" | "=")}
                >
                  <option value="<=">≤</option>
                  <option value=">=">≥</option>
                  <option value="=">=</option>
                </select>
              </div>
              <div className="form-group">
                <label>Valor b:</label>
                <input
                  type="number"
                  value={r.rhs}
                  step={0.01}
                  onChange={(e) => handleRestrictionRhs(ri, Number(e.target.value))}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
    <div className="button-container">
      <button className="btn btn-success" onClick={goToSolve}>
        Continuar a Resolver →
      </button>
    </div>
  </>
);

type SolveSectionProps = {
  problem: Problem;
  solveProblem: () => void;
  setTab: (tab: "setup" | "solve" | "tutorial") => void;
  solution: React.ReactNode;
};

const SolveSection: React.FC<SolveSectionProps> = ({ problem, solveProblem, setTab, solution }) => (
  <div className="form-section">
    <h3>🔍 Problema Configurado</h3>
    <div className="example-box">
      <strong>Método:</strong> {problem.method === "granm" ? "Gran M" : "Dos Fases"}
      <br />
      <strong>Tipo:</strong> {problem.objType === "min" ? "Minimizar" : "Maximizar"}
      <br />
      <br />
      <strong>Función Objetivo:</strong>
      <br />
      {problem.objType === "min" ? "Minimizar" : "Maximizar"} Z = {problem.objective.map((c, i) => (
        <span key={i}>
          {i > 0 && c >= 0 ? " + " : ""}
          {c < 0 ? " - " : ""}
          {Math.abs(c)}x{i + 1}
        </span>
      ))}
      <br />
      <br />
      <strong>Restricciones:</strong>
      <br />
      {problem.restrictions.map((r, i) => (
        <span key={i}>
          {r.coefficients.map((c, j) => (
            <span key={j}>
              {j > 0 && c >= 0 ? " + " : ""}
              {c < 0 ? " - " : ""}
              {Math.abs(c)}x{j + 1}
            </span>
          ))}{" "}
          {r.sign} {r.rhs}
          <br />
        </span>
      ))}
      <br />
      <strong>Restricciones de no negatividad:</strong> xi ≥ 0 para todo i
    </div>
    <div className="button-container">
      <button className="btn" onClick={solveProblem}>
        🚀 Resolver Problema
      </button>
      <button className="btn btn-warning" onClick={() => setTab("setup")}>
        ← Volver a Configuración
      </button>
    </div>
    {solution && (
      <div id="solutionResults" className="results-section">
        <h3>📋 Resultados de la Optimización</h3>
        <div>{solution}</div>
      </div>
    )}
  </div>
);

// Nuevo: Renderizado de solución real y fetch al backend

// Tipos para la respuesta del backend
interface BackendTable {
  headers: string[];
  rows: { base: string; values: (string | number)[] }[];
}
interface Iteracion {
  paso: number;
  tabla: BackendTable;
  base: string[];
  optima?: boolean;
  ilimitado?: boolean;
  pivote_invalido?: boolean;
}
interface BackendResponse {
  // Campos para Gran M
  penalized_obj?: { expr: string; terms: string[] };
  simplex_obj?: { expr: string; terms: string[] };
  initial_tableau?: BackendTable;
  sbfi?: { variables: Record<string, number>; z: string };
  r0_nuevo?: BackendTable;
  iteraciones?: Iteracion[];
  
  // Campos para Dos Fases
  fase1?: {
    factible: boolean;
    valor_objetivo: number;
    iteraciones: Iteracion[];
  };
  fase2?: {
    optimo?: boolean;
    ilimitado?: boolean;
    valor_objetivo: number;
    solucion: Record<string, number>;
    iteraciones: Iteracion[];
  };
  
  // Campo para errores
  error?: string;
}

// Utilidad para transformar el problema del frontend al formato del backend
function toBackendPayload(problem: Problem) {
  return {
    method: problem.method,
    n_vars: problem.numVars,
    n_cons: problem.numRestrictions,
    c: problem.objective,
    A: problem.restrictions.map((r) => r.coefficients),
    b: problem.restrictions.map((r) => r.rhs),
    signs: problem.restrictions.map((r) => r.sign),
    obj_type: problem.objType, // Usar el tipo seleccionado por el usuario
  };
}

// Nuevo: Solución real
const SolutionReal: React.FC<{ data: BackendResponse; problem: Problem }> = ({ data, problem }) => {
  console.log("Renderizando SolutionReal con data:", data);
  
  if (!data) {
    return <div style={{color:'red'}}>No hay datos para mostrar</div>;
  }

  // Si hay error, mostrarlo
  if (data.error) {
    return (
      <div style={{color:'red', padding: '20px', background: '#ffebee', borderRadius: '8px'}}>
        <h4>Error en el cálculo:</h4>
        <p>{data.error}</p>
      </div>
    );
  }

  // Renderizado para Método Dos Fases
  if (data.fase1 || data.fase2) {
    return (
      <>
        <div className="iteration-header">🔄 Método de Dos Fases</div>
        {data.fase1 && (
          <>
            <h4>FASE I: Encontrar Solución Factible</h4>
            <div className="example-box">
              <p><strong>Objetivo Fase I:</strong> Minimizar suma de variables artificiales</p>
              <p><strong>Resultado:</strong> {data.fase1.factible ? "✅ Factible" : "❌ No factible"}</p>
            </div>
            {data.fase1.iteraciones && data.fase1.iteraciones.length > 0 && (
              <>
                <h5>Iteraciones Fase I:</h5>
                {data.fase1.iteraciones.map((it, idx) => (
                  <div key={idx} style={{marginBottom: 24}}>
                    <div className="iteration-header">Iteración {idx + 1} - Fase I</div>
                    <SimplexTableBackend table={{
                      headers: it.headers,
                      rows: it.rows.map(rowArr => ({
                        base: rowArr[0],
                        values: rowArr.slice(1)
                      }))
                    }} />
                  </div>
                ))}
              </>
            )}
          </>
        )}

        {data.fase2 && (
          <>
            <h4>FASE II: Optimizar Función Objetivo Original</h4>
            <div className="example-box">
              <p><strong>Objetivo Fase II:</strong> Optimizar función objetivo original</p>
              {data.fase2.optimo && <p><strong>Resultado:</strong> ✅ Solución óptima encontrada</p>}
              {data.fase2.ilimitado && <p><strong>Resultado:</strong> ⚠️ Problema ilimitado</p>}
              <p><strong>Valor objetivo final:</strong> {data.fase2.valor_objetivo}</p>
            </div>
            {data.fase2.iteraciones && data.fase2.iteraciones.length > 0 && (
              <>
                <h5>Iteraciones Fase II:</h5>
                {data.fase2.iteraciones.map((it, idx) => (
                  <div key={idx} style={{marginBottom: 24}}>
                    <div className="iteration-header">Iteración {idx + 1} - Fase II</div>
                    <SimplexTableBackend table={{
                      headers: it.headers,
                      rows: it.rows.map(rowArr => ({
                        base: rowArr[0],
                        values: rowArr.slice(1)
                      }))
                    }} />
                  </div>
                ))}
                {data.fase2.solucion && (
                  <div className="iteration-header" style={{background: '#27ae60'}}>✅ Solución Óptima Encontrada</div>
                )}
              </>
            )}
          </>
        )}
      </>
    );
  }

  // Renderizado para Método Gran M (código original)
  return (
    <>
      <div className="iteration-header">🔄 Método de la Gran M</div>
      
      {data.penalized_obj && (
        <>
          <h4>Paso 1: Función Objetivo Penalizada</h4>
          <div className="example-box">{data.penalized_obj.expr}</div>
        </>
      )}
      
      {data.simplex_obj && (
        <>
          <h4>Paso 2: Fila 0 del Simplex</h4>
          <div className="example-box">{data.simplex_obj.expr}</div>
        </>
      )}
      
      {data.initial_tableau && (
        <>
          <h4>Paso 3: Tabla Simplex Inicial</h4>
          <SimplexTableBackend table={data.initial_tableau} />
        </>
      )}
      
      {data.sbfi && (
        <>
          <h4>Paso 4: Solución Básica Inicial</h4>
          <div className="example-box">
            {Object.entries(data.sbfi.variables).map(([k, v]) => (
              <div key={k}>{k} = {v}</div>
            ))}
            <div><strong>Z = {data.sbfi.z}</strong></div>
          </div>
        </>
      )}
      
      {data.r0_nuevo && (
        <>
          <h4>Paso 5: Renglón 0 Nuevo</h4>
          <SimplexTableBackend table={data.r0_nuevo} />
        </>
      )}
      
      {data.iteraciones && data.iteraciones.length > 0 && (
        <>
          <h4>Paso 6: Iteraciones Simplex</h4>
          {data.iteraciones.map((it, idx) => (
            <div key={idx}>
              <div className="iteration-header">Iteración {it.paso}</div>
              <SimplexTableBackend table={it.tabla} />
              {it.optima && <div className="example-box" style={{background:'#e8f5e8'}}><strong>✅ Solución óptima encontrada</strong></div>}
              {it.ilimitado && <div className="example-box" style={{background:'#ffeaea'}}><strong>⚠️ Problema ilimitado</strong></div>}
              {it.pivote_invalido && <div className="example-box" style={{background:'#ffeaea'}}><strong>⚠️ Pivote inválido</strong></div>}
            </div>
          ))}
          
          {/* Mostrar solución final si hay una iteración óptima */}
          {data.iteraciones.some(it => it.optima) && (
            <>
              <div className="iteration-header" style={{background: '#27ae60'}}>✅ Solución Óptima Encontrada</div>
              <SolucionFinalGranM iteraciones={data.iteraciones} problem={problem} />
            </>
          )}
        </>
      )}
      
      {(!data.iteraciones || data.iteraciones.length === 0) && (
        <div className="example-box" style={{background:'#fff3cd'}}>
          <strong>⚠️ No se encontraron iteraciones del simplex</strong>
        </div>
      )}
    </>
  );
};

// Renderiza una tabla simplex del backend
const SimplexTableBackend: React.FC<{ table: BackendTable }> = ({ table }) => {
  if (!table || !table.headers || !table.rows) {
    return <div style={{color:'red'}}>Datos de tabla incompletos</div>;
  }
  
  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {table.headers.map((h, i) => (
              <th key={i}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, i) => (
            <tr key={i}>
              <td><strong>{row.base}</strong></td>
              {row.values.map((v, j) => (
                <td key={j}>{v}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Componente para mostrar la solución final del método Gran M
const SolucionFinalGranM: React.FC<{ iteraciones: Iteracion[]; problem: Problem }> = ({ iteraciones, problem }) => {
  // Encontrar la última iteración óptima
  const iteracionOptima = iteraciones.find(it => it.optima);
  if (!iteracionOptima || !iteracionOptima.tabla) {
    return <div style={{color:'red'}}>No se pudo extraer la solución óptima</div>;
  }

  const tabla = iteracionOptima.tabla;
  const headers = tabla.headers;
  const rows = tabla.rows;

  // Extraer valores de las variables de decisión (x1, x2, ...)
  const variables: Record<string, number> = {};
  const variablesStr: Record<string, string> = {}; // Para mantener valores exactos como fracciones
  let valorObjetivo = 0;

  // Inicializar todas las variables de decisión en 0
  headers.forEach(header => {
    if (header.startsWith('x')) {
      variables[header] = 0;
      variablesStr[header] = '0';
    }
  });

  // Obtener valores de las variables básicas
  rows.forEach(row => {
    if (row.base.startsWith('x')) {
      const valorStr = String(row.values[row.values.length - 1]); // Última columna (b)
      variablesStr[row.base] = valorStr; // Guardar valor original
      
      // Manejar fracciones (ej: "100/3" o "50/3")
      if (valorStr.includes('/')) {
        const [numerator, denominator] = valorStr.split('/');
        const num = parseFloat(numerator);
        const den = parseFloat(denominator);
        if (!isNaN(num) && !isNaN(den) && den !== 0) {
          variables[row.base] = num / den;
        }
      } else {
        const valor = parseFloat(valorStr);
        if (!isNaN(valor)) {
          variables[row.base] = valor;
        }
      }
    }
  });

  // Obtener el valor objetivo de la fila R0*
  const filaObjetivo = rows.find(row => row.base === 'R0*');
  let valorObjetivoStr = '';
  
  if (filaObjetivo) {
    valorObjetivoStr = String(filaObjetivo.values[filaObjetivo.values.length - 1]);
    // Parsear el valor, removiendo cualquier 'M' o términos complejos
    const valorLimpio = valorObjetivoStr.replace(/[+-]?\d*\.?\d*M/g, '').trim();
    
    // Manejar fracciones (ej: "-50/3" o "50/3")
    if (valorLimpio.includes('/')) {
      const [numerator, denominator] = valorLimpio.split('/');
      const num = parseFloat(numerator);
      const den = parseFloat(denominator);
      if (!isNaN(num) && !isNaN(den) && den !== 0) {
        valorObjetivo = num / den;
      }
    } else {
      const valorNumerico = parseFloat(valorLimpio);
      if (!isNaN(valorNumerico)) {
        valorObjetivo = valorNumerico;
      }
    }
  }

  return (
    <div className="results-section">
      <h3>📋 Resultado Final</h3>
      
      <div className="example-box" style={{background: '#e8f5e8', border: '2px solid #27ae60'}}>
        <h4><strong>Variables de decisión:</strong></h4>
        {Object.entries(variables).map(([variable, valor]) => (
          <div key={variable} style={{margin: '5px 0', fontSize: '16px'}}>
            <strong>{variable} = {valor.toFixed(2)}</strong>
            {variablesStr[variable].includes('/') && (
              <span style={{fontSize: '14px', color: '#666', marginLeft: '10px'}}>
                (Exacto: {variablesStr[variable]})
              </span>
            )}
          </div>
        ))}
        
        <div style={{marginTop: '15px', padding: '10px', background: '#d4edda', borderRadius: '5px'}}>
          <strong>{problem.objType === 'min' ? 'Costo mínimo' : 'Beneficio máximo'} total: ${Math.abs(valorObjetivo).toFixed(2)}</strong>
          {valorObjetivoStr.includes('/') && (
            <div style={{fontSize: '14px', color: '#666', marginTop: '5px'}}>
              (Valor exacto: {valorObjetivoStr.replace(/[+-]?\d*\.?\d*M/g, '').trim().replace('-', '')})
            </div>
          )}
        </div>
      </div>

      <div className="example-box" style={{background: '#fff3cd'}}>
        <h4>🚛 Interpretación del Transporte:</h4>
        <p>Esta solución indica la cantidad óptima de productos a transportar por cada ruta para minimizar el costo total de transporte, respetando las capacidades de los almacenes y las demandas de las ciudades.</p>
        
        {Object.entries(variables).map(([variable, valor]) => {
          if (valor > 0) {
            const numVar = variable.replace('x', '');
            const origen = Math.ceil(parseInt(numVar) / 2);
            const destino = parseInt(numVar) % 2 === 1 ? 1 : 2;
            const valorDisplay = variablesStr[variable].includes('/') 
              ? `${valor.toFixed(2)} (${variablesStr[variable]})`
              : valor.toString();
            return (
              <div key={variable} style={{margin: '5px 0'}}>
                • <strong>{variable}:</strong> Transportar {valorDisplay} unidades del Almacén {origen} a la Ciudad {destino}
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
};

// Componente para mostrar la solución final del método Dos Fases
const SolucionFinalDosFases: React.FC<{ 
  solucion: Record<string, any>; 
  valorObjetivo: any;
  iteraciones?: Iteracion[];
  objType?: string;
}> = ({ solucion, valorObjetivo, objType = 'min' }) => {
  
  // Convertir los valores de la solución a números y strings para manejo de fracciones
  const variables: Record<string, number> = {};
  const variablesStr: Record<string, string> = {};
  
  Object.entries(solucion).forEach(([variable, valor]) => {
    const valorStr = String(valor);
    variablesStr[variable] = valorStr;
    
    // Manejar fracciones (ej: "100/3" o "50/3")
    if (valorStr.includes('/')) {
      const [numerator, denominator] = valorStr.split('/');
      const num = parseFloat(numerator);
      const den = parseFloat(denominator);
      if (!isNaN(num) && !isNaN(den) && den !== 0) {
        variables[variable] = num / den;
      }
    } else {
      const valorNumerico = parseFloat(valorStr);
      if (!isNaN(valorNumerico)) {
        variables[variable] = valorNumerico;
      }
    }
  });

  // Procesar el valor objetivo
  let valorObjetivoNumerico = 0;
  const valorObjetivoStr = String(valorObjetivo);
  
  if (valorObjetivoStr.includes('/')) {
    const [numerator, denominator] = valorObjetivoStr.split('/');
    const num = parseFloat(numerator);
    const den = parseFloat(denominator);
    if (!isNaN(num) && !isNaN(den) && den !== 0) {
      valorObjetivoNumerico = num / den;
    }
  } else {
    const valorNumerico = parseFloat(valorObjetivoStr);
    if (!isNaN(valorNumerico)) {
      valorObjetivoNumerico = valorNumerico;
    }
  }

  return (
    <div className="results-section">
      <h3>📋 Resultado Final</h3>
      
      <div className="example-box" style={{background: '#e8f5e8', border: '2px solid #27ae60'}}>
        <h4><strong>Variables de decisión:</strong></h4>
        {Object.entries(variables).map(([variable, valor]) => (
          <div key={variable} style={{margin: '5px 0', fontSize: '16px'}}>
            <strong>{variable} = {valor.toFixed(2)}</strong>
            {variablesStr[variable].includes('/') && (
              <span style={{fontSize: '14px', color: '#666', marginLeft: '10px'}}>
                (Exacto: {variablesStr[variable]})
              </span>
            )}
          </div>
        ))}
        
        <div style={{marginTop: '15px', padding: '10px', background: '#d4edda', borderRadius: '5px'}}>
          <strong>{objType === 'max' ? 'Beneficio máximo total' : 'Costo mínimo total'}: ${Math.abs(valorObjetivoNumerico).toFixed(2)}</strong>
          {valorObjetivoStr.includes('/') && (
            <div style={{fontSize: '14px', color: '#666', marginTop: '5px'}}>
              (Valor exacto: {valorObjetivoStr.replace('-', '')})
            </div>
          )}
        </div>
      </div>

      <div className="example-box" style={{background: '#fff3cd'}}>
        <h4>🚛 Interpretación del Transporte:</h4>
        <p>Esta solución indica la cantidad óptima de productos a transportar por cada ruta para {objType === 'max' ? 'maximizar el beneficio total' : 'minimizar el costo total'} de transporte, respetando las capacidades de los almacenes y las demandas de las ciudades.</p>
        
        {Object.entries(variables).map(([variable, valor]) => {
          if (valor > 0) {
            const numVar = variable.replace('x', '');
            const origen = Math.ceil(parseInt(numVar) / 2);
            const destino = parseInt(numVar) % 2 === 1 ? 1 : 2;
            const valorDisplay = variablesStr[variable].includes('/') 
              ? `${valor.toFixed(2)} (${variablesStr[variable]})`
              : valor.toString();
            return (
              <div key={variable} style={{margin: '5px 0'}}>
                • <strong>{variable}:</strong> Transportar {valorDisplay} unidades del Almacén {origen} a la Ciudad {destino}
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
};

const TutorialSection: React.FC<{objType?: string}> = ({objType = 'min'}) => (
  <div>
    <div className="tutorial-step">
      <h4>📚 Paso 1: Entender el Problema</h4>
      <p>
        El problema de transporte busca {objType === 'max' ? 'maximizar el beneficio' : 'minimizar el costo'} de enviar productos desde almacenes hasta ciudades, respetando capacidades y demandas.
      </p>
      <div className="example-box">
        <strong>Ejemplo práctico:</strong>
        <br />
        Una empresa tiene 2 almacenes y debe abastecer a 2 ciudades:
        <br />• Almacén 1: capacidad 100 unidades
        <br />• Almacén 2: capacidad 80 unidades
        <br />• Ciudad 1: demanda 70 unidades
        <br />• Ciudad 2: demanda 110 unidades
        <br />
        Costos de transporte por unidad: A1→C1: $3, A1→C2: $4, A2→C1: $2, A2→C2: $5
      </div>
    </div>
    <div className="tutorial-step">
      <h4>⚙️ Paso 2: Configurar Variables</h4>
      <p>Las variables representan la cantidad de productos a transportar por cada ruta:</p>
      <ul>
        <li>
          <strong>x₁:</strong> Del Almacén 1 a la Ciudad 1
        </li>
        <li>
          <strong>x₂:</strong> Del Almacén 1 a la Ciudad 2
        </li>
        <li>
          <strong>x₃:</strong> Del Almacén 2 a la Ciudad 1
        </li>
        <li>
          <strong>x₄:</strong> Del Almacén 2 a la Ciudad 2
        </li>
      </ul>
    </div>
    <div className="tutorial-step">
      <h4>🎯 Paso 3: Definir Función Objetivo</h4>
      <p>
        Minimizar: <span className="highlight">Z = 3x₁ + 4x₂ + 2x₃ + 5x₄</span>
      </p>
      <p>Donde cada coeficiente es el costo de transporte por unidad en esa ruta.</p>
    </div>
    <div className="tutorial-step">
      <h4>📏 Paso 4: Establecer Restricciones</h4>
      <p>
        <strong>Capacidad de almacenes:</strong>
      </p>
      <ul>
        <li>x₁ + x₂ ≤ 100 (Almacén 1)</li>
        <li>x₃ + x₄ ≤ 80 (Almacén 2)</li>
      </ul>
      <p>
        <strong>Demanda de ciudades:</strong>
      </p>
      <ul>
        <li>x₁ + x₃ ≥ 70 (Ciudad 1)</li>
        <li>x₂ + x₄ ≥ 110 (Ciudad 2)</li>
      </ul>
    </div>
    <div className="tutorial-step">
      <h4>🔧 Paso 5: Usar la Interfaz</h4>
      <ol>
        <li>Ve a la pestaña "Configuración"</li>
        <li>Selecciona el método (Gran M o Dos Fases)</li>
        <li>Define el número de variables y restricciones</li>
        <li>Ingresa los coeficientes de la función objetivo</li>
        <li>Configura cada restricción con sus coeficientes y signos</li>
        <li>Ve a "Resolver" y presiona el botón para obtener la solución</li>
      </ol>
    </div>
    <div className="tutorial-step">
      <h4>📊 Paso 6: Interpretar Resultados</h4>
      <p>La solución te mostrará:</p>
      <ul>
        <li>
          <strong>Valores óptimos:</strong> Cuánto transportar por cada ruta
        </li>
        <li>
          <strong>Costo mínimo:</strong> El costo total más bajo posible
        </li>
        <li>
          <strong>Iteraciones:</strong> Pasos del algoritmo simplex
        </li>
      </ul>
    </div>
  </div>
);

export default App;
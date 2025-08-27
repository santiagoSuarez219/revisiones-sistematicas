import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getPapers } from "./api/PaperApi/PaperApi";
import "./App.css"

import CardPaper from "./components/CardPaper/CardPaper";
import PaperInfo from './components/PaperInfo/PaperInfo';
import type { FilterStatusPapers, Paper } from "./types";

interface FilterOption {
  value: FilterStatusPapers;
  label: string;
}

function App() {
  // Estados
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [activeFilter, setActiveFilter] = useState<FilterStatusPapers>("all");

  // Query para obtener papers filtrados
  const {
    data: papersResponse,
    isError,
    isLoading,
    isFetching
  } = useQuery({
    queryKey: ["papers", activeFilter], // ✅ La key incluye el filtro
    queryFn: () => getPapers(activeFilter),
  });

  // Extraer datos de la respuesta
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const papers = papersResponse?.papers || [];
  const stats = papersResponse?.stats || {
    all: 0,
    pending: 0,
    included: 0,
    excluded: 0,
    maybe: 0
  };

  // Opciones de filtro con conteos del backend
  const filterOptions: FilterOption[] = [
    { value: "all", label: `Todos (${stats.all})` },
    { value: "pending", label: `Pending (${stats.pending})` },
    { value: "included", label: `Include (${stats.included})` },
    { value: "excluded", label: `Exclude (${stats.excluded})` },
    { value: "maybe", label: `Maybe (${stats.maybe})` },
  ];

  // Función para manejar cambio de filtro
  const handleFilterChange = (filterValue: FilterStatusPapers) => {
    setActiveFilter(filterValue);
    setSelectedPaper(null); // Limpiar selección al cambiar filtro
  };

  // Función para manejar la selección de un paper
  const handlePaperSelect = (paper: Paper) => {
    setSelectedPaper(paper);
  };

  // Auto-seleccionar primer paper cuando llegan nuevos datos
  useEffect(() => {
    if (!selectedPaper && papers.length > 0 && !isFetching) {
      setSelectedPaper(papers[0]);
    }
  }, [papers, selectedPaper, isFetching]);

  // Función para obtener estilos del botón de filtro
  const getFilterButtonStyles = (filterValue: FilterStatusPapers, isFirst: boolean, isLast: boolean) => {
    const baseStyles = "px-4 py-2 text-sm font-medium transition-all duration-200 focus:z-10 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed";
    const activeStyles = "bg-blue-600 text-white border-blue-600 hover:bg-blue-700";
    const inactiveStyles = "text-gray-900 bg-white border-gray-200 hover:bg-gray-100 hover:text-blue-700 dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:hover:text-white dark:hover:bg-gray-700";

    let positionStyles = "border-t border-b";
    if (isFirst) positionStyles = "border rounded-s-lg";
    if (isLast) positionStyles = "border rounded-e-lg";
    if (!isFirst && !isLast) positionStyles = "border-t border-b border-l";

    const isActive = activeFilter === filterValue;
    const stateStyles = isActive ? activeStyles : inactiveStyles;

    return `${baseStyles} ${positionStyles} ${stateStyles}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center gap-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <p className="text-lg text-gray-600 dark:text-gray-400">Cargando papers...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-lg text-red-600 dark:text-red-400 mb-4">Error al cargar los documentos</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <h1 className="mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white text-center">
        Papers
      </h1>

      {/* Filtros */}
      <div className="flex justify-center my-4">
        <div className="inline-flex rounded-md shadow-sm" role="group">
          {filterOptions.map((option, index) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleFilterChange(option.value)}
              disabled={isFetching}
              className={getFilterButtonStyles(
                option.value,
                index === 0,
                index === filterOptions.length - 1
              )}
            >
              {isFetching && activeFilter === option.value ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-3 w-3 border-b border-current"></div>
                  <span>{option.label}</span>
                </div>
              ) : (
                option.label
              )}
            </button>
          ))}
        </div>
      </div>



      <div className="flex h-[calc(100vh-212px)] gap-4">
        <div className="w-1/3 overflow-y-auto overflow-x-hidden flex flex-col gap-3">
          {isFetching && (
            <div className="flex items-center justify-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-sm text-blue-800 dark:text-blue-200">
                  Cargando papers...
                </span>
              </div>
            </div>
          )}

          {papers.length > 0 ? (
            papers.map((paper) => (
              <CardPaper
                key={paper._id}
                paper={paper}
                onSelect={handlePaperSelect}
                isSelected={selectedPaper?._id === paper._id}
              />
            ))
          ) : !isFetching ? (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <p className="text-lg mb-2">No hay papers</p>
                <p className="text-sm">
                  {activeFilter === "all"
                    ? "No se encontraron papers"
                    : `No hay papers con estado "${filterOptions.find(opt => opt.value === activeFilter)?.label.split(' (')[0]}"`
                  }
                </p>
                {activeFilter !== "all" && (
                  <button
                    onClick={() => handleFilterChange("all")}
                    className="mt-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 text-sm underline"
                  >
                    Ver todos los papers
                  </button>
                )}
              </div>
            </div>
          ) : null}
        </div>


        <div className="w-2/3">
          {selectedPaper ? (
            <PaperInfo paper={selectedPaper} />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
              <p>Selecciona un paper para ver los detalles</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { ToLabelPaper, updateScreeningStatus } from "../../api/PaperApi/PaperApi";
import type { Paper } from "../../types";

// Tipos para mejor type safety
type ScreeningStatus = "included" | "excluded" | "maybe" | "pending" | "to_label";

interface UpdateScreeningStatusParams {
    paperId: string;
    screeningStatus: ScreeningStatus;
}

interface ActionButton {
    label: string;
    onClick: () => void;
    disabled?: boolean;
}

export default function PaperInfo({ paper }: { paper: Paper }) {
    const queryClient = useQueryClient();

    // Mutación para etiquetar paper
    const { mutate: toLabelMutate, isPending: isLabeling } = useMutation({
        mutationFn: ToLabelPaper,
        onError: (error) => {
            console.error("Error al etiquetar paper:", error);
            // TODO: Agregar toast/notification de error
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["papers"] });
            console.log("Paper etiquetado exitosamente:", data);
            // TODO: Agregar toast/notification de éxito
        },
    });

    // Mutación para actualizar estado de screening
    const { mutate: updateScreeningStatusMutate, isPending: isUpdatingStatus } = useMutation({
        mutationFn: (params: UpdateScreeningStatusParams) => updateScreeningStatus(params),
        onError: (error) => {
            console.error("Error al actualizar estado de screening:", error);
            // TODO: Agregar toast/notification de error
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["papers"] });
            console.log("Estado actualizado exitosamente:", data);
            // TODO: Agregar toast/notification de éxito
        },
    });

    // Handlers para las acciones
    const handleToLabel = () => {
        toLabelMutate(paper._id);
    };

    const handleExclude = () => {
        updateScreeningStatusMutate({
            paperId: paper._id,
            screeningStatus: "excluded"
        });
    };

    const handleMaybe = () => {
        updateScreeningStatusMutate({
            paperId: paper._id,
            screeningStatus: "maybe"
        });
    };

    const handleInclude = () => {
        updateScreeningStatusMutate({
            paperId: paper._id,
            screeningStatus: "included"
        });
    };


    // Definición de acciones con mejor tipado
    const actions: ActionButton[] = [
        {
            label: "To Label",
            onClick: handleToLabel,
            disabled: isLabeling
        },
        {
            label: "Include",
            onClick: handleInclude,
            disabled: isUpdatingStatus
        },
        {
            label: "Maybe",
            onClick: handleMaybe,
            disabled: isUpdatingStatus
        },
        {
            label: "Exclude",
            onClick: handleExclude,
            disabled: isUpdatingStatus
        }
    ];

    return (
        <div className="w-full h-full p-6 bg-white border border-gray-200 rounded-lg shadow-sm dark:bg-gray-800 dark:border-gray-700 flex flex-col">
            {/* Header con título */}
            <div className="mb-4">
                <h2 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                    {paper.title}
                </h2>

                {/* Información adicional */}
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>
                        <strong>Fecha:</strong> {paper.publication_date}
                    </span>
                    <span className="px-2 py-1 rounded-full border ">
                        Estado: {paper.screening_status}
                    </span>

                </div>
            </div>

            {/* Labels con estado de carga mejorado */}
            <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Etiquetas:
                </h3>
                <div className="flex gap-2 flex-wrap min-h-[2rem]">
                    {isLabeling ? (
                        <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                                Etiquetando...
                            </span>
                        </div>
                    ) : paper.labels.length > 0 ? (
                        paper.labels.map((label, index) => (
                            <span
                                key={index}
                                className="inline-block whitespace-nowrap bg-blue-100 text-blue-800 text-xs font-semibold px-3 py-1 rounded-full dark:bg-blue-900 dark:text-blue-200 border border-blue-200 dark:border-blue-700"
                            >
                                {label}
                            </span>
                        ))
                    ) : (
                        <span className="text-sm text-gray-500 dark:text-gray-400 italic">
                            No hay etiquetas disponibles
                        </span>
                    )}
                </div>
            </div>

            {/* Resumen */}
            <div className="flex-1 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Resumen:
                </h3>
                <div className="max-h-80 overflow-y-auto">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                        {paper.abstract || "No hay resumen disponible."}
                    </p>
                </div>
            </div>

            {/* Botones de acción */}
            <div className="mt-auto">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                    Acciones:
                </h3>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
                    {actions.map((action) => (
                        <button
                            key={action.label}
                            type="button"
                            className="text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-100 font-medium rounded-full text-sm px-5 py-2.5 me-2 mb-2 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700"
                            onClick={action.onClick}
                            disabled={action.disabled}
                        >
                            {action.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Indicador de estado global */}
            {(isLabeling || isUpdatingStatus) && (
                <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
                    <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span className="text-sm text-blue-800 dark:text-blue-200">
                            {isLabeling ? "Etiquetando paper..." : "Actualizando estado..."}
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}
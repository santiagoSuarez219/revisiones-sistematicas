import type { Request, Response } from "express";

import PaperService from "../services/PaperService";
import Paper from "../models/Paper";

// Tipos válidos para el filtro de screening status
type ScreeningStatus = "pending" | "included" | "excluded" | "maybe";

export class PaperController {
  static getAllPapers = async (req: Request, res: Response) => {
    try {
      // Extraer parámetros de query
      const { status } = req.query;

      // Construir el filtro de MongoDB
      let filter: any = {};

      if (status && status !== "all") {
        // Validar que el status sea válido
        const validStatuses: ScreeningStatus[] = [
          "pending",
          "included",
          "excluded",
          "maybe",
        ];

        if (validStatuses.includes(status as ScreeningStatus)) {
          filter.screening_status = status;
        } else {
          return res.status(400).json({
            error:
              "Status inválido. Valores válidos: pending, included, excluded, maybe",
          });
        }
      }

      // Ejecutar consulta con filtro
      const papers = await Paper.find(filter);

      // Opcional: devolver también estadísticas de conteo
      const stats = await Paper.aggregate([
        {
          $group: {
            _id: "$screening_status",
            count: { $sum: 1 },
          },
        },
      ]);

      // Formatear estadísticas para facilitar uso en frontend
      const formattedStats = {
        all: papers.length,
        pending: 0,
        included: 0,
        excluded: 0,
        maybe: 0,
      };

      stats.forEach((stat) => {
        if (stat._id) {
          formattedStats[stat._id as ScreeningStatus] = stat.count;
        } else {
          // Papers sin screening_status se consideran pending
          formattedStats.pending += stat.count;
        }
      });

      // Calcular total
      formattedStats.all =
        Object.values(formattedStats).reduce((sum, count) => {
          return typeof count === "number" ? sum + count : sum;
        }, 0) - formattedStats.all; // Restar el valor inicial de 'all'

      res.json({
        papers,
        stats: formattedStats,
        filter: status || "all",
        total: papers.length,
      });
    } catch (error) {
      console.error("Error in getAllPapers:", error);
      res.status(500).json({ error: "Hubo un error al obtener los papers" });
    }
  };

  static getPaperById = async (req: Request, res: Response) => {
    try {
      const paper = await Paper.findById(req.params.id);
      if (!paper) {
        return res.status(404).json({ error: "Paper no encontrado" });
      }
      res.json(paper);
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: "Hubo un error" });
    }
  };

  // Nuevo endpoint para obtener solo las estadísticas
  static getPaperStats = async (req: Request, res: Response) => {
    try {
      const stats = await Paper.aggregate([
        {
          $group: {
            _id: "$screening_status",
            count: { $sum: 1 },
          },
        },
      ]);

      const formattedStats = {
        all: 0,
        pending: 0,
        included: 0,
        excluded: 0,
        maybe: 0,
      };

      stats.forEach((stat) => {
        if (stat._id) {
          formattedStats[stat._id as ScreeningStatus] = stat.count;
        } else {
          formattedStats.pending += stat.count;
        }
      });

      // Calcular total
      formattedStats.all =
        formattedStats.pending +
        formattedStats.included +
        formattedStats.excluded +
        formattedStats.maybe;

      res.json(formattedStats);
    } catch (error) {
      console.error("Error in getPaperStats:", error);
      res.status(500).json({ error: "Error al obtener estadísticas" });
    }
  };

  static toLabelPaper = async (req: Request, res: Response) => {
    try {
      const paper = await Paper.findById(req.params.id);
      if (!paper) {
        return res.status(404).json({ error: "Paper no encontrado" });
      }

      const abstract = paper.abstract;
      const labels = await PaperService.getLabelsFromSummary(abstract);

      console.log("Labels recibidas:", labels);
      console.log("Tipo de labels:", typeof labels);

      // ✅ Ahora labels ya es un array
      paper.labels = labels;
      await paper.save();

      res.status(200).json({
        message: "Etiquetas asignadas",
        labels,
      });
    } catch (error) {
      console.error("Error in toLabelPaper:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      res.status(500).json({
        error: "Error al procesar el artículo",
        details: errorMessage,
      });
    }
  };

  static updateScreeningStatus = async (req: Request, res: Response) => {
    try {
      const paper = await Paper.findById(req.params.id);
      if (!paper) {
        return res.status(404).json({ error: "Paper no encontrado" });
      }

      const { screeningStatus } = req.body;

      // Validar screening status
      const validStatuses: ScreeningStatus[] = [
        "pending",
        "included",
        "excluded",
        "maybe",
      ];
      if (!validStatuses.includes(screeningStatus)) {
        return res.status(400).json({
          error:
            "Status inválido. Valores válidos: pending, included, excluded, maybe",
        });
      }

      paper.screening_status = screeningStatus;
      await paper.save();

      res.status(200).json({
        message: "Estado de screening actualizado",
        paper: {
          _id: paper._id,
          screening_status: paper.screening_status,
          title: paper.title,
        },
      });
    } catch (error) {
      console.error("Error in updateScreeningStatus:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      res.status(500).json({
        error: "Error al actualizar el estado de screening",
        details: errorMessage,
      });
    }
  };

  // ...código existente...

  static getPapersByLabels = async (req: Request, res: Response) => {
    try {
      // labels puede venir como string (un solo label) o array (varios labels)
      let { labels } = req.query;

      if (!labels) {
        return res
          .status(400)
          .json({ error: "Debes especificar al menos un label" });
      }

      // Si es string, convertir a array
      if (typeof labels === "string") {
        labels = [labels];
      }

      // Buscar papers que contengan TODOS los labels indicados
      const papers = await Paper.find({ labels: { $all: labels } });

      res.json({ papers, filter: labels, total: papers.length });
    } catch (error) {
      console.error("Error in getPapersByLabels:", error);
      res.status(500).json({ error: "Error al filtrar por labels" });
    }
  };
}

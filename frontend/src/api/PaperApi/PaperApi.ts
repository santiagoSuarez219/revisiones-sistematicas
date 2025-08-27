import { isAxiosError } from "axios";
import api from "../../lib/axios";
import {
  GetAllPapersResponseSchema,
  ToLabelResponseSchema,
  type FilterStatusPapers,
  type GetAllPapersResponse,
} from "../../types";

export async function getPapers(status?: FilterStatusPapers) {
  try {
    // Construir URL con query parameters
    const params = new URLSearchParams();
    if (status && status !== "all") {
      params.append("status", status);
    }

    const queryString = params.toString();
    const url = queryString ? `/papers?${queryString}` : "/papers";
    console.log(url);

    const { data } = await api(url);

    // Si la respuesta incluye stats (nueva estructura), usar esa
    if (data.papers && data.stats) {
      return data as GetAllPapersResponse;
    }

    const response = GetAllPapersResponseSchema.safeParse(data);
    if (response.success) {
      return response.data;
    }
  } catch (error) {
    if (isAxiosError(error) && error.response) {
      throw new Error(error.response.data.error);
    }
  }
}

// Función específica para obtener solo estadísticas (útil para actualizar contadores)
export async function getPaperStats() {
  try {
    const { data } = await api("/papers/stats");
    return data;
  } catch (error) {
    if (isAxiosError(error) && error.response) {
      throw new Error(error.response.data.error);
    }
    throw new Error("Error al obtener estadísticas");
  }
}

export async function ToLabelPaper(paperId: string) {
  try {
    const { data } = await api.put(`/papers/${paperId}/label`);
    const response = ToLabelResponseSchema.safeParse(data);
    if (response.success) {
      return response.data;
    }
  } catch (error) {
    if (isAxiosError(error) && error.response) {
      throw new Error(error.response.data.error);
    }
  }
}

export async function updateScreeningStatus({
  paperId,
  screeningStatus,
}: {
  paperId: string;
  screeningStatus: string;
}) {
  try {
    const { data } = await api.put(`/papers/${paperId}/screening`, {
      screeningStatus,
    });
    const response = ToLabelResponseSchema.safeParse(data);
    if (response.success) {
      return response.data;
    }
  } catch (error) {
    if (isAxiosError(error) && error.response) {
      throw new Error(error.response.data.error);
    }
  }
}
